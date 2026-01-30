from prometheus_client import Gauge

# Định nghĩa các chỉ số bạn muốn theo dõi trên Grafana
# Cấu trúc: Gauge('tên_metric_trong_prometheus', 'mô tả')

# 1. Đo độ lệch dữ liệu (Data Drift)
DATA_DRIFT_SCORE = Gauge('evidently_data_drift_score', 'Current Data Drift Score calculated by Evidently')

# 2. Đo độ chính xác model (Nếu có ground truth)
MODEL_ACCURACY_SCORE = Gauge('evidently_model_accuracy', 'Current Model Accuracy')

# 3. Đếm số lượng Model Drift (Số cột bị lệch)
DRIFTED_FEATURES_COUNT = Gauge('evidently_drifted_features_count', 'Number of features that have drifted')