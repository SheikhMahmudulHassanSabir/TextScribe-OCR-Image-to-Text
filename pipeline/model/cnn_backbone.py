"""
7-block CNN backbone for feature extraction.
"""

import paddle
import paddle.nn as nn

class CNNBackbone(nn.Layer):
    """
    7-block CNN backbone that processes the preprocessed image.
    Input: [B, 1, 32, W]
    Output: [B, T, 512] where T = W/4
    """
    def __init__(self):
        super(CNNBackbone, self).__init__()
        
        # Block 1: Conv2D(1->64, 3x3) -> BN -> ReLU -> MaxPool(2x2)
        # Out shape: [B, 64, 16, W/2]
        self.block1 = nn.Sequential(
            nn.Conv2D(in_channels=1, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm2D(num_features=64),
            nn.ReLU(),
            nn.MaxPool2D(kernel_size=2, stride=2)
        )
        
        # Block 2: Conv2D(64->128, 3x3) -> BN -> ReLU -> MaxPool(2x2)
        # Out shape: [B, 128, 8, W/4]
        self.block2 = nn.Sequential(
            nn.Conv2D(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.BatchNorm2D(num_features=128),
            nn.ReLU(),
            nn.MaxPool2D(kernel_size=2, stride=2)
        )
        
        # Block 3: Conv2D(128->256, 3x3) -> BN -> ReLU
        # Out shape: [B, 256, 8, W/4]
        self.block3 = nn.Sequential(
            nn.Conv2D(in_channels=128, out_channels=256, kernel_size=3, padding=1),
            nn.BatchNorm2D(num_features=256),
            nn.ReLU()
        )
        
        # Block 4: Conv2D(256->256, 3x3) -> BN -> ReLU -> MaxPool(1x2)
        # Out shape: [B, 256, 4, W/4]
        self.block4 = nn.Sequential(
            nn.Conv2D(in_channels=256, out_channels=256, kernel_size=3, padding=1),
            nn.BatchNorm2D(num_features=256),
            nn.ReLU(),
            nn.MaxPool2D(kernel_size=[2, 1], stride=[2, 1])
        )
        
        # Block 5: Conv2D(256->512, 3x3) -> BN -> ReLU
        # Out shape: [B, 512, 4, W/4]
        self.block5 = nn.Sequential(
            nn.Conv2D(in_channels=256, out_channels=512, kernel_size=3, padding=1),
            nn.BatchNorm2D(num_features=512),
            nn.ReLU()
        )
        
        # Block 6: Conv2D(512->512, 3x3) -> BN -> ReLU -> MaxPool(1x2)
        # Out shape: [B, 512, 2, W/4]
        self.block6 = nn.Sequential(
            nn.Conv2D(in_channels=512, out_channels=512, kernel_size=3, padding=1),
            nn.BatchNorm2D(num_features=512),
            nn.ReLU(),
            nn.MaxPool2D(kernel_size=[2, 1], stride=[2, 1])
        )
        
        # Block 7: Conv2D(512->512, 2x2) -> BN -> ReLU
        # Using kernel=2, padding=0, stride=1
        # Out shape: [B, 512, 1, W/4]
        self.block7 = nn.Sequential(
            nn.Conv2D(in_channels=512, out_channels=512, kernel_size=2, padding=0, stride=[2, 1]),
            nn.BatchNorm2D(num_features=512),
            nn.ReLU()
        )
        
    def forward(self, x):
        try:
            x = self.block1(x)
            x = self.block2(x)
            x = self.block3(x)
            x = self.block4(x)
            x = self.block5(x)
            x = self.block6(x)
            x = self.block7(x)
            
            # Now x shape is: [B, 512, 1, W/4]
            # Reshape to Feature Sequence [B, T, 512] where T = W/4
            # 1. Squeeze the height dimension (which is 1)
            x = paddle.squeeze(x, axis=2) # Shape: [B, 512, W/4]
            # 2. Transpose to [B, W/4, 512] == [B, T, 512]
            x = paddle.transpose(x, perm=[0, 2, 1])
            
            return x
        except Exception as e:
            raise RuntimeError(f"Error in CNN Backbone forward pass: {str(e)}")
