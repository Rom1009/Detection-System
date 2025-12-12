import pytest
from airflow.models import DagBag
import os

def test_dag_import_errors():
    """
    Test này sẽ thử load tất cả các file trong folder 'dags'.
    Nếu có bất kỳ lỗi cú pháp hay lỗi import nào, nó sẽ fail.
    """
    # Lấy đường dẫn tuyệt đối đến folder dags
    dag_folder = os.path.join(os.getcwd(), 'dags')
    
    print(f"Checking DAGs in: {dag_folder}")
    
    # Load DAGs
    dag_bag = DagBag(dag_folder=dag_folder, include_examples=False)
    
    # 1. Kiểm tra xem có lỗi import nào không (Quan trọng nhất)
    # Nếu bạn quên thêm thư viện vào requirements.txt, cái này sẽ bắt được.
    if dag_bag.import_errors:
        print("GẶP LỖI KHI IMPORT DAGs:")
        for filename, errors in dag_bag.import_errors.items():
            print(f"File: {filename} \nLỗi: {errors}")
            
    assert len(dag_bag.import_errors) == 0, f"Có {len(dag_bag.import_errors)} lỗi import DAG!"

    # 2. Kiểm tra xem có ít nhất 1 DAG được load không (tránh trường hợp trỏ sai folder)
    assert len(dag_bag.dags) > 0, "Không tìm thấy DAG nào cả!"