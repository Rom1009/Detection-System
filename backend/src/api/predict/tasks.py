from .service import PredictService
from core.celery_app import celery

service = PredictService()

@celery.task(name="predict.process_image")
def process_image_task(image_path: str):
    print(f"Worker is processing: {image_path}")
    return service.predict(image_path)