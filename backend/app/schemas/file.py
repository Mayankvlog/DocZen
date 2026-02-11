from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    TXT = "txt"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(str, Enum):
    MERGE_PDF = "merge_pdf"
    SPLIT_PDF = "split_pdf"
    COMPRESS_PDF = "compress_pdf"
    CONVERT_PDF_TO_WORD = "convert_pdf_to_word"
    CONVERT_WORD_TO_PDF = "convert_word_to_pdf"
    CONVERT_IMAGE_TO_PDF = "convert_image_to_pdf"
    CONVERT_PDF_TO_IMAGE = "convert_pdf_to_image"
    EXTRACT_PAGES = "extract_pages"
    REMOVE_PAGES = "remove_pages"
    ROTATE_PAGES = "rotate_pages"
    ADD_WATERMARK = "add_watermark"
    PROTECT_PDF = "protect_pdf"
    REMOVE_PROTECTION = "remove_protection"
    OCR_PROCESSING = "ocr_processing"

class FileBase(BaseModel):
    filename: str
    original_filename: str
    file_type: FileType
    file_size: int
    mime_type: str
    user_id: str
    is_favorite: bool = False
    tags: List[str] = []
    metadata: Optional[dict] = {}

class FileCreate(FileBase):
    pass

class FileUpdate(BaseModel):
    filename: Optional[str] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None

class FileResponse(FileBase):
    id: str
    file_path: str
    thumbnail_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    download_count: int = 0
    is_public: bool = False
    
    model_config = {"from_attributes": True}

class JobBase(BaseModel):
    job_type: JobType
    user_id: str
    input_files: List[str]
    parameters: Optional[dict] = {}
    priority: int = 1

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    progress: Optional[int] = None
    result: Optional[dict] = None
    error_message: Optional[str] = None

class JobResponse(JobBase):
    id: str
    job_id: str
    status: JobStatus
    progress: int = 0
    result: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class FileUpload(BaseModel):
    filename: str
    file_size: int
    mime_type: str
    chunk_size: int = 8192
    total_chunks: int

class ChunkUpload(BaseModel):
    upload_id: str
    chunk_index: int
    chunk_data: str  # Base64 encoded

class ShareLinkBase(BaseModel):
    file_id: str
    user_id: str
    expires_at: Optional[datetime] = None
    download_limit: Optional[int] = None
    password: Optional[str] = None

class ShareLinkCreate(ShareLinkBase):
    pass

class ShareLinkResponse(ShareLinkBase):
    id: str
    link_id: str
    download_count: int = 0
    is_active: bool = True
    created_at: datetime
    
    model_config = {"from_attributes": True}
