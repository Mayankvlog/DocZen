from flask import Flask, request, jsonify
from celery import Celery
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from app.core.config import settings
from app.services.pdf_service import PDFService
from app.services.conversion_service import ConversionService
from app.services.ocr_service import OCRService

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = settings.MAX_FILE_SIZE

# Celery configuration
celery = Celery(
    'doczen_worker',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Initialize services
pdf_service = PDFService()
conversion_service = ConversionService()
ocr_service = OCRService()

@celery.task(bind=True)
def process_pdf_task(self, task_type: str, input_files: list, parameters: dict, job_id: str):
    """Process PDF tasks asynchronously"""
    try:
        # Update job status to processing
        update_job_status(job_id, "processing", 0)
        
        if task_type == "merge_pdf":
            result = pdf_service.merge_pdfs(input_files, parameters)
        elif task_type == "split_pdf":
            result = pdf_service.split_pdf(input_files[0], parameters)
        elif task_type == "compress_pdf":
            result = pdf_service.compress_pdf(input_files[0], parameters)
        elif task_type == "extract_pages":
            result = pdf_service.extract_pages(input_files[0], parameters)
        elif task_type == "remove_pages":
            result = pdf_service.remove_pages(input_files[0], parameters)
        elif task_type == "rotate_pages":
            result = pdf_service.rotate_pages(input_files[0], parameters)
        elif task_type == "add_watermark":
            result = pdf_service.add_watermark(input_files[0], parameters)
        elif task_type == "protect_pdf":
            result = pdf_service.protect_pdf(input_files[0], parameters)
        elif task_type == "remove_protection":
            result = pdf_service.remove_protection(input_files[0], parameters)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
        
        # Update job status to completed
        update_job_status(job_id, "completed", 100, result)
        return result
        
    except Exception as e:
        # Update job status to failed
        update_job_status(job_id, "failed", 0, error_message=str(e))
        raise

@celery.task(bind=True)
def convert_file_task(self, task_type: str, input_file: str, parameters: dict, job_id: str):
    """Convert files asynchronously"""
    try:
        # Update job status to processing
        update_job_status(job_id, "processing", 0)
        
        if task_type == "pdf_to_word":
            result = conversion_service.pdf_to_word(input_file, parameters)
        elif task_type == "word_to_pdf":
            result = conversion_service.word_to_pdf(input_file, parameters)
        elif task_type == "image_to_pdf":
            result = conversion_service.image_to_pdf(input_file, parameters)
        elif task_type == "pdf_to_image":
            result = conversion_service.pdf_to_image(input_file, parameters)
        else:
            raise ValueError(f"Unknown conversion type: {task_type}")
        
        # Update job status to completed
        update_job_status(job_id, "completed", 100, result)
        return result
        
    except Exception as e:
        # Update job status to failed
        update_job_status(job_id, "failed", 0, error_message=str(e))
        raise

@celery.task(bind=True)
def ocr_task(self, input_file: str, parameters: dict, job_id: str):
    """OCR processing asynchronously"""
    try:
        # Update job status to processing
        update_job_status(job_id, "processing", 0)
        
        result = ocr_service.process_ocr(input_file, parameters)
        
        # Update job status to completed
        update_job_status(job_id, "completed", 100, result)
        return result
        
    except Exception as e:
        # Update job status to failed
        update_job_status(job_id, "failed", 0, error_message=str(e))
        raise

def update_job_status(job_id: str, status: str, progress: int = 0, result: dict = None, error_message: str = None):
    """Update job status in database"""
    # This would update the job status in MongoDB
    # For now, we'll just log it
    print(f"Job {job_id} status: {status}, progress: {progress}%")
    
    if status == "completed" and result:
        print(f"Job {job_id} completed with result: {result}")
    elif status == "failed" and error_message:
        print(f"Job {job_id} failed with error: {error_message}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "doczen-worker",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/process', methods=['POST'])
def process_file():
    """Submit a processing task"""
    try:
        data = request.get_json()
        
        task_type = data.get('task_type')
        input_files = data.get('input_files', [])
        parameters = data.get('parameters', {})
        job_id = data.get('job_id')
        
        if not task_type or not job_id:
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Submit appropriate task based on type
        if task_type.startswith('pdf_') or task_type in ['merge_pdf', 'split_pdf', 'compress_pdf', 'extract_pages', 'remove_pages', 'rotate_pages', 'add_watermark', 'protect_pdf', 'remove_protection']:
            task = process_pdf_task.delay(task_type, input_files, parameters, job_id)
        elif task_type.startswith('convert_') or task_type in ['pdf_to_word', 'word_to_pdf', 'image_to_pdf', 'pdf_to_image']:
            task = convert_file_task.delay(task_type, input_files[0] if input_files else None, parameters, job_id)
        elif task_type == 'ocr_processing':
            task = ocr_task.delay(input_files[0] if input_files else None, parameters, job_id)
        else:
            return jsonify({"error": "Unknown task type"}), 400
        
        return jsonify({
            "task_id": task.id,
            "job_id": job_id,
            "status": "submitted"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id: str):
    """Get task status"""
    try:
        task = celery.AsyncResult(task_id)
        
        return jsonify({
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None,
            "error": str(task.info) if task.failed() else None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
