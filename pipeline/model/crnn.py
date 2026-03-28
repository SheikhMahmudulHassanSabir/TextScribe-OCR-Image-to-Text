"""
CRNN Model wrapping Backbone, BiLSTM, and Dense components.
"""

import paddle
import paddle.nn as nn
from .cnn_backbone import CNNBackbone
from .bilstm import SequenceModel
from .dense import DenseLayer

class CRNN(nn.Layer):
    """
    Complete CRNN Architecture combining CNN backbone, BiLSTM, and Dense layer.
    """
    def __init__(self, num_classes: int = 96, hidden_size: int = 256):
        super(CRNN, self).__init__()
        
        self.backbone = CNNBackbone()
        self.sequence_model = SequenceModel(input_size=512, hidden_size=hidden_size)
        self.dense = DenseLayer(input_size=512, num_classes=num_classes)
        
    def forward(self, x):
        try:
            # 1. Feature extraction
            # x shape: [B, 1, 32, W]
            x = self.backbone(x)
            
            # 2. Sequence modeling
            # x shape: [B, T, 512]
            x = self.sequence_model(x)
            
            # 3. Dense layer classification
            # x shape: [B, T, 512]
            x = self.dense(x)
            
            # Output shape: [B, T, num_classes + 1]
            return x
        except Exception as e:
            raise RuntimeError(f"Error in CRNN forward pass: {str(e)}")
