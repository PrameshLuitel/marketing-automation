"""
APScheduler job definitions for daily automated pipeline runs.
"""

import asyncio
import uuid
from datetime import datetime
from loguru import logger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


class PipelineScheduler:
    """Manages scheduled pipeline execution."""

    def __init__(self, timezone: str = "UTC"):
        self.scheduler = AsyncIOScheduler(timezone=timezone)
        self._pipeline_func = None

    def configure(self, pipeline_func, scrape_hour=2, analysis_hour=3, agents_hour=4, creative_hour=5):
        """
        Configure scheduled jobs.
        In practice, we run the full pipeline as one job since each stage
        depends on the previous one.
        """
        self._pipeline_func = pipeline_func

        # Main pipeline job — runs daily at scrape_hour
        self.scheduler.add_job(
            self._run_pipeline,
            CronTrigger(hour=scrape_hour, minute=0),
            id="daily_pipeline",
            name="Daily Marketing Pipeline",
            replace_existing=True,
            misfire_grace_time=3600,  # 1 hour grace
        )

        logger.info(
            f"Scheduler configured: Daily pipeline at {scrape_hour:02d}:00 UTC"
        )

    async def _run_pipeline(self):
        """Execute the full pipeline."""
        run_id = str(uuid.uuid4())[:8]
        logger.info(f"[Scheduler] Starting daily pipeline run: {run_id}")
        start = datetime.utcnow()

        try:
            if self._pipeline_func:
                await self._pipeline_func(run_id=run_id)
            logger.success(f"[Scheduler] Pipeline {run_id} completed")
        except Exception as e:
            logger.error(f"[Scheduler] Pipeline {run_id} failed: {e}")

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def get_jobs(self) -> list[dict]:
        """Get list of scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        return jobs
