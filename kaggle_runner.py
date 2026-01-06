import os
import subprocess
import sys

# --- PHẦN THAY ĐỔI QUAN TRỌNG ---
# Lấy Token từ tham số dòng lệnh (sys.argv)
# sys.argv[0] là tên file, sys.argv[1] là tham số đầu tiên truyền vào
try:
    if len(sys.argv) > 1:
        DAGSHUB_TOKEN = sys.argv[1]
        print("✅ Received Token from arguments.")
    else:
        raise Exception("Missing DAGSHUB_TOKEN argument")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
# --------------------------------

def run(cmd):
    print(f"🚀 Running: {cmd}")
    if subprocess.call(cmd, shell=True) != 0:
        print(f"❌ Error: {cmd}")
        sys.exit(1)

print("=== KAGGLE PIPELINE STARTED ===")

# 1. Cài đặt thư viện
print("📦 Installing dependencies...")
run("pip install dvc mlflow dagshub")
run("pip install -r backend/requirements.txt")

# 2. Cấu hình DAGsHub Auth
print("🔐 Configuring Auth...")
run("dvc remote modify origin --local auth basic")
run("dvc remote modify origin --local user japanesegirl2002")
# Truyền biến DAGSHUB_TOKEN đã lấy ở trên vào lệnh
run(f"dvc remote modify origin --local password {DAGSHUB_TOKEN}")

# 3. Pull Data
print("⬇️ Pulling Data...")
run("dvc pull")

# 4. Training
print("🔥 Training & Logging...")
os.environ["MLFLOW_TRACKING_URI"] = "https://dagshub.com/japanesegirl2002/Detection-System.mlflow"
os.environ["MLFLOW_TRACKING_USERNAME"] = "japanesegirl2002"
os.environ["MLFLOW_TRACKING_PASSWORD"] = DAGSHUB_TOKEN

# Chạy quy trình train
run("dvc repro -f")

print("🧹 Cleaning up to speed up GitHub Action...")

# Xóa thư mục code (chứa cả data ảnh nặng)
# Nếu không xóa, GitHub Action sẽ cố tải cả ngàn tấm ảnh này về -> Treo máy
run("rm -rf Detection-System")

print("✅ DONE! Ready to finish.")