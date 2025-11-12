from __future__ import annotations

import pendulum
from airflow.decorators import dag
from airflow.providers.smtp.operators.smtp import EmailOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

from src.ml_pipeline.data_pipeline.data_collection import main as data_collection

# --- CẤU HÌNH AIRFLOW & DỰ ÁN ---
YOUR_EMAIL = "quynguyencurit2002@gmail.com"

# Airflow sẽ chạy code từ thư mục working_dir=/app (đã được mount từ Host)

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
        python_callable =  data_collection,
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
    task_collect_data >> task_send_label_request

# Kích hoạt DAG
data_ingestion_and_label_request_dag()