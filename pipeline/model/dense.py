"""
Dense layer for character classification.
"""

import paddle
import paddle.nn as nn

class DenseLayer(nn.Layer):
    """
    Final Dense layer mapping from BiLSTM hidden state to vocabulary size.
    Input: [B, T, 512]
    Output: [B, T, num_classes + 1] (where 1 is for CTC blank token)
    """
    def __init__(self, input_size: int = 512, num_classes: int = 96):
        super(DenseLayer, self).__init__()
        
        # +1 for CTC blank token
        self.fc = nn.Linear(
            in_features=input_size,
            out_features=num_classes + 1
        )
        
    def forward(self, x):
        try:
            # x shape: [B, T, 512]
            x = self.fc(x) # x shape: [B, T, num_classes + 1]
            return x
        except Exception as e:
            raise RuntimeError(f"Error in Dense forward pass: {str(e)}")
