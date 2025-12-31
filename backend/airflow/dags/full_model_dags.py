from __future__ import annotations
import sys
import os
import pendulum
from datetime import timedelta

from airflow import DAG
from airflow.providers.smtp.operators.smtp import EmailOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.standard.operators.python import ShortCircuitOperator
from airflow.providers.standard.sensors.filesystem import FileSensor # <--- Import mới
from docker.types import Mount
from airflow.providers.standard.operators.bash import BashOperator


# Setup đường dẫn
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

YOUR_EMAIL = "japanesegirl2002@gmail.com"
PROJECT_PATH = '/home/thomas/Desktop/AI/Detection-System'

shared_mount = Mount(
    source=PROJECT_PATH, 
    target='/app',     
    type='bind',
)

def check_if_data_updated(**context):
    logs = context["ti"].xcom_pull(task_ids = "data_collection", key='return_value')
    # Lưu ý: DockerOperator trả về log dưới dạng bytes hoặc string tùy config, cần convert cẩn thận
    if logs:
        # Convert bytes to string nếu cần
        log_str = logs.decode("utf-8") if isinstance(logs, bytes) else str(logs)
        if "STATUS: DATA_UPDATED" in log_str:
            print("Detected new data! Label it")
            return True
    print("No new data")
    return False

default_args = {
    'owner': 'airflow',
    'depends_on_past': False, 
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    # Tăng timeout lên để chờ người gán nhãn (ví dụ 7 ngày)
    'execution_timeout': timedelta(days=7) 
}

with DAG(
    dag_id="data_ingestion_and_label_request_dag_v2",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags = ["Production"],
    default_args=default_args # Nhớ truyền default_args vào đây
) as dag:
    
    collect_data = DockerOperator(
        task_id='data_collection',
        image='ml_pipeline:latest',
        api_version='auto',
        auto_remove="success",
        mount_tmp_dir=False,
        do_xcom_push=True,
        network_mode="bridge",
        command='python /app/ai/src/ml_pipline/data_pipeline/data_collection.py',
        environment={'RCLONE_CONFIG': '/etc/rclone.conf'},
        mounts=[
            Mount(
                source='/home/thomas/.config/r  clone/rclone.conf', 
                target='/etc/rclone.conf',     
                type='bind',
                read_only=True 
            ), 
            Mount(
                source='/home/thomas/Desktop/AI/Detection-System/backend/public/labelling', 
                target='/app/ai/public/labelling', # Check lại log lỗi cũ để lấy đúng đường dẫn đích
                type='bind'
            )
        ]
    )
    
    check_new_data = ShortCircuitOperator(
        task_id = "check_new_data",
        python_callable = check_if_data_updated,
    )
    
    task_send_label_request = EmailOperator(
        task_id="send_label_request_email",
        from_email="quynguyencurit2002@gmail.com",
        to=YOUR_EMAIL,
        subject="[Action Required] Cần gán nhãn dữ liệu & Tạo file DONE_LABELING",
        html_content=f"""
            <h3>⚠️ Dữ liệu mới đã về</h3>
            <p>1. Vui lòng truy cập tool để gán nhãn.</p>
            <p>2. Sau khi xong, hãy tạo một file rỗng tên là <b>DONE_LABELING</b> tại thư mục:</p>
            <code>{PROJECT_PATH}/DONE_LABELING</code>
            <p>Hệ thống sẽ tự động phát hiện file này và chạy training.</p>
        """,
    )
    
    # --- SỬA LOGIC Ở ĐÂY ---
    wait_for_manual_labeling = FileSensor(
        task_id="wait_for_human_signal",
        filepath=f"{PROJECT_PATH}/done_labeling", # Đường dẫn file cần kiểm tra
        poke_interval=600,       # Check mỗi 10 phút
        mode="reschedule",       # Giải phóng tài nguyên trong lúc chờ
        timeout=60 * 60 * 24 * 7 ,# Chờ tối đa 7 ngày,
        fs_conn_id="fs_default",  # Kết nối hệ thống file mặc định
    )
    
    # Hàm xóa file DONE_LABELING sau khi đã nhận tín hiệu (Clean up)
    # Dùng BashOperator cho nhanh gọn
    cleanup_signal_file = BashOperator(
        task_id="cleanup_signal_file",
        bash_command=f"rm -f {PROJECT_PATH}/done_labeling"
    )

    dvc_task = DockerOperator(
        task_id="dvc_pull_and_add",
        image="dvc_tools:latest",
        api_version="auto",
        auto_remove="success",
        network_mode="bridge",
        mount_tmp_dir=False,
        working_dir="/app",
        command='dvc pull',
        mounts=[shared_mount]
    )
        
    machine_learning_pipeline = DockerOperator(
        task_id = "machine_learning_pipeline", 
        api_version = "auto",
        image = "ml_pipeline:latest", 
        auto_remove = "success",
        mount_tmp_dir=False,
        network_mode="bridge",
        working_dir="/app",
        command = "dvc repro -f", 
        mounts=[shared_mount]
    )
    
    # Luồng chạy mới:
    # Sensor thấy file -> Xóa file -> Chạy DVC -> Training
    collect_data >> check_new_data >> task_send_label_request >> wait_for_manual_labeling >> cleanup_signal_file >> dvc_task >> machine_learning_pipeline