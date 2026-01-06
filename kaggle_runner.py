import os
import subprocess
import sys

# --- 1. SETUP HÀM RUN & TOKEN ---
def run(cmd):
    print(f"🚀 Running: {cmd}")
    # check_call sẽ tự ném lỗi nếu lệnh thất bại, giúp nhảy vào except
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing: {cmd}")
        raise e # Ném lỗi ra ngoài để khối try...except bắt được

# Lấy Token an toàn
DAGSHUB_TOKEN = ""
try:
    if len(sys.argv) > 1:
        DAGSHUB_TOKEN = sys.argv[1]
        print("✅ Received Token from arguments.")
    else:
        # Fallback nếu test trên máy local có biến môi trường
        DAGSHUB_TOKEN = os.getenv("DAGSHUB_TOKEN")
        if not DAGSHUB_TOKEN:
             raise Exception("Missing DAGSHUB_TOKEN")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# --- 2. BẮT ĐẦU PIPELINE (CÓ BẢO HỘ TRY...FINALLY) ---
try:
    print("=== KAGGLE PIPELINE STARTED ===")

    # A. Cài đặt thư viện
    print("📦 Installing dependencies...")
    run("pip install dvc mlflow dagshub")
    run("pip install -r backend/requirements.txt")

    # B. Cấu hình DAGsHub Auth
    print("🔐 Configuring Auth...")
    run("dvc remote modify origin --local auth basic")
    run("dvc remote modify origin --local user token") 
    # Lưu ý: Dùng user là 'token' thay vì tên đăng nhập để tránh lỗi với token
    run(f"dvc remote modify origin --local password {DAGSHUB_TOKEN}")

    # C. Pull Data
    print("⬇️ Pulling Data...")
    run("dvc pull")

    # D. Training
    print("🔥 Training & Logging...")
    os.environ["MLFLOW_TRACKING_URI"] = "https://dagshub.com/japanesegirl2002/Detection-System.mlflow"
    os.environ["MLFLOW_TRACKING_USERNAME"] = "japanesegirl2002"
    os.environ["MLFLOW_TRACKING_PASSWORD"] = DAGSHUB_TOKEN

    # Chạy quy trình train (Ép chạy lại với -f)
    run("dvc repro")

except Exception as e:
    print(f"\n❌ PIPELINE FAILED WITH ERROR: {e}")
    # Không exit ngay, để nó chạy xuống finally dọn dẹp đã
    # Biến này để đánh dấu là có lỗi
    os.environ["PIPELINE_STATUS"] = "FAILED"

finally:
    # --- 3. DỌN DẸP (LUÔN CHẠY DÙ SỐNG HAY CHẾT) ---
    print("\n🧹 AGGRESSIVE CLEANUP (To fix GitHub Action hanging)...")
    
    try:
        # Quay về thư mục gốc của Kaggle
        os.chdir("/kaggle/working")
        
        # Xóa thư mục code
        if os.path.exists("Detection-System"):
            subprocess.call("rm -rf Detection-System", shell=True)
            
        # QUAN TRỌNG: Xóa sạch các file ẩn (.dvc, .cache, .git)
        # Đây là thủ phạm chính khiến Kaggle đóng gói lâu
        subprocess.call("rm -rf .cache", shell=True)
        subprocess.call("rm -rf .dvc", shell=True)
        subprocess.call("rm -rf .git", shell=True)
        subprocess.call("rm -rf ./*", shell=True) # Xóa nốt những gì còn sót lại

        print("✅ STORAGE CLEARED. KAGGLE SHOULD STOP NOW.")
        
    except Exception as cleanup_error:
        print(f"⚠️ Cleanup warning: {cleanup_error}")

    # Nếu nãy có lỗi thì giờ mới báo exit để GitHub hiện đỏ
    if os.environ.get("PIPELINE_STATUS") == "FAILED":
        sys.exit(1)