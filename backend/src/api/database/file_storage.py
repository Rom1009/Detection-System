import os
import uuid
from PIL import Image
from datetime import datetime

# Folder lưu trữ (Map với Volume Docker)
UPLOAD_DIR = "src/api/data/images"
MASK_DIR = "src/api/data/masks"

# Tạo folder nếu chưa có
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MASK_DIR, exist_ok=True)

def save_image_to_disk(image: Image.Image, prefix="img") -> str:
    """Lưu ảnh PIL xuống ổ cứng và trả về đường dẫn"""
    
    # Tạo tên file theo ngày để dễ quản lý: 2024-01-12/uuid.jpg
    today = datetime.now().strftime("%Y-%m-%d")
    save_path = os.path.join(UPLOAD_DIR, today)
    os.makedirs(save_path, exist_ok=True)
    
    filename = f"{prefix}_{uuid.uuid4()}.jpg"
    full_path = os.path.join(save_path, filename)
    
    # Lưu ảnh
    image.save(full_path, quality=95)
    
    return full_path

def save_mask_to_disk(mask_array, prefix="mask") -> str:
    """Lưu Mask (Numpy) xuống ổ cứng"""
    image = Image.fromarray(mask_array * 50) # Nhân 50 để nhìn thấy được (nếu class nhỏ)
    
    today = datetime.now().strftime("%Y-%m-%d")
    save_path = os.path.join(MASK_DIR, today)
    os.makedirs(save_path, exist_ok=True)
    
    filename = f"{prefix}_{uuid.uuid4()}.png"
    full_path = os.path.join(save_path, filename)
    
    image.save(full_path)
    return full_path