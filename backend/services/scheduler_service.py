"""
Scheduler Service for Artha AI Cache Cleanup
Runs hourly cleanup jobs to remove expired data
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging
import asyncio
import os

from services.cache_service import cache_service

logger = logging.getLogger(__name__)

class SchedulerService:
    """
    Service for managing scheduled tasks
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.cleanup_interval_hours = int(os.getenv("CACHE_CLEANUP_INTERVAL_HOURS", "1"))
        self.is_running = False
    
    async def cleanup_expired_cache(self):
        """
        Scheduled task to clean up expired cache data
        """
        try:
            logger.info("🧹 Starting scheduled cache cleanup...")
            stats = cache_service.cleanup_expired_data()
            logger.info(f"✅ Cache cleanup completed: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Cache cleanup failed: {e}")
    
    async def health_check(self):
        """
        Scheduled health check for the caching system
        """
        try:
            from database.config import test_connection
            from utils.encryption import encryption
            
            # Test database connection
            db_healthy = test_connection()
            
            # Test encryption
            encryption_healthy = encryption.test_encryption()
            
            if db_healthy and encryption_healthy:
                logger.info("✅ Cache system health check passed")
            else:
                logger.warning(f"⚠️ Cache system health check issues: DB={db_healthy}, Encryption={encryption_healthy}")
                
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
    
    def start_scheduler(self):
        """
        Start the scheduler with all jobs
        """
        try:
            if self.is_running:
                logger.warning("Scheduler is already running")
                return
            
            # Add cleanup job (runs every hour)
            self.scheduler.add_job(
                self.cleanup_expired_cache,
                trigger=IntervalTrigger(hours=self.cleanup_interval_hours),
                id="cache_cleanup",
                name="Cache Cleanup Job",
                replace_existing=True,
                max_instances=1
            )
            
            # Add health check job (runs every 30 minutes)
            self.scheduler.add_job(
                self.health_check,
                trigger=IntervalTrigger(minutes=30),
                id="health_check",
                name="System Health Check",
                replace_existing=True,
                max_instances=1
            )
            
            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"✅ Scheduler started with cleanup interval: {self.cleanup_interval_hours} hours")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
    
    def stop_scheduler(self):
        """
        Stop the scheduler
        """
        try:
            if not self.is_running:
                logger.warning("Scheduler is not running")
                return
            
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("✅ Scheduler stopped")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop scheduler: {e}")
    
    def get_job_status(self) -> dict:
        """
        Get status of scheduled jobs
        """
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
            
            return {
                "scheduler_running": self.is_running,
                "jobs": jobs,
                "cleanup_interval_hours": self.cleanup_interval_hours
            }
            
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return {"error": str(e)}
    
    async def run_cleanup_now(self):
        """
        Manually trigger cache cleanup
        """
        try:
            logger.info("🧹 Manual cache cleanup triggered...")
            await self.cleanup_expired_cache()
            return True
        except Exception as e:
            logger.error(f"Manual cleanup failed: {e}")
            return False

# Global scheduler service instance
scheduler_service = SchedulerService()