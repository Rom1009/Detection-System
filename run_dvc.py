import subprocess
from dotenv import load_dotenv

# Nạp tất cả các biến từ .env vào môi trường hiện tại
load_dotenv()

# Chạy lệnh DVC
command = "dvc status"
subprocess.run(command, shell=True)