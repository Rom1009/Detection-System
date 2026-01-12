from fastapi import UploadFile
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2
from PIL import Image
import numpy as np
import io
import uuid
import torch.nn.functional as F
import mlflow
import os
from dotenv import load_dotenv
from mlflow.tracking import MlflowClient
import base64
import cv2
from .interface import IPredictService
from .model import PredictionResponse
from database.db import PredictionLog
from sqlmodel import Session
from database.file_storage import save_image_to_disk, save_mask_to_disk

load_dotenv()

class PredictService(IPredictService):
    
    _isinstance = None

    def __new__(cls):
        if cls._isinstance is None:
            print("Init AI Engine")
            cls._isinstance = super(PredictService, cls).__new__(cls)
            cls._isinstance.load_model_direct()
        return cls._isinstance
        
        
    def load_model_direct(self):
        self.model_version = "unknown"
        self.model_name = "DeepLabV3_Model_Registry"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"🔄 Đang kết nối MLflow để load model: {self.model_name}")
        
        # 1. Cấu hình URI
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
        
        try:
            # 2. Lấy thông tin version mới nhất (Để lưu vào biến self.model_version thôi)
            client = MlflowClient()
            # Tìm model ở giai đoạn Production hoặc Staging, hoặc bản mới nhất bất kỳ
            versions = client.get_latest_versions(self.model_name, stages=["None", "Production"])
            
            if not versions:
                raise Exception(f"Không tìm thấy model {self.model_name} trên DagsHub")
            
            # Lấy bản mới nhất
            latest_version = versions[0]
            self.model_version = latest_version.version
            print(f"🎯 Tìm thấy phiên bản: {self.model_version} (Stage: {latest_version.current_stage})")

            model_uri = f"models:/{self.model_name}/2"
            
            print(f"🚀 Đang load model từ URI: {model_uri}")
            
            # MLflow tự động tải về /tmp, tự cache, và load vào biến
            self.model = mlflow.pytorch.load_model(model_uri, map_location=self.device)
            
            self.model.to(self.device)
            self.model.eval()
            print("✅ Model đã load thành công!")
            
        except Exception as e:
            print(f"❌ Lỗi khi load model: {e}")
            # Tùy chọn: Raise lỗi để server dừng lại luôn nếu không có model
            raise e

    def inference(self, image, device):
        transform = A.Compose([
            A.Resize(256, 256),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2(),
        ])

        transformed = transform(image=image)
        image_tensor = transformed['image'].unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = self.model(image_tensor)['out']
        
        probs = F.softmax(outputs, dim=1) 
        conf_values, predicted_mask = torch.max(probs, dim=1)
        
        # Chuyển về CPU/Numpy
        predicted_mask = predicted_mask.squeeze(0).cpu().numpy().astype(np.uint8)
        confidence_map = conf_values.squeeze(0).cpu().numpy()
        
        return image, predicted_mask, confidence_map
    
    # Hàm phụ trợ để nén mask thành base64 (Fix lỗi performance)
    def mask_to_base64(self, mask):
        # Nhân 50 để mask nhìn rõ hơn (class 1->50, 2->100...)
        _, buffer = cv2.imencode('.png', mask * 50) 
        return base64.b64encode(buffer).decode('utf-8')

    async def predict(self, file: UploadFile, session: Session) -> PredictionResponse:
        label_map = { 0: "scratch", 1: "stain", 2: "oil" }
        
        if self.model is None:
            return {"error": "Model chưa sẵn sàng"}

        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("RGB")
        image_np = np.array(image)
        
        _, predicted_mask, confidence_map = self.inference(image_np, self.device)
        
        # Logic tính toán label (Giữ nguyên logic của bạn)
        unique, counts = np.unique(predicted_mask, return_counts=True)
        mask_bg = unique != 0
        unique_obj = unique[mask_bg]
        counts_obj = counts[mask_bg]

        label_name = "no defect detected"
        if len(unique_obj) > 0:
            class_id = int(unique_obj[np.argmax(counts_obj)])
            label_name = label_map.get(class_id - 1, "unknown") 
            
        image_path = save_image_to_disk(image)
        mask_path = save_mask_to_disk(predicted_mask)
        
        log_entry = PredictionLog(
            input_image_path=image_path,
            output_mask_path=mask_path,
            model_version=self.model_version,
            detected_label=label_name,
            confidence_score=float(np.mean(confidence_map)),
        )
        
        session.add(log_entry)
        session.commit()
        session.refresh(log_entry)
        
        return {
            "id": str(uuid.uuid4()),
            "label": label_name,
            # QUAN TRỌNG: Đổi tolist() thành base64 để không sập server
            "mask": self.mask_to_base64(predicted_mask), 
            "confidence": float(np.mean(confidence_map)),
            "model_version": self.model_version
        }