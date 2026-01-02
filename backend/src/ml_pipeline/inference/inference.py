import torch
from pycocotools.coco import COCO
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2


def predict(model, image_path, device, num_classes):
    """
    Hàm dự đoán segmentation mask cho một ảnh duy nhất.
    
    Args:
        model: Model PyTorch đã được tải và ở chế độ eval().
        image_path (str): Đường dẫn tới file ảnh cần dự đoán.
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

    # 2. Đọc và xử lý ảnh
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    transformed = transform(image=image)
    image_tensor = transformed['image'].unsqueeze(0).to(device) # Thêm batch dimension và chuyển sang device

    # 3. Đưa ảnh qua model để dự đoán
    with torch.no_grad():
        outputs = model(image_tensor)['out']
    
    # 4. Xử lý kết quả đầu ra
    # Lấy lớp có xác suất cao nhất tại mỗi pixel
    predicted_mask = torch.argmax(outputs, dim=1).squeeze(0).cpu().numpy()
    
    return image, predicted_mask