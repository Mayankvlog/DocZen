from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from app.core.database import get_database
from app.core.security import verify_token
from app.schemas.file import FileResponse, FileUpload, JobResponse, JobCreate, ShareLinkCreate, ShareLinkResponse
from app.services.user_service import UserService
from app.services.file_service import FileService
from app.services.job_service import JobService
from app.models.user import User

router = APIRouter()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_database)
) -> User:
    """Get current authenticated user"""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Upload a file"""
    file_service = FileService(db)
    
    # Validate file
    if not file_service.is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed",
        )
    
    uploaded_file = await file_service.upload_file(file, current_user.id)
    return uploaded_file

@router.get("/files", response_model=List[FileResponse])
async def get_files(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    file_type: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user's files"""
    file_service = FileService(db)
    
    files = await file_service.get_user_files(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        file_type=file_type,
        is_favorite=is_favorite
    )
    
    return files

@router.get("/files/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get file details"""
    file_service = FileService(db)
    
    file = await file_service.get_file(file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    return file

@router.put("/files/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: str,
    file_update: dict,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update file metadata"""
    file_service = FileService(db)
    
    file = await file_service.update_file(file_id, current_user.id, file_update)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    return file

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete a file"""
    file_service = FileService(db)
    
    success = await file_service.delete_file(file_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    return {"message": "File deleted successfully"}

@router.post("/jobs", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new processing job"""
    job_service = JobService(db)
    
    job = await job_service.create_job(job_data, current_user.id)
    return job

@router.get("/jobs", response_model=List[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user's jobs"""
    job_service = JobService(db)
    
    jobs = await job_service.get_user_jobs(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return jobs

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get job details"""
    job_service = JobService(db)
    
    job = await job_service.get_job(job_id, current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    return job

@router.delete("/jobs/{job_id}")
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Cancel a job"""
    job_service = JobService(db)
    
    success = await job_service.cancel_job(job_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or cannot be cancelled",
        )
    
    return {"message": "Job cancelled successfully"}

@router.post("/files/{file_id}/share", response_model=ShareLinkResponse)
async def create_share_link(
    file_id: str,
    share_data: ShareLinkCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a share link for a file"""
    file_service = FileService(db)
    
    # Verify file ownership
    file = await file_service.get_file(file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    share_link = await file_service.create_share_link(share_data)
    return share_link

@router.get("/shared/{link_id}")
async def get_shared_file(
    link_id: str,
    password: Optional[str] = None,
    db = Depends(get_database)
):
    """Get shared file via link"""
    file_service = FileService(db)
    
    file = await file_service.get_shared_file(link_id, password)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared link not found or expired",
        )
    
    return file
