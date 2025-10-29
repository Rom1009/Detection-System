from __future__ import annotations
import pendulum
from airflow.sdk import dag
from airflow.providers.smtp.operators.smtp import EmailOperator
from airflow.providers.standard.operators.bash import BashOperator # Dùng BashOperator thay thế DockerOperator
from airflow.providers.docker.operators.docker import DockerOperator


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
    task_collect_data = DockerOperator(
        task_id="data_collection",
        
        image='ml_pipeline:latest', 

        # Nối hai lệnh bằng '&&'
        # Điều này đảm bảo 'dvc pull' chạy xong và thành công
        # trước khi 'dvc repro' bắt đầu.
        command='dvc pull && dvc repro', 

        working_dir='/app', 
        
        # Mounts vẫn giữ nguyên, rất quan trọng
        mounts=[
            '/home/dinhquy/Desktop/Code/AI/Detection-System:/app' 
        ],
        
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge" 
    )

    # == TASK 2: KIỂM TRA IMAGE DRIFT (ẢNH THÔ) ==
    task_check_image_drift = BashOperator(
        task_id="check_image_drift",
        bash_command="python -m backend.src.ml_pipeline.evaluation.check_image_drift \
                    --mode check \
                    --data-dir data/raw_cleaned \
                    --reference-csv data/reference/reference_image_metadata.csv",
        cwd="/app",
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
    task_collect_data >> task_check_image_drift >> task_send_label_request

# Kích hoạt DAG
data_ingestion_and_label_request_dag()