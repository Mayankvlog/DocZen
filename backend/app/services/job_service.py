import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from app.models.job import Job
from app.schemas.file import JobCreate, JobUpdate
from app.core.redis import redis_client


class JobService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.jobs

    async def create_job(self, job_data: JobCreate, user_id: str) -> Job:
        """Create a new processing job"""
        job_id = str(uuid.uuid4())
        
        job_dict = job_data.dict()
        job_dict.update({
            "_id": str(uuid.uuid4()),
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "result": None,
            "error_message": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": None
        })
        
        job = Job(**job_dict)
        
        # Insert into database
        await self.collection.insert_one(job.to_dict())
        
        # Queue job for processing (in a real implementation, this would use Celery or similar)
        await self._queue_job(job_id)
        
        return job

    async def get_user_jobs(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[Job]:
        """Get user's jobs with filters"""
        query = {"user_id": user_id}
        
        if status:
            query["status"] = status
        
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        jobs_data = await cursor.to_list(length=limit)
        
        return [Job.from_dict(job_data) for job_data in jobs_data]

    async def get_job(self, job_id: str, user_id: str) -> Optional[Job]:
        """Get job by ID and user"""
        job_data = await self.collection.find_one({"job_id": job_id, "user_id": user_id})
        if job_data:
            return Job.from_dict(job_data)
        return None

    async def update_job(self, job_id: str, job_update: JobUpdate) -> Optional[Job]:
        """Update job status and progress"""
        update_data = {k: v for k, v in job_update.dict(exclude_unset=True).items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        if update_data.get("status") == "completed":
            update_data["completed_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"job_id": job_id},
            {"$set": update_data}
        )
        
        if result.modified_count:
            job_data = await self.collection.find_one({"job_id": job_id})
            return Job.from_dict(job_data)
        return None

    async def cancel_job(self, job_id: str, user_id: str) -> bool:
        """Cancel a job"""
        job = await self.get_job(job_id, user_id)
        if not job:
            return False
        
        if job.status not in ["pending", "processing"]:
            return False
        
        await self.update_job(job_id, JobUpdate(status="cancelled"))
        
        # Remove from queue if pending
        if job.status == "pending":
            await self._remove_from_queue(job_id)
        
        return True

    async def _queue_job(self, job_id: str) -> None:
        """Queue job for processing (mock implementation)"""
        # In a real implementation, this would use Celery or Redis queue
        await redis_client.lpush("job_queue", job_id)
        
        # Simulate job processing (remove in production)
        await self._simulate_job_processing(job_id)

    async def _remove_from_queue(self, job_id: str) -> None:
        """Remove job from queue"""
        # In a real implementation, this would remove from Celery/Redis queue
        await redis_client.delete(f"job:{job_id}")

    async def _simulate_job_processing(self, job_id: str) -> None:
        """Simulate job processing (for demo purposes - remove in production)"""
        import asyncio
        
        async def process():
            await asyncio.sleep(2)  # Simulate processing time
            
            # Update job to completed
            job_data = await self.collection.find_one({"job_id": job_id})
            if job_data:
                await self.update_job(job_id, JobUpdate(
                    status="completed",
                    progress=100,
                    result={"message": "Job completed successfully"}
                ))
        
        # Run in background (in production, this would be handled by Celery workers)
        asyncio.create_task(process())
