import torch.nn as nn
import torch

class conv_block(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(in_c, out_c, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_c),
            nn.ReLU(),
        )
        
        self.layer2 = nn.Sequential(
            nn.Conv2d(out_c, out_c, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_c),
            nn.ReLU(),
        )
        
    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        return x
    
    
class encoder(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()
        self.conv = conv_block(in_c, out_c)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        
    def forward(self, x):
        x = self.conv(x)
        p = self.pool(x)
        return x, p
    
class decoder(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()
        self.up = nn.ConvTranspose2d(in_c, out_c, kernel_size = 2, stride =2 , padding = 0)
        self.conv = conv_block(out_c + out_c , out_c)
        
    def forward(self, x, skip):
        x = self.up(x)
        x = torch.cat([x, skip], axis = 1)
        x = self.conv(x)
        return x
    
class UNET(nn.Module):
    def __init__(self):
        super().__init__()
        self.enc1 = encoder(3, 64)
        self.enc2 = encoder(64, 128)
        self.enc3 = encoder(128, 256)
        self.enc4 = encoder(256, 512)
        
        self.bottleneck = conv_block(512, 1024)
        
        self.dec1 = decoder(1024, 512)  
        self.dec2 = decoder(512, 256)
        self.dec3 = decoder(256, 128)
        self.dec4 = decoder(128, 64)
        
        self.outputs = nn.Conv2d(64, 4, kernel_size=1)
    
    def forward(self, x):
        s1, p1 = self.enc1(x)
        s2, p2 = self.enc2(p1)
        s3, p3 = self.enc3(p2)
        s4, p4 = self.enc4(p3)
        
        b = self.bottleneck(p4)
        
        d1 = self.dec1(b, s4)
        d2 = self.dec2(d1, s3)
        d3 = self.dec3(d2, s2)
        d4 = self.dec4(d3, s1)
        
        outputs = self.outputs(d4)
        return outputs