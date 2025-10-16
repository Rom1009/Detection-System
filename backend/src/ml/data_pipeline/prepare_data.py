import json
import datetime
from PIL import Image
from skimage import measure
import numpy as np
import os
from tqdm import tqdm


def create_coco_annotations(root_dir, output_file):
    """
    Quét qua thư mục dữ liệu và tạo file chú thích định dạng COCO.
    """

    # --- 1. Khởi tạo cấu trúc file COCO ---
    info = {
        "description": "Phone Defect Dataset",
        "url": "",
        "version": "1.0",
        "year": datetime.date.today().year,
        "contributor": "Your Name",
        "date_created": datetime.date.today().isoformat()
    }

    licenses = [{"url": "", "id": 0, "name": "License"}]

    # Định nghĩa các lớp lỗi. ID 0 thường dành cho background.
    categories = [
        {"id": 1, "name": "scratch", "supercategory": "defect"},
        {"id": 2, "name": "stain", "supercategory": "defect"},
        {"id": 3, "name": "oil", "supercategory": "defect"}
    ]
    
    # Tạo category mapping để dễ tra cứu
    category_map = {cat['name']: cat['id'] for cat in categories}

    coco_output = {
        "info": info,
        "licenses": licenses,
        "categories": categories,
        "images": [],
        "annotations": []
    }

    image_id_counter = 1
    annotation_id_counter = 1

    # # --- 2. Xử lý các thư mục chứa lỗi ---
    defect_folders = ["scratch", "stain", "oil"]
    ground_truth_folders = ["ground_truth_1", "ground_truth_2"]

    for category_name in defect_folders:
        category_id = category_map[category_name]
        image_folder = os.path.join(root_dir, category_name)
        
        if not os.path.isdir(image_folder):
            continue

        print(f"Processing folder: {category_name}")
        for image_filename in tqdm(os.listdir(image_folder)):
            image_path = os.path.join(image_folder, image_filename)
            
            # Đọc ảnh để lấy kích thước
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
            except IOError:
                print(f"Warning: Could not read image {image_path}. Skipping.")
                continue

            # Thêm thông tin ảnh vào danh sách
            image_info = {
                "id": image_id_counter,
                "file_name": os.path.join(category_name, image_filename),
                "width": width,
                "height": height
            }
            coco_output["images"].append(image_info)

            # Tìm mask tương ứng
            # Giả định tên mask có hậu tố '_mask.png'
            mask_filename = os.path.splitext(image_filename)[0] + '.png' 
            mask_path = None
            for gt_folder in ground_truth_folders:
                potential_path = os.path.join(root_dir, gt_folder, mask_filename)
                if os.path.exists(potential_path):
                    mask_path = potential_path
                    break
            
            if mask_path:
                # Chuyển mask thành polygon cho COCO
                mask_image = Image.open(mask_path).convert('L')
                mask_np = np.array(mask_image)
                
                # Tìm các đường viền trong mask (mỗi đường là một vùng lỗi)
                # 0.5 là ngưỡng để coi pixel là một phần của đối tượng
                contours = measure.find_contours(mask_np, 0.5)

                for contour in contours:
                    # Chuyển contour thành list [x1, y1, x2, y2, ...]
                    contour = np.flip(contour, axis=1) # Đảo (row, col) thành (x, y)
                    segmentation = contour.ravel().tolist()

                    # Chỉ thêm vào nếu polygon có ít nhất 3 điểm (6 tọa độ)
                    if len(segmentation) < 6:
                        continue

                    # Tính bounding box [x, y, width, height]
                    x_coords = contour[:, 0]
                    y_coords = contour[:, 1]
                    x_min, x_max = np.min(x_coords), np.max(x_coords)
                    y_min, y_max = np.min(y_coords), np.max(y_coords)
                    bbox = [int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)]

                    # Tính diện tích
                    area = (x_max - x_min) * (y_max - y_min)
                    
                    annotation_info = {
                        "id": annotation_id_counter,
                        "image_id": image_id_counter,
                        "category_id": category_id,
                        "segmentation": [segmentation], # COCO format yêu cầu list của các list
                        "area": float(area),
                        "bbox": bbox,
                        "iscrowd": 0
                    }
                    coco_output["annotations"].append(annotation_info)
                    annotation_id_counter += 1

            image_id_counter += 1

    # --- 3. Xử lý thư mục "good" (chỉ thêm thông tin ảnh, không có annotation) ---
    good_folder = os.path.join(root_dir, "good")
    if os.path.isdir(good_folder):
        print("Processing folder: good")
        for image_filename in tqdm(os.listdir(good_folder)):
            image_path = os.path.join(good_folder, image_filename)
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
            except IOError:
                print(f"Warning: Could not read image {image_path}. Skipping.")
                continue
            
            image_info = {
                "id": image_id_counter,
                "file_name": os.path.join("good", image_filename),
                "width": width,
                "height": height
            }
            coco_output["images"].append(image_info)
            image_id_counter += 1

    # --- 4. Lưu file JSON ---
    with open(output_file, 'w') as f:
        json.dump(coco_output, f, indent=4)
    
    print(f"\nSuccessfully created COCO annotation file at: {output_file}")