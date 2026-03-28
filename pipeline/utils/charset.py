"""
Character set definitions.
"""
from typing import List

def get_default_charset() -> List[str]:
    """
    Returns standard printable English character set.
    """
    digits = "0123456789"
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    punctuation = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "
    
    charset = list(digits + lower + upper + punctuation)
    return charset
