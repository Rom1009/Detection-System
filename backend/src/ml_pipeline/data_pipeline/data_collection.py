import subprocess
import sys 
import os


GDRIVE_REMOTE_NAME = "img_seg"

GDRIVE_SOURCE_PATH = "DVC/new_data"

LOCAL_LANDING_ZONE = "backend/public/labelling"

def data_collection():
    print(f"--- Start Data Collection from Google Drive")
    
    command = [
        "rclone", 
        "sync", 
        f"{GDRIVE_REMOTE_NAME}:{GDRIVE_SOURCE_PATH}",
        LOCAL_LANDING_ZONE,
        "--progress"
    ]
    
    try: 
        subprocess.run(command, check = True)
    
    except subprocess.CalledProcessError as e:
        print(f"Error when sync data: {e}", file = sys.stderr)
        sys.exit(1)
        
    except FileExistsError:
        print(f"Error: Not find 'rclone'", file = sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    data_collection()
