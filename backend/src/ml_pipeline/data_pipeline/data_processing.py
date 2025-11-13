import json
import yaml
import argparse
from pycocotools.coco import COCO

def train_valid_split(X, test_size = 0.2):
    test_size = int(len(X) * test_size)
    X_train = X[:-test_size]
    X_valid = X[-test_size:]
    return X_train, X_valid 

def split_data(params_path):
    """
    Đọc file COCO, chia ID ảnh thành tập train và valid,
    và lưu lại thành các file JSON.
    """
    with open(params_path) as f:
        params = yaml.safe_load(f)

    # Đường dẫn và tham số từ params.yaml
    annotation_file = params['path']['annotation_path']
    test_size = params['train_valid']['test_size']
    random_state = params['train_valid']['random_state']
    train_output = params['train_valid']['train_output']
    valid_output = params['train_valid']['valid_output']

    # Tải toàn bộ ID ảnh
    coco = COCO(annotation_file)
    all_image_ids = list(sorted(coco.imgs.keys()))

    # Chia danh sách ID
    train_ids, valid_ids = train_valid_split(
        all_image_ids, 
        test_size=test_size, 
    )

    # Lưu kết quả ra file
    with open(train_output, 'w') as f:
        json.dump(train_ids, f)
    
    with open(valid_output, 'w') as f:
        json.dump(valid_ids, f)

    print(f"Data split complete. Train IDs saved to {train_output}, Valid IDs saved to {valid_output}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", default="params.yaml")
    args = parser.parse_args()
    split_data(args.params)