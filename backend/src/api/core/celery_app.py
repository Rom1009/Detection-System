from celery import Celery 

celery = Celery(
    "backend_worker", 
    broker = "redis://127.0.0.1:6379/0",
    backend = "redis://127.0.0.1:6379/0"
)

celery.conf.update(
    task_track_started = True,
)