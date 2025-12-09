"""Celery application configuration"""

from celery import Celery
from celery.signals import task_failure, task_prerun, task_postrun, task_retry

from app.config import get_settings
from app.logger import error as log_error, info, warning

settings = get_settings()

# Initialize Celery app
celery_app = Celery(
    "transkeep",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.extract_pdf",
        "app.tasks.translate_blocks",
        "app.tasks.orchestrator",
    ],
)

# Configure Celery
celery_app.conf.update(
    # Task execution settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task timeouts
    task_soft_time_limit=600,  # 10 minutes soft limit
    task_time_limit=720,  # 12 minutes hard limit
    
    # Retry settings
    task_acks_late=True,  # Acknowledge tasks after execution
    task_reject_on_worker_lost=True,  # Reject tasks if worker dies
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Fetch one task at a time for long-running tasks
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (prevent memory leaks)
    worker_disable_rate_limits=False,
    
    # Monitoring
    task_track_started=True,  # Track when tasks start
    task_send_sent_event=True,  # Send task-sent events
    
    # Broker settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
)

# Task routes (optional - for multiple queues)
celery_app.conf.task_routes = {
    "app.tasks.extract_pdf.*": {"queue": "extraction"},
    "app.tasks.translate_blocks.*": {"queue": "translation"},
    "app.tasks.orchestrator.*": {"queue": "default"},
}


# Celery signals for logging and monitoring

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Log when a task starts"""
    info(
        "Task starting",
        task_name=task.name,
        task_id=task_id,
        args=str(args)[:100],  # Truncate long args
    )


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **extra):
    """Log when a task completes"""
    info(
        "Task completed",
        task_name=task.name,
        task_id=task_id,
        state=state,
    )


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **extra):
    """Log task failures"""
    log_error(
        "Task failed",
        task_name=sender.name,
        task_id=task_id,
        exc=exception,
        args=str(args)[:100],
    )


@task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, einfo=None, **extra):
    """Log task retries"""
    warning(
        "Task retrying",
        task_name=sender.name,
        task_id=task_id,
        reason=str(reason),
    )


# Health check task
@celery_app.task(name="health_check")
def health_check():
    """Simple health check task for monitoring"""
    return {"status": "healthy", "message": "Celery worker is running"}
