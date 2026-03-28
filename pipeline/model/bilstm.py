"""
BiLSTM sequence model.
"""

import paddle
import paddle.nn as nn

class SequenceModel(nn.Layer):
    """
    BiLSTM sequence processing module.
    Input: [B, T, 512]
    Output: [B, T, 512]
    """
    def __init__(self, input_size: int = 512, hidden_size: int = 256):
        super(SequenceModel, self).__init__()
        
        self.lstm1 = nn.LSTM(
            input_size=input_size, 
            hidden_size=hidden_size, 
            direction='bidirectional'
        )
        
        # Output of BiLSTM has size 2 * hidden_size = 512
        self.lstm2 = nn.LSTM(
            input_size=hidden_size * 2, 
            hidden_size=hidden_size, 
            direction='bidirectional'
        )
        
    def forward(self, x):
        try:
            # x shape: [B, T, 512]
            # LSTM returns (output, (h, c))
            x, _ = self.lstm1(x) # x shape: [B, T, 512]
            x, _ = self.lstm2(x) # x shape: [B, T, 512]
            return x
        except Exception as e:
            raise RuntimeError(f"Error in BiLSTM forward pass: {str(e)}")
