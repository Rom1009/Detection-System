from __future__ import annotations
import pendulum
from airflow.decorators import dag
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.email import EmailOperator
from docker.types import Mount

# --- CẤU HÌNH ---
# SỬA LẠI: Đường dẫn tuyệt đối đến thư mục gốc dự án của BẠN
PROJECT_ROOT_PATH = "/home/dinhquy/Desktop/Code/AI/Detection-System"
# SỬA LẠI: Đường dẫn đến cache DVC của BẠN
DVC_CACHE_PATH = "/home/dinhquy/.cache/dvc"
# SỬA LẠI: Email của bạn để nhận thông báo
YOUR_EMAIL = "quynguyencurit2002@gmail.com"



# Mounts (chia sẻ file) chung cho các container
common_mounts = [
    Mount(source=PROJECT_ROOT_PATH, target="/app", type="bind"),
    Mount(source=DVC_CACHE_PATH, target="/.cache/dvc", type="bind")
]

@dag(
    dag_id="dag_1_data_ingestion",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",  # Chạy hàng ngày
    catchup=False,
    tags=["ingestion", "drift-check", "labeling"],
)
def data_ingestion_and_label_request_dag():
    """
    DAG này chạy hàng ngày:
    1. Thu nạp dữ liệu mới từ Google Drive.
    2. Kiểm tra Image Drift (Distribution Drift) trên ảnh thô.
    3. Nếu OK, di chuyển file vào thư mục 'needs_labeling'.
    4. Gửi email yêu cầu gán nhãn.
    """
    
    # == TASK 1: THU NẠP DỮ LIỆU TỪ DRIVE ==
    task_collect_data = DockerOperator(
        task_id="data_collection",
        image="mlops_pipeline_image:latest",
        command="python -m src.ml_pipeline.data_pipeline.data_collection",
        mounts=common_mounts,
        working_dir="/app",
        auto_remove="success",
    )

    # == TASK 2: KIỂM TRA IMAGE DRIFT (ẢNH THÔ) ==
    task_check_image_drift = DockerOperator(
        task_id="check_image_drift",
        image="mlops_pipeline_image:latest",
        # Script này sẽ check ảnh trong 'data/raw_cleaned' (giả sử)
        # và so sánh với 'data/reference/reference_image_metadata.csv'
        command="python -m src.ml_pipeline.evaluation.check_image_drift \
                    --mode check \
                    --data-dir data/raw_cleaned \
                    --reference-csv data/reference/reference_image_metadata.csv",
        mounts=common_mounts,
        working_dir="/app",
        auto_remove="success",
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
        Pipeline đã chạy thành công `data_collection` và `check_image_drift`.
        <br>
        Không phát hiện Image Drift nghiêm trọng.
        <br><br>
        Vui lòng bắt đầu quá trình gán nhãn.
        </p>
        """,
    )

    # Định nghĩa luồng chạy:
    task_collect_data >> task_check_image_drift >> task_send_label_request

# Kích hoạt DAG
data_ingestion_and_label_request_dag()