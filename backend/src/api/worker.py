# worker.py
from src.api.core.celery_app import celery # Lấy cái neo ra
from src.api.auth.module import AuthModule
from src.api.predict.module import PredictModule

# 1. Khai báo Modules
modules = [
    AuthModule(), 
    PredictModule()
]

# 2. Lọc danh sách file tasks
task_modules_list = [m.task_module for m in modules if getattr(m, 'task_module', None)]

# 3. Nạp tasks vào Celery App
# Lúc này Celery mới thực sự biết tasks nằm ở đâu
if task_modules_list:
    print(f"🔄 Loading tasks from: {task_modules_list}")
    celery.autodiscover_tasks(packages=task_modules_list, force=True)