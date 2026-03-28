"""
Configuration settings for the PaddleOCR Pipeline.
"""

from typing import Any, Dict

config: Dict[str, Any] = {
    "resize":        {"enabled": False, "height": 32, "max_width": 1280},
    "grayscale":     {"enabled": False},
    "denoise":       {"enabled": False, "h": 10},
    "clahe":         {"enabled": False, "clip_limit": 2.0, "tile_grid": (8, 8)},
    "threshold":     {"enabled": False, "block_size": 11, "C": 2},
    "morph":         {"enabled": False, "op": "dilate", "kernel_size": (2, 2)},
    "deskew":        {"enabled": False, "min_angle": 0.5},
    "num_classes":   96,
    "hidden_size":   256,
    "blank_index":   0,
    "beam_width":    10,
    "use_gpu":       False,
    "lang":          "en",
    "use_angle_cls": True,
}
