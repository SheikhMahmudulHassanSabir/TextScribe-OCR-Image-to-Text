"""
CTC Loss for training CRNN.
"""

import paddle
import paddle.nn as nn

class CTCLoss(nn.Layer):
    """
    CTC Loss calculation wrapper.
    """
    def __init__(self, blank: int = 0, reduction: str = 'mean'):
        super(CTCLoss, self).__init__()
        # Paddle padding index/blank is specified during init
        self.loss_fn = nn.CTCLoss(blank=blank, reduction=reduction)
        
    def forward(self, log_probs, targets, input_lengths, target_lengths):
        """
        Args:
            log_probs: Tensor of shape [T, B, C+1] (time-first expected by CTCLoss)
            targets: Variable-length label sequences [B, ...]
            input_lengths: Tensor of shape [B]
            target_lengths: Tensor of shape [B]
            
        Returns:
            Calculated CTC loss.
        """
        try:
            return self.loss_fn(log_probs, targets, input_lengths, target_lengths)
        except Exception as e:
            raise RuntimeError(f"Error calculating CTC Loss: {str(e)}")
