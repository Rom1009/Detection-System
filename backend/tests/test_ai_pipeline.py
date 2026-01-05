import pytest
from airflow.models import DagBag
from pathlib import Path
import os
import sys

# --- CẤU HÌNH ĐƯỜNG DẪN (CHỈ CẦN SỬA ĐOẠN NÀY) ---
def get_dag_folder():
    # 1. Lấy vị trí file test hiện tại: backend/tests/test_ai_pipeline.py
    current_test_dir = Path(__file__).resolve().parent
    
    # TRƯỜNG HỢP A: Nếu folder dags nằm ở GỐC dự án (ngang hàng backend)
    # path = current_test_dir.parent.parent / 'dags'
    
    # TRƯỜNG HỢP B: Nếu folder dags nằm trong backend/airflow/dags
    # path = current_test_dir.parent / 'airflow' / 'dags'

    # --> Mặc định mình để theo Trường hợp A (như cũ), bạn bỏ comment dòng tương ứng nhé:
    dag_path = current_test_dir.parent.parent / 'dags'
    
    return dag_path

def test_dag_import_errors():
    dag_folder = get_dag_folder()
    
    print(f"\nDEBUG: Đang tìm DAGs tại: {dag_folder}")
    
    # Kiểm tra folder có tồn tại không
    assert dag_folder.exists() and dag_folder.is_dir(), f"Lỗi: Không tìm thấy thư mục dags tại {dag_folder}"
    
    # Load DAGs
    dag_bag = DagBag(dag_folder=str(dag_folder), include_examples=False)
    
    # 1. In lỗi import ra cho dễ sửa
    if dag_bag.import_errors:
        print("\n!!! GẶP LỖI KHI IMPORT DAGs !!!")
        for filename, errors in dag_bag.import_errors.items():
            print(f"-"*30)
            print(f"File: {filename}")
            print(f"Lỗi: {errors}")
            
    # 2. Assertions
    assert len(dag_bag.import_errors) == 0, f"Có {len(dag_bag.import_errors)} lỗi import DAG!"
    assert len(dag_bag.dags) > 0, "Không tìm thấy bất kỳ DAG nào! (List DAG rỗng)"