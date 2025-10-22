from pycocotools.coco import COCO
import albumentations as A
from albumentations.pytorch import ToTensorV2
from PIL import Image
import numpy as np
import os
from torch.utils.data import Dataset


def train_transform():
    train_transforms = A.Compose([
        A.Resize(height=512, width=512),
        A.HorizontalFlip(p=0.5),
        A.Rotate(limit=20, p=0.5),
        A.RandomBrightnessContrast(p=0.2),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])
    return train_transforms

def valid_transform():
    valid_transforms = A.Compose([
        A.Resize(height=512, width=512),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])
    return valid_transforms

class Img_Segmentation_Dataset(Dataset):
    def __init__(self, root_dir, annotation_file, transforms=None, image_ids=None): # Thêm image_ids
        self.root_dir = root_dir
        self.transforms = transforms
        
        self.coco = COCO(annotation_file)
        
        # Lọc ID nếu được cung cấp, nếu không thì lấy tất cả
        if image_ids:
            self.ids = image_ids
        else:
            self.ids = list(sorted(self.coco.imgs.keys()))
    
    def __len__(self):
        return len(self.ids)
    
    def __getitem__(self, idx):
        img_id = self.ids[idx]
        img_info = self.coco.loadImgs(img_id)[0]
        img_path = os.path.join(self.root_dir, img_info['file_name'])
        
        image = np.array(Image.open(img_path).convert("RGB"))
        
        ann_ids = self.coco.getAnnIds(imgIds=img_id)
        annotations = self.coco.loadAnns(ann_ids)
        
        mask = np.zeros((img_info["height"], img_info["width"]), dtype=np.uint8)
        
        for ann in annotations:
            category_id = ann["category_id"]
            single_ann_mask = self.coco.annToMask(ann)
            mask[single_ann_mask == 1] = category_id
            
        if self.transforms:
            augmented = self.transforms(image=image, mask=mask)
            image = augmented['image']
            mask = augmented['mask']
            
        return image, mask