import torch
import torch.nn as nn

def calculate_metrics_multiclass(preds, labels, num_classes = 4, epsilon=1e-6):
    """
    Hàm tính Dice và IoU cho bài toán segmentation đa lớp.
    """
    # ======================================================================
    # BƯỚC QUAN TRỌNG NHẤT LÀ ĐÂY
    # Chuyển đổi shape từ [N, C, H, W] thành [N, H, W] để có thể so sánh
    pred_labels = torch.argmax(preds, dim=1)
    # ======================================================================
    
    dice_scores = []
    iou_scores = []
    
    # Lặp qua các lớp khuyết tật (bỏ qua lớp 0 là background)
    for c in range(1, num_classes):
        # Tạo mask nhị phân cho lớp hiện tại từ kết quả argmax
        pred_c = (pred_labels == c).float()
        
        # Tạo mask nhị phân cho lớp hiện tại từ ground truth
        label_c = (labels == c).float()
        
        # Bây giờ pred_c và label_c có shape giống nhau và có thể nhân với nhau
        if label_c.sum() == 0 and pred_c.sum() == 0:
            continue
            
        intersection = (pred_c * label_c).sum()
        union = pred_c.sum() + label_c.sum()
        
        dice = (2. * intersection + epsilon) / (union + epsilon)
        iou = (intersection + epsilon) / (union - intersection + epsilon)
        
        dice_scores.append(dice.item())
        iou_scores.append(iou.item())
        
    avg_dice = sum(dice_scores) / len(dice_scores) if dice_scores else 0.0
    avg_iou = sum(iou_scores) / len(iou_scores) if iou_scores else 0.0
    
    return avg_dice, avg_iou