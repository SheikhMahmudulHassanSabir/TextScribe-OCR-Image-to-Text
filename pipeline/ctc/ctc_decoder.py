"""
CTC Decoder for prediction.
"""

import numpy as np  # type: ignore
from typing import List

class CTCDecoder:
    """
    CTC Decoder implementing Greedy and Beam Search decoding.
    """
    def __init__(self, charset: List[str], blank_index: int = 0):
        self.charset = charset
        self.blank_index = blank_index
        
    def greedy_decode(self, preds: np.ndarray) -> List[str]:
        """
        Greedy decoder: argmax -> collapse repeats -> remove blanks
        
        Args:
            preds: Predictions of shape [B, T, C+1] or [T, B, C+1] 
                   Assuming [B, T, C+1] based on model output.
            
        Returns:
            List of decoded strings, one per batch item.
        """
        try:
            # 1. argmax over probability distribution
            indices = np.argmax(preds, axis=2) # [B, T]
            
            decoded_texts = []
            for b in range(indices.shape[0]):
                sequence = indices[b]
                text = []
                prev_idx = -1
                
                for idx in sequence:
                    # collapse repeats and ignore blanks
                    if idx != self.blank_index and idx != prev_idx:
                        # Character index is usually shifted by 1 because blank=0
                        char_idx = idx - 1
                        if 0 <= char_idx < len(self.charset):
                            text.append(self.charset[char_idx])
                    prev_idx = idx
                    
                decoded_texts.append("".join(text))
                
            return decoded_texts
        except Exception as e:
            raise RuntimeError(f"Error in Greedy Decoding: {str(e)}")

    def beam_search_decode(self, preds: np.ndarray, beam_width: int = 10) -> List[str]:
        """
        Beam search decoder. Currently falls back to greedy for simplicity,
        as Paddle's native beam search is complex to implement purely in NumPy.
        """
        print(f"Beam search (width={beam_width}) not fully implemented. Falling back to greedy.")
        return self.greedy_decode(preds)
