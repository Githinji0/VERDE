import asyncio
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.models import WorkerJob


class JobQueue:
    """Async in-memory and database-backed priority job queue for background research workflows."""

    def __init__(self):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._active_jobs: Dict[str, Dict[str, Any]] = {}

    async def enqueue_job(
        self,
        job_type: str,
        payload: Dict[str, Any],
        priority: int = 50,
        session: Optional[AsyncSession] = None
    ) -> str:
        """Enqueues a new background job with given priority (lower number = higher priority)."""
        job_id = None
        if session:
            job = WorkerJob(
                job_type=job_type,
                priority=priority,
                status="QUEUED",
                payload=payload
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)
            job_id = job.id
        else:
            import uuid
            job_id = str(uuid.uuid4())

        await self._queue.put((priority, job_id, job_type, payload))
        return job_id

    async def dequeue_job(self) -> Tuple[int, str, str, Dict[str, Any]]:
        """Pulls the highest priority job from the queue."""
        return await self._queue.get()

    def get_queue_size(self) -> int:
        return self._queue.qsize()


job_queue = JobQueue()
