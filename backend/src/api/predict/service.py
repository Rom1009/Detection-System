from .interface import IPredictService
from fastapi import UploadFile
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2
from PIL import Image
import numpy as np
import io
import torchvision.models.segmentation as models
from .model import PredictionResponse
import uuid
import torch.nn.functional as F

NUM_CLASSES = 4

class PredictService(IPredictService):
    
    def inference(self, model, image, device):
        """
        Hàm dự đoán segmentation mask cho một ảnh duy nhất.
        
        Args:
            model: Model PyTorch đã được tải và ở chế độ eval().
            image (PIL.Image): Ảnh đầu vào.
            device: 'cuda' hoặc 'cpu'.
            num_classes (int): Số lượng lớp của bài toán.
            
        Returns:
            tuple: (original_image, predicted_mask)
                original_image là ảnh gốc (NumPy array)
                predicted_mask là mask dự đoán (NumPy array, 2D)
        """
        # 1. Định nghĩa các phép biến đổi - PHẢI GIỐNG HỆT validation transform
        transform = A.Compose([
            A.Resize(256, 256),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2(),
        ])

        transformed = transform(image=image)
        image_tensor = transformed['image'].unsqueeze(0).to(device) # Thêm batch dimension và chuyển sang device

        # 3. Đưa ảnh qua model để dự đoán
        with torch.no_grad():
            outputs = model(image_tensor)['out']
        
        probs = F.softmax(outputs, dim=1) 
        conf_values, predicted_mask = torch.max(probs, dim=1)
        
        predicted_mask = predicted_mask.squeeze(0).cpu().numpy()
        confidence_map = conf_values.squeeze(0).cpu().numpy()
        
        return image, predicted_mask, confidence_map
    
    async def predict(self, file: UploadFile) -> PredictionResponse:
        label = {
            0: "scratch",
            1: "stain",
            2: "oil"
        }
        
        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("RGB")
        image = np.array(image)
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = models.deeplabv3_resnet50(weights = None, num_classes=NUM_CLASSES)
        model.load_state_dict(torch.load('/home/dinhquy/Desktop/Code/AI/Detection-System/backend/model/model.pth', map_location=device), strict=False)
        model.to(device)
        
        model.eval()
        
        _, predicted_mask, confidence_map = self.inference(model, image, device)
        
        
        unique, counts = np.unique(predicted_mask, return_counts=True)

        mask = unique != 0
        unique = unique[mask]
        counts = counts[mask]

        if len(unique) == 0:
            return {
                "id": str(uuid.uuid4()),
                "label": str("no defect detected"),
                "mask": predicted_mask.tolist(),
                "confidence": np.mean(confidence_map),
                "model_version": "1.0.0"
            }

        class_id = int(unique[np.argmax(counts)])
        label_name = label.get(class_id - 1, "unknown")
        
        return {
            "id": str(uuid.uuid4()),
            "label": label_name,
            "mask": predicted_mask.tolist(),
            "confidence": np.mean(confidence_map),
            "model_version": "1.0.0"
        }

        
