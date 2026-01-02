import os
import sys
import cv2
import pandas as pd
import numpy as np
from evidently import Report
from evidently.presets import DataDriftPreset
import argparse    

def extract_img_data(dir_path):
    metadata = []
    print(f"Bắt đầu trích xuất metadata hình ảnh từ: {dir_path}")
    
    for filename in os.listdir(dir_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(dir_path, filename)
            try:
                image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if image is None: continue
                
                brightness = np.mean(image)
                contrast = np.std(image)
                height, width = image.shape
                
                metadata.append({
                    "filename": filename,
                    "brightness": brightness,
                    "contrast": contrast,
                    "height": height,
                    "width": width
                })
            except Exception as e:
                print(f"Lỗi xử lý file {filename}: {e}", file=sys.stderr)

    print(f"Hoàn tất trích xuất. Tổng cộng {len(metadata)} file.")
    return pd.DataFrame(metadata)

def run_drift_check(reference_df, current_df):
    """
    Sử dụng Evidently AI để so sánh hai DataFrame.
    """
    print("Bắt đầu chạy so sánh drift hình ảnh...")
    data_drift_report = Report(metrics=[DataDriftPreset()])
    data_drift_report.run(
        current_data=current_df, 
        reference_data=reference_df, 
        column_mapping=None
    )
    drift_results = data_drift_report.as_dict()
    is_drifted = drift_results['metrics'][0]['result']['dataset_drift']
    
    if is_drifted:
        print("CẢNH BÁO: Phát hiện IMAGE DRIFT!", file=sys.stderr)
        sys.exit(1) # Báo lỗi cho Airflow
    else:
        print("✅ THÀNH CÔNG: Không phát hiện Image Drift.")
        sys.exit(0) # Báo thành công

if __name__ == "__main__":
    # --- Định nghĩa Command-Line Arguments ---
    parser = argparse.ArgumentParser(description="Kiểm tra Image Drift")
    parser.add_argument('--mode', type=str, default='check', choices=['check', 'generate'],
                        help="Chế độ chạy: 'check' (mặc định) hoặc 'generate' (tạo file reference)")
    parser.add_argument('--data-dir', type=str, required=True,
                        help="Thư mục chứa ảnh (dữ liệu mới để 'check', hoặc dữ liệu chuẩn để 'generate')")
    parser.add_argument('--reference-csv', type=str, default='public/data/reference/reference_image_metadata.csv',
                        help="Đường dẫn đến file reference CSV (để đọc ở chế độ 'check')")
    parser.add_argument('--output-csv', type=str, default='public/data/reference/reference_image_metadata.csv',
                        help="Đường dẫn để LƯU file reference CSV (chỉ dùng ở chế độ 'generate')")
    
    args = parser.parse_args()

    # --- Chạy logic chính ---
    if args.mode == 'generate':
        print(f"--- Chế độ GENERATE: Tạo file reference từ {args.data_dir} ---")
        metadata_df = extract_img_data(args.data_dir)
        os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)
        metadata_df.to_csv(args.output_csv, index=False)
        print(f"✅ Đã lưu file reference mới tại: {args.output_csv}")
        sys.exit(0)

    elif args.mode == 'check':
        print(f"--- Chế độ CHECK: So sánh {args.data_dir} với {args.reference_csv} ---")
        if not os.path.exists(args.reference_csv):
            print(f"Lỗi: Không tìm thấy file reference {args.reference_csv}", file=sys.stderr)
            sys.exit(1)
            
        reference_df = pd.read_csv(args.reference_csv)
        current_df = extract_img_data(args.data_dir)
        
        if current_df.empty:
            print("Không tìm thấy ảnh mới để kiểm tra. Bỏ qua.")
            sys.exit(0)
            
        run_drift_check(reference_df, current_df)