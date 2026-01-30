from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid

# Bảng 1: Lưu lịch sử Inference
class PredictionLog(SQLModel, table=True):
    __tablename__ = "prediction_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Metadata về file (Chỉ lưu đường dẫn)
    input_image_path: str = Field(index=True)  # VD: /data/2026/01/11/img_abc.jpg
    output_mask_path: str                      # VD: /data/2026/01/11/mask_abc.png
    
    # Thông tin Model (Cực quan trọng cho MLOps)
    model_name: str = "DeepLabV3"
    model_version: str = Field(index=True)     # VD: "v1.2" (Lấy từ DagsHub/MLflow)
    
    # Kết quả dự đoán
    detected_label: str                        # VD: "oil", "scratch", "clean"
    confidence_score: float                    # VD: 0.95
    
    # Performance Monitoring
    inference_time_ms: float                   # VD: 120.5 (ms)
    
    # Thời gian
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Quan hệ với bảng Feedback
    feedback: Optional["UserFeedback"] = Relationship(back_populates="prediction")


# Bảng 2: Lưu Feedback của User (Ground Truth)
class UserFeedback(SQLModel, table=True):
    __tablename__ = "user_feedbacks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Liên kết với bảng PredictionLog
    prediction_id: uuid.UUID = Field(foreign_key="prediction_logs.id")
    
    # Feedback của user
    is_correct: bool = Field(default=False)    # True: Đúng, False: Sai
    actual_label: Optional[str] = None         # Nếu sai, thì nhãn đúng là gì?
    
    # Nếu user vẽ lại mask (Advanced feature)
    corrected_mask_path: Optional[str] = None  
    
    # Ghi chú thêm
    user_comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Quan hệ ngược lại
    prediction: Optional[PredictionLog] = Relationship(back_populates="feedback")