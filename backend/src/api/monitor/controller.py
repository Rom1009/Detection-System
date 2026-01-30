from fastapi import APIRouter
from .service import MonitorService
import pandas as pd
import numpy as np

monitor_service = MonitorService()

async def calculate_drift():
    # Giả lập dữ liệu hiện tại (Current Data)
    # Thực tế: Bạn query 100 dòng log gần nhất từ Database lên
    current_data = pd.DataFrame({
        'feature1': np.random.normal(0.5, 1, 100), # Lệch nhẹ so với ref
        'feature2': np.random.normal(5, 2, 100)
    })
    
    # Tính toán & Update Prometheus
    result = monitor_service.calculate_drift(current_data)
    
    return {"status": "success", "metrics": result}