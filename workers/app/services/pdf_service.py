import PyPDF2
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import io
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from app.core.config import settings

class PDFService:
    """Service for PDF processing operations"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def merge_pdfs(self, input_files: List[str], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple PDF files into one"""
        try:
            output_filename = f"merged_{uuid.uuid4()}.pdf"
            output_path = os.path.join(self.upload_dir, output_filename)
            
            merger = PyPDF2.PdfMerger()
            
            for file_path in input_files:
                if os.path.exists(file_path):
                    merger.append(file_path)
            
            merger.write(output_path)
            merger.close()
            
            return {
                "output_file": output_path,
                "filename": output_filename,
                "pages_merged": len(input_files),
                "file_size": os.path.getsize(output_path)
            }
            
        except Exception as e:
            raise Exception(f"Failed to merge PDFs: {str(e)}")
    
    def split_pdf(self, input_file: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Split PDF into multiple files"""
        try:
            split_type = parameters.get('split_type', 'page_range')
            output_files = []
            
            if split_type == 'page_range':
                page_ranges = parameters.get('page_ranges', [])
                
                for i, page_range in enumerate(page_ranges):
                    output_filename = f"split_{uuid.uuid4()}.pdf"
                    output_path = os.path.join(self.upload_dir, output_filename)
                    
                    reader = PyPDF2.PdfReader(input_file)
                    writer = PyPDF2.PdfWriter()
                    
                    start_page, end_page = page_range
                    for page_num in range(start_page, end_page + 1):
                        if page_num < len(reader.pages):
                            writer.add_page(reader.pages[page_num])
                    
                    with open(output_path, 'wb') as f:
                        writer.write(f)
                    
                    output_files.append({
                        "file": output_path,
                        "filename": output_filename,
                        "pages": end_page - start_page + 1
                    })
            
            elif split_type == 'single_pages':
                reader = PyPDF2.PdfReader(input_file)
                
                for i, page in enumerate(reader.pages):
                    output_filename = f"page_{i+1}_{uuid.uuid4()}.pdf"
                    output_path = os.path.join(self.upload_dir, output_filename)
                    
                    writer = PyPDF2.PdfWriter()
                    writer.add_page(page)
                    
                    with open(output_path, 'wb') as f:
                        writer.write(f)
                    
                    output_files.append({
                        "file": output_path,
                        "filename": output_filename,
                        "pages": 1
                    })
            
            return {
                "output_files": output_files,
                "total_files": len(output_files)
            }
            
        except Exception as e:
            raise Exception(f"Failed to split PDF: {str(e)}")
    
    def compress_pdf(self, input_file: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Compress PDF file"""
        try:
            compression_level = parameters.get('compression_level', 'medium')
            output_filename = f"compressed_{uuid.uuid4()}.pdf"
            output_path = os.path.join(self.upload_dir, output_filename)
            
            # Use PyMuPDF for compression
            doc = fitz.open(input_file)
            
            # Compression settings based on level
            if compression_level == 'low':
                quality = 90
                deflate = True
            elif compression_level == 'medium':
                quality = 70
                deflate = True
            else:  # high
                quality = 50
                deflate = True
            
            # Save with compression
            doc.save(
                output_path,
                garbage=4,
                deflate=deflate,
                clean=True,
                quality=quality
            )
            doc.close()
            
            original_size = os.path.getsize(input_file)
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            return {
                "output_file": output_path,
                "filename": output_filename,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": round(compression_ratio, 2)
            }
            
        except Exception as e:
            raise Exception(f"Failed to compress PDF: {str(e)}")
    
    def extract_pages(self, input_file: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Extract specific pages from PDF"""
        try:
            pages_to_extract = parameters.get('pages', [])
            output_filename = f"extracted_{uuid.uuid4()}.pdf"
            output_path = os.path.join(self.upload_dir, output_filename)
            
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()
            
            for page_num in pages_to_extract:
                if page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return {
                "output_file": output_path,
                "filename": output_filename,
                "pages_extracted": len(pages_to_extract),
                "file_size": os.path.getsize(output_path)
            }
            
        except Exception as e:
            raise Exception(f"Failed to extract pages: {str(e)}")
    
    def remove_pages(self, input_file: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Remove specific pages from PDF"""
        try:
            pages_to_remove = parameters.get('pages', [])
            output_filename = f"removed_{uuid.uuid4()}.pdf"
            output_path = os.path.join(self.upload_dir, output_filename)
            
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()
            
            for i, page in enumerate(reader.pages):
                if i not in pages_to_remove:
                    writer.add_page(page)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return {
                "output_file": output_path,
                "filename": output_filename,
                "pages_removed": len(pages_to_remove),
                "remaining_pages": len(reader.pages) - len(pages_to_remove),
                "file_size": os.path.getsize(output_path)
            }
            
        except Exception as e:
            raise Exception(f"Failed to remove pages: {str(e)}")
    
    def rotate_pages(self, input_file: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate pages in PDF"""
        try:
            rotation = parameters.get('rotation', 90)
            pages_to_rotate = parameters.get('pages', [])
            output_filename = f"rotated_{uuid.uuid4()}.pdf"
            output_path = os.path.join(self.upload_dir, output_filename)
            
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()
            
            for i, page in enumerate(reader.pages):
                if i in pages_to_rotate or not pages_to_rotate:
                    page.rotate(rotation)
                writer.add_page(page)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return {
                "output_file": output_path,
                "filename": output_filename,
                "rotation_degrees": rotation,
                "pages_rotated": len(pages_to_rotate) if pages_to_rotate else len(reader.pages),
                "file_size": os.path.getsize(output_path)
            }
            
        except Exception as e:
            raise Exception(f"Failed to rotate pages: {str(e)}")
    
    def add_watermark(self, input_file: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Add watermark to PDF"""
        try:
            watermark_text = parameters.get('text', 'Confidential')
            opacity = parameters.get('opacity', 0.3)
            position = parameters.get('position', 'center')
            output_filename = f"watermarked_{uuid.uuid4()}.pdf"
            output_path = os.path.join(self.upload_dir, output_filename)
            
            # Create watermark PDF
            watermark_pdf = self._create_watermark_pdf(watermark_text, opacity, position)
            
            # Add watermark to each page
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()
            
            watermark_page = PyPDF2.PdfReader(watermark_pdf).pages[0]
            
            for page in reader.pages:
                page.merge_page(watermark_page)
                writer.add_page(page)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            # Clean up watermark file
            os.remove(watermark_pdf)
            
            return {
                "output_file": output_path,
                "filename": output_filename,
                "watermark_text": watermark_text,
                "opacity": opacity,
                "file_size": os.path.getsize(output_path)
            }
            
        except Exception as e:
            raise Exception(f"Failed to add watermark: {str(e)}")
    
    def protect_pdf(self, input_file: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Add password protection to PDF"""
        try:
            password = parameters.get('password', '')
            output_filename = f"protected_{uuid.uuid4()}.pdf"
            output_path = os.path.join(self.upload_dir, output_filename)
            
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            writer.encrypt(password)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return {
                "output_file": output_path,
                "filename": output_filename,
                "is_protected": True,
                "file_size": os.path.getsize(output_path)
            }
            
        except Exception as e:
            raise Exception(f"Failed to protect PDF: {str(e)}")
    
    def remove_protection(self, input_file: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Remove password protection from PDF"""
        try:
            password = parameters.get('password', '')
            output_filename = f"unprotected_{uuid.uuid4()}.pdf"
            output_path = os.path.join(self.upload_dir, output_filename)
            
            reader = PyPDF2.PdfReader(input_file)
            if reader.is_encrypted:
                reader.decrypt(password)
            
            writer = PyPDF2.PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return {
                "output_file": output_path,
                "filename": output_filename,
                "protection_removed": True,
                "file_size": os.path.getsize(output_path)
            }
            
        except Exception as e:
            raise Exception(f"Failed to remove protection: {str(e)}")
    
    def _create_watermark_pdf(self, text: str, opacity: float, position: str) -> str:
        """Create a watermark PDF"""
        try:
            watermark_filename = f"watermark_{uuid.uuid4()}.pdf"
            watermark_path = os.path.join(self.upload_dir, watermark_filename)
            
            # Create a simple PDF with watermark text
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            c = canvas.Canvas(watermark_path, pagesize=letter)
            
            # Set transparency
            c.setFillAlpha(opacity)
            
            # Set font and size
            c.setFont("Helvetica-Bold", 48)
            
            # Calculate position
            page_width = letter[0]
            page_height = letter[1]
            
            if position == 'center':
                x = page_width / 2
                y = page_height / 2
            elif position == 'top':
                x = page_width / 2
                y = page_height - 100
            else:  # bottom
                x = page_width / 2
                y = 100
            
            # Draw text (rotated for diagonal watermark)
            c.saveState()
            c.translate(x, y)
            c.rotate(45)
            c.drawCentredText(0, 0, text)
            c.restoreState()
            
            c.save()
            
            return watermark_path
            
        except Exception as e:
            raise Exception(f"Failed to create watermark PDF: {str(e)}")
