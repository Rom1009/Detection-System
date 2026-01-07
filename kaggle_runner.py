import os
import subprocess
import sys
import shutil

# --- 1. SETUP TOKEN (QUAN TRỌNG) ---
# Đây là "Bến đỗ" để GitHub Actions tiêm token thật vào
# Khi chạy trên GitHub Actions, dòng này sẽ bị thay đổi thành Token thật
DAGSHUB_TOKEN = "DAGSHUB_TOKEN_PLACEHOLDER"

# Kiểm tra an toàn: Nếu vẫn là placeholder (tức là chạy local hoặc quên replace)
# thì fallback về biến môi trường để debug
if not DAGSHUB_TOKEN:
    print("❌ Lỗi: Không tìm thấy DAGSHUB_TOKEN!")
    sys.exit(1)

# --- 2. HÀM CHẠY LỆNH ---
def run(cmd):
    print(f"🚀 Running: {cmd}")
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError:
        print(f"❌ Error executing: {cmd}")
        sys.exit(1)

# --- 3. PIPELINE CHÍNH ---
try:
    print("=== KAGGLE PIPELINE STARTED ===")

    # Cleanup cũ
    if os.path.exists("Detection-System"):
        shutil.rmtree("Detection-System")

    # Clone & Setup
    run("git clone --branch dev https://github.com/Rom1009/Detection-System.git")
    os.chdir("Detection-System")

    print("📦 Installing dependencies...")
    run("pip install dvc mlflow dagshub")

    print("🔐 Configuring Auth...")
    # Dùng Token đã được tiêm vào
    run("dvc remote modify origin --local auth basic")
    run("dvc remote modify origin --local user japanesegirl2002")
    run(f"dvc remote modify origin --local password {DAGSHUB_TOKEN}")

    print("⬇️ Pulling Data...")
    run("dvc pull")

    print("🔥 Training...")
    os.environ["MLFLOW_TRACKING_URI"] = "https://dagshub.com/japanesegirl2002/Detection-System.mlflow"
    os.environ["MLFLOW_TRACKING_USERNAME"] = "japanesegirl2002"
    os.environ["MLFLOW_TRACKING_PASSWORD"] = DAGSHUB_TOKEN
    
    run("dvc repro -f")
    
    print("✅ SUCCESS")
    sys.exit(0)

except Exception as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)
finally:
    # Cleanup disk để tránh đầy bộ nhớ Kaggle
    os.chdir("/kaggle/working")
    run("sync")