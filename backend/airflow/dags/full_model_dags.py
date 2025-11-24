from __future__ import annotations
import sys
import os
import pendulum

# --- 1. SỬA IMPORT CHO ĐÚNG CHUẨN AIRFLOW 2.X ---
from airflow import DAG  # Dùng class DAG gốc
from airflow.providers.smtp.operators.smtp import EmailOperator
from airflow.providers.standard.operators.bash import BashOperator # Dùng BashOperator thay thế DockerOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.standard.operators.python import PythonOperator   # Import chuẩn
from airflow.utils.context import Context
from src.ml_pipeline.data_pipeline.data_collection import data_collection
from docker.types import Mount

# Setup đường dẫn (Giữ nguyên)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

YOUR_EMAIL = "quynguyencurit2002@gmail.com"

# --- 2. ĐƯA HÀM TEST RA NGOÀI CÙNG ---
def test_print_function(**context):
    run_date = context["ds"]

    print("--- BAT DAU TEST ---")
    print(f"Hello World! Ngay chay la: {run_date}")
    print("Kiem tra Log: Ham nay dang chay on dinh!")
    print("--- KET THUC TEST ---")

# --- 3. DÙNG 'WITH DAG' ĐỂ TỰ ĐỘNG GÁN DAG CHO OPERATOR ---
with DAG(
    dag_id="data_ingestion_and_label_request_dag",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["ingestion", "drift-check", "labeling"],
) as dag:
    
    # == TASK 1: CHẠY THỬ HELLO WORLD ==
    # Nhờ nằm trong khối 'with', task này tự hiểu nó thuộc về DAG trên
    
    collect_data = DockerOperator(
        task_id='data_collection',
        image='ml_pipeline:latest',
        api_version='auto',
        auto_remove="success",
        mount_tmp_dir=False,
        command='python /app/ai/src/ml_pipline/data_pipeline/data_collection.py',
        environment={
            'RCLONE_CONFIG': '/etc/rclone.conf'
        },
        mounts=[
            Mount(
                source='/home/thomas/.config/rclone/rclone.conf', 
                target='/etc/rclone.conf',     
                type='bind',
                read_only=True 
            )
        ]
    )
    

    # # == TASK 2: THÔNG BÁO ==
    # task_send_label_request = EmailOperator(
    #     task_id="send_label_request_email",
    #     to=YOUR_EMAIL,
    #     subject="[Airflow] Yêu cầu gán nhãn dữ liệu mới",
    #     html_content="""
    #     <h3>Test Log Success!</h3>
    #     <p>Pipeline đã chạy thành công.</p>
    #     """,
    # )
    
    # Định nghĩa luồng chạy
    collect_data