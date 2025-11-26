from __future__ import annotations
import sys
import os
import pendulum

# --- 1. SỬA IMPORT CHO ĐÚNG CHUẨN AIRFLOW 2.X ---
from airflow import DAG  # Dùng class DAG gốc
from airflow.providers.smtp.operators.smtp import EmailOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.standard.operators.python import ShortCircuitOperator, PythonOperator
from airflow.utils.context import Context
from src.ml_pipeline.data_pipeline.data_collection import data_collection
from docker.types import Mount
from airflow.exceptions import AirflowException

# Setup đường dẫn (Giữ nguyên)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

YOUR_EMAIL = "japanesegirl2002@gmail.com"

def check_if_data_updated(**context):
    logs = context["ti"].xcom_pull(task_ids = "data_collection", key='return_value')
    if logs and "STATUS: DATA_UPDATED" in logs:
        print("Detected new data! Label it")
        return True     
    else:
        print("No new data")
        return False

def stop_pipeline_for_approval():
    raise AirflowException(
        "✋ DỪNG LẠI CHỜ GÁN NHÃN!\n"
        "Vui lòng gán nhãn dữ liệu xong, quay lại đây bấm 'Mark as Success' để chạy tiếp bước DVC."
    )

# --- 3. DÙNG 'WITH DAG' ĐỂ TỰ ĐỘNG GÁN DAG CHO OPERATOR ---
with DAG(
    dag_id="data_ingestion_and_label_request_dag",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
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
        environment={
            'RCLONE_CONFIG': '/etc/rclone.conf'
        },
        mounts=[
            Mount(
                source='/home/dinhquy/.config/rclone/rclone.conf', 
                target='/etc/rclone.conf',     
                type='bind',
                read_only=True 
            ), 
            Mount(
                source='/home/dinhquy/Desktop/Code/AI/Detection-System/backend/public/labelling', 
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
        subject="[Action Required] Dữ liệu mới đã về - Cần gán nhãn ngay!",
        html_content="""
            <h3>⚠️ Phát hiện dữ liệu mới từ Google Drive</h3>
            <p>Hệ thống vừa tải dữ liệu mới về thành công.</p>
            <p><b>Hành động:</b> Vui lòng truy cập công cụ gán nhãn và xử lý ngay.</p>
            <p><i>Thư mục: /app/ai/public/labelling</i></p>
        """,
    )
    
    wait_for_manual_labeling = PythonOperator(
        task_id = "wait_for_manual_labeling",
        python_callable = stop_pipeline_for_approval,
        trigger_rule="all_success",
        do_xcom_push=False
    )
    
    # dvc_task = DockerOperator(
    #     task_id = "dvc pull and dvc add",
    #     api_version = "auto",
    #     image = "dvc_tools:latest",
    #     auto_remove = "success",
    #     mount_tmp_dir=False,
    #     network_mode="bridge",
    #     command = "dvc pull && dvc add . && git add .", 
    #     mounts=[
    #         Mount(
    #             source='/home/dinhquy/Desktop/Code/AI/Detection-System/.git', 
    #             target='/etc/rclone.conf',     
    #             type='bind',
    #             read_only=True 
    #         ), 
    #         Mount(
    #             source='/home/dinhquy/Desktop/Code/AI/Detection-System/.dvc', 
    #             target='/etc/rclone.conf',     
    #             type='bind',
    #             read_only=True 
    #         ), 
    #     ]
    # )
    
    
    # machine_learning_pipeline = DockerOperator(
    #     task_id = "machine learning pipeline", 
    #     api_version = "auto",
    #     image = "ml_pipeline:latest", 
    #     auto_remove = "success",
    #     mount_tmp_dir=False,
    #     network_mode="bridge",
    #     command = "dvc repro", 
    #     mounts=[
    #         Mount(
    #             source='/home/dinhquy/Desktop/Code/AI/Detection-System/.git', 
    #             target='/etc/rclone.conf',     
    #             type='bind',
    #             read_only=True 
    #         ), 
    #         Mount(
    #             source='/home/dinhquy/Desktop/Code/AI/Detection-System/.dvc', 
    #             target='/etc/rclone.conf',     
    #             type='bind',
    #             read_only=True 
    #         ), 
    #     ]
    # )
    
    # Định nghĩa luồng chạy
    collect_data >> check_new_data >> task_send_label_request >> wait_for_manual_labeling