import os
import subprocess
import sys
import time 


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
# --------------------------------

def run(cmd):
    print(f"🚀 Running: {cmd}")
    if subprocess.call(cmd, shell=True) != 0:
        print(f"❌ Error: {cmd}")
        sys.exit(1)

# 1. Cài đặt thư viện
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

    run("git clone --branch dev https://github.com/Rom1009/Detection-System.git")

    os.chdir("Detection-System")

    # A. Cài đặt thư viện
    print("📦 Installing dependencies...")
    run("pip install dvc mlflow dagshub")

    # B. Cấu hình DAGsHub Auth
    print("🔐 Configuring Auth...")
    run("dvc remote modify origin --local auth basic")
    run("dvc remote modify origin --local user japanesegirl2002") 
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

    run("dvc repro")

except Exception as e:
    print(f"\n❌ PIPELINE FAILED: {e}")
    os.environ["PIPELINE_STATUS"] = "FAILED"

finally:
    print("\n🧹 FINAL CLEANUP...")
    
    try:
        # 1. Xóa sạch dữ liệu (như cũ)
        if os.path.exists("/kaggle/working"):
            os.chdir("/kaggle/working")
            subprocess.call("rm -rf ./*", shell=True)
            subprocess.call("rm -rf ./.??*", shell=True) # Xóa file ẩn (.dvc, .git, .cache)
            
        # 2. CÂU THẦN CHÚ 1: Ép hệ điều hành ghi nhận việc xóa ngay lập tức
        # Giúp Kaggle nhận ra folder đã rỗng nhanh hơn
        subprocess.call("sync", shell=True)
        
        print("✅ CLEANUP DONE. EXITING NOW.")

    except Exception as cleanup_error:
        print(f"⚠️ Cleanup warning: {cleanup_error}")

    # 3. CÂU THẦN CHÚ 2: Kiểm tra trạng thái và thoát dứt khoát
    if os.environ.get("PIPELINE_STATUS") == "FAILED":
        print("❌ Exiting with failure code.")
        sys.exit(1) # Báo đỏ
    else:
        print("✅ Exiting with success code.")
        sys.exit(0) # Báo xanh (Bắt buộc phải có dòng này để Python thoát sạch sẽ)