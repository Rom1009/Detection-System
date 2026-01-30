import pandas as pd
import os
import cv2
import numpy as np
import json
import warnings
from evidently import Report
from evidently.presets import DataDriftPreset
from .metrics import DATA_DRIFT_SCORE, DRIFTED_FEATURES_COUNT

class MonitorService:
    def __init__(self):
        csv_path = "src/api/reference_data.csv"
        self.reference_data = None
        
        # Load Reference Data
        if os.path.exists(csv_path):
            try:
                self.reference_data = pd.read_csv(csv_path)
                # Lọc bỏ cột biến thiên bằng 0 để tránh lỗi chia cho 0
                nums = self.reference_data.select_dtypes(include=[np.number])
                self.reference_data = self.reference_data.loc[:, nums.std() > 0]
                print(f"✅ Loaded Reference Data. Shape: {self.reference_data.shape}")
            except Exception as e:
                print(f"❌ Error loading csv: {e}")
        else:
            print(f"❌ File not found: {csv_path}")

    def calculate_drift(self, image_numpy, mask_numpy=None):
        if self.reference_data is None or self.reference_data.empty:
            print("⚠️ Skipped: No reference data.")
            return

        # --- 1. TẮT CẢNH BÁO NUMPY (CHỈ TRONG HÀM NÀY) ---
        with warnings.catch_warnings():
            warnings.simplefilter("ignore") # Bỏ qua mọi warning tính toán
            
            try:
                # --- 2. TRÍCH XUẤT ĐẶC TRƯNG ---
                features = self.extract_image_features(image_numpy, mask_numpy)
                current_data = pd.DataFrame([features])
                
                # Chỉ lấy các cột chung (tránh lệch cột)
                common_cols = list(set(self.reference_data.columns) & set(current_data.columns))
                if not common_cols:
                    print("⚠️ No common columns found.")
                    return

                # --- 3. CHẠY REPORT ---
                report = Report(metrics=[DataDriftPreset()])
                my_eval = report.run(
                    current_data=current_data[common_cols],
                    reference_data=self.reference_data[common_cols]
                )
                
                # --- 4. LẤY KẾT QUẢ (TRY-EXCEPT ĐA NĂNG) ---
                results = {}
                try:
                    # Cách 1: Chuẩn mới (v0.4+)
                    results = my_eval.as_dict()
                except AttributeError:
                    try:
                        # Cách 2: Chuẩn cũ (v0.2 - v0.3)
                        json_str = my_eval.json()
                        results = json.loads(json_str)

                        my_eval.save_html("report_drift.html")
                    except AttributeError:
                        # Cách 3: Cùng đường
                        print(f"❌ Lỗi lạ: Object Report có các hàm sau: {dir(my_eval)}")
                        return

                # --- 5. UPDATE PROMETHEUS ---
                # Parse kết quả (Cấu trúc JSON có thể thay đổi tùy version)
                try:
                    # Evidently trả về metrics dạng list, ta cần tìm đúng cái DataDrift
                    metrics = results['metrics'][0]['value']
                    drift_share = metrics['share']
                    drifted_count = metrics['count']
                    
                    DATA_DRIFT_SCORE.set(drift_share)
                    DRIFTED_FEATURES_COUNT.set(drifted_count)
                    
                    print(f"✅ Monitor Success! Drift Score: {drift_share}")
                except KeyError:
                    # Nếu cấu trúc JSON khác dự đoán (do version)
                    print("⚠️ JSON structure mismatch (Check version compatibility)")
                    print(results.keys())

            except Exception as e:
                print(f"❌ Monitor Crash: {e}")
                import traceback
                traceback.print_exc()

    def extract_image_features(self, image_numpy, mask_numpy=None):
        # (Giữ nguyên logic cũ của bạn)
        if len(image_numpy.shape) == 3:
            gray = cv2.cvtColor(image_numpy, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_numpy
            
        features = {}
        # Ép kiểu float để tránh lỗi JSON dump
        features['brightness'] = float(np.mean(gray))
        features['contrast'] = float(np.std(gray))
        features['sharpness'] = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        # Các cột mặc định
        features['mask_area_ratio'] = 0.0
        features['defect_count'] = 0
        features['category_id'] = 0
        
        if mask_numpy is not None:
             total_defect_area = np.sum(mask_numpy > 0)
             image_area = mask_numpy.shape[0] * mask_numpy.shape[1]
             if image_area > 0:
                features['mask_area_ratio'] = float(total_defect_area / image_area)
        
        return features