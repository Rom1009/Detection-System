import torchvision.models.segmentation as models
import torch

model = models.deeplabv3_resnet50(pretrained=True)

model.classifier[4] = torch.nn.Conv2d(256, 4,  kernel_size=(1, 1), stride=(1, 1))