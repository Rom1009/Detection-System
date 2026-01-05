import torch
from tqdm import tqdm
import mlflow
import mlflow.pytorch
import torch.nn.functional as F
from backend.src.ml_pipeline.evaluation.evaluation import calculate_metrics_multiclass
from mlflow.models.signature import infer_signature
import os

# ... (Hàm train và validate giữ nguyên) ...

# ===================================================================
# HÀM TRAIN (Không thay đổi)
# ===================================================================
def train(train_data_loader, model, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    
    for images, masks in tqdm(train_data_loader, desc="Training"):
        images = images.to(device)
        masks = masks.to(device)
        
        optimizer.zero_grad()
        
        outputs = model(images)["out"]
        outputs = F.interpolate(outputs, size=masks.shape[-2:], mode='bilinear', align_corners=False)
        
        loss = criterion(outputs, masks.long())
        
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * images.size(0)
    
    epoch_loss = running_loss / len(train_data_loader.dataset)
    return epoch_loss

# ===================================================================
# HÀM VALIDATE (Không thay đổi)
# ===================================================================
def validate(valid_data_loader, model, criterion, device, num_classes):
    model.eval()
    running_loss = 0.0
    total_dice = 0
    total_iou = 0
    
    with torch.no_grad():
        for images, masks in tqdm(valid_data_loader, desc="Validating"):
            images = images.to(device)
            masks = masks.to(device)
            
            outputs = model(images)["out"]
            outputs = F.interpolate(outputs, size=masks.shape[-2:], mode='bilinear', align_corners=False)
            
            loss = criterion(outputs, masks.long())
            running_loss += loss.item() * images.size(0)
            
            dice, iou = calculate_metrics_multiclass(outputs, masks.long(), num_classes=num_classes)
            total_dice += dice
            total_iou += iou
            
    epoch_loss = running_loss / len(valid_data_loader.dataset)
    avg_dice = total_dice / len(valid_data_loader)
    avg_iou = total_iou / len(valid_data_loader)
    
    return epoch_loss, avg_dice, avg_iou

# ===================================================================
# HÀM RUN (Nâng cấp với lr_scheduler)
# ===================================================================
def run(train_data_loader, valid_data_loader, model, criterion, optimizer,
        lr_scheduler, device, num_epochs, num_classes, hparams): # ⭐ 1. Thêm lr_scheduler vào tham số
    
    REGISTRY_MODEL_NAME = "DeepLabV3_Model_Registry"
    
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
    
    mlflow.set_experiment("DeepLabV3_Experiment")
    
    with mlflow.start_run(run_name=hparams.get("run_name", "default_run")):
        
        print("MLflow Run started...")
        mlflow.log_params(hparams)
        
        best_iou = 0.0 
        
        for epoch in range(num_epochs):
            print(f"Epoch {epoch+1}/{num_epochs}")
            
            train_loss = train(train_data_loader, model, criterion, optimizer, device)
            
            valid_loss, valid_dice, valid_iou = validate(valid_data_loader, model, criterion, device, num_classes=num_classes)
            
            # ⭐ 2. Cập nhật learning rate SAU KHI validate
            # (Đối với StepLR, nó chỉ cập nhật sau 1 số epoch nhất định)
            lr_scheduler.step()

            # ⭐ 3. Log learning rate hiện tại để theo dõi
            current_lr = optimizer.param_groups[0]['lr']
            mlflow.log_metric("learning_rate", current_lr, step=epoch)

            # In thông tin đầy đủ
            print(f"  Train Loss: {train_loss:.4f}")
            print(f"  Valid Loss: {valid_loss:.4f} | Valid Dice: {valid_dice:.4f} | Valid IoU: {valid_iou:.4f}")
            print(f"  Current LR: {current_lr}") # In ra LR
            
            # Log các chỉ số (Metrics) theo từng epoch
            mlflow.log_metric("train_loss", train_loss, step=epoch)
            mlflow.log_metric("valid_loss", valid_loss, step=epoch)
            mlflow.log_metric("valid_dice", valid_dice, step=epoch)
            mlflow.log_metric("valid_iou", valid_iou, step=epoch)
            
            if valid_iou > best_iou:
                best_iou = valid_iou
                model_path = 'best_model.pth'
                torch.save(model.state_dict(), model_path)
                print(f"  🎉 New best model saved with IoU: {best_iou:.4f}")
                
        print("\nTraining complete. Processing best model for Registry...")
        mlflow.log_metric("best_valid_iou", best_iou)
        
        model.load_state_dict(torch.load('best_model.pth'))
        
        dummy_input, _ = next(iter(valid_data_loader))
        dummy_input = dummy_input.to(device)
        signature = infer_signature(dummy_input.cpu().numpy(), model(dummy_input).detach().cpu().numpy())
        
        
        model_info = mlflow.pytorch.log_model(
            pytorch_model=model,
            artifact_path="model",
            signature=signature,
            registered_model_name=REGISTRY_MODEL_NAME  # <--- ĐÂY LÀ CHÌA KHÓA
        )
        
        client = mlflow.tracking.MlflowClient()
        client.set_registered_model_alias(
            name=REGISTRY_MODEL_NAME, 
            alias="Candidate", 
            version=model_info.registered_model_version
        )
        
        print(f"✅ Model registered as '{REGISTRY_MODEL_NAME}' version {model_info.registered_model_version}")
        print(f"✅ Tagged as alias: 'Candidate'")

    return best_iou