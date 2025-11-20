from __future__ import annotations
import sys
import os

# Lấy đường dẫn tuyệt đối của thư mục gốc Airflow (/opt/airflow)
# __file__ là file hiện tại (full_model_dags.py)
# os.path.dirname(__file__) là thư mục /opt/airflow/dags
# os.path.abspath(os.path.join(..., "..")) là thư mục /opt/airflow
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Thêm thư mục gốc (/opt/airflow) vào đầu Python Path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pendulum
from airflow.sdk import dag
from airflow.providers.smtp.operators.smtp import EmailOperator
from airflow.providers.standard.operators.bash import BashOperator # Dùng BashOperator thay thế DockerOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.standard.operators.python import PythonOperator
from src.ml_pipeline.data_pipeline.data_collection import data_collection

YOUR_EMAIL = "quynguyencurit2002@gmail.com"

@dag(
    dag_id="data_ingestion_and_label_request_dag", # Đặt lại tên DAG ID cho rõ ràng
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",  # Chạy hàng ngày
    catchup=False,
    tags=["ingestion", "drift-check", "labeling"],
)
def data_ingestion_and_label_request_dag():
    """
    DAG này chạy các tác vụ ML/Data trực tiếp trong môi trường Airflow
    (sử dụng BashOperator để chạy các script Python).
    """
    
    # == TASK 1: THU NẠP DỮ LIỆU TỪ DRIVE ==
    # Sử dụng BashOperator để chạy module Python trong thư mục dự án (/app)
    task_collect_data = PythonOperator(
        task_id="data_collection",
        python_callable=data_collection,
        op_kwargs={'run_date': '{{ ds }}'},
    )

    # == TASK 3: THÔNG BÁO CHO CON NGƯỜI (HUMAN-IN-THE-LOOP) ==
    # Task này chỉ chạy nếu Task 1 và 2 thành công
    task_send_label_request = EmailOperator(
        task_id="send_label_request_email",
        to=YOUR_EMAIL,
        subject="[Airflow] Yêu cầu gán nhãn dữ liệu mới",
        html_content="""
        <h3>Đã phát hiện dữ liệu ảnh mới!</h3>
        <p>
        Pipeline đã chạy thành công data_collection và check_image_drift.
        <br><br>
        Vui lòng bắt đầu quá trình gán nhãn thủ công.
        </p>
        """,
    )
    
    # Định nghĩa luồng chạy:
    task_collect_data  >> task_send_label_request

# Kích hoạt DAG
data_ingestion_and_label_request_dag()