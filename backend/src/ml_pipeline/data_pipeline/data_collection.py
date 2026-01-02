import subprocess
import sys 
import os


GDRIVE_REMOTE_NAME = "img_seg"

GDRIVE_SOURCE_PATH = "DVC/new_data"

LOCAL_LANDING_ZONE = "/app/ai/public/labelling"

def data_collection():
    print(f"--- Start Data Collection from Google Drive")
    
    command = [
        "rclone", "sync", 
        f"{GDRIVE_REMOTE_NAME}:{GDRIVE_SOURCE_PATH}",
        LOCAL_LANDING_ZONE,
        "--progress",
        "--stats-one-line" # Thêm cái này để log ngắn gọn dễ check
    ]
    
    try: 
        # capture_output=True để bắt lấy dòng chữ mà rclone in ra
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        # In log ra màn hình để debug (vẫn hiện trên Airflow UI)
        print(result.stderr) 
        print(result.stdout)

        # LOGIC KIỂM TRA: Rclone thường ghi log vào stderr
        # Nếu KHÔNG thấy dòng "Transferred: 0 / 0" nghĩa là CÓ file mới
        if "Transferred: 0 / 0" not in result.stderr:
            print("STATUS: DATA_UPDATED") # <--- TÍN HIỆU QUAN TRỌNG
        else:
            print("STATUS: NO_CHANGE")

    except subprocess.CalledProcessError as e:
        print(f"Error when sync data: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    data_collection()