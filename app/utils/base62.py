import random
import string

ALPHABET = string.digits + string.ascii_letters  # 0-9, a-z, A-Z (62 chars)
BASE = len(ALPHABET)


def encode(num: int) -> str:
    """Convert a number to Base62 string."""
    if num == 0:
        return ALPHABET[0]
    
    chars = []
    while num:
        num, remainder = divmod(num, BASE)
        chars.append(ALPHABET[remainder])
    return ''.join(reversed(chars))


def decode(short_code: str) -> int:
    """Convert a Base62 string back to number."""
    num = 0
    for char in short_code:
        num = num * BASE + ALPHABET.index(char)
    return num


def generate_short_code(length: int = 7) -> str:
    """Generate a random short code."""
    return ''.join(random.choices(ALPHABET, k=length))