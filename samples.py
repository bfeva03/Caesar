from __future__ import annotations

# Minimal demo samples (ciphertext + expected plaintext)
# Keep these short so the UI stays snappy.

SAMPLES = {
    "Caesar": {
        "ciphertext": "Khoor Zruog! Frgh lv ixq.",
        "expected": "Hello World! Code is fun.",
        "hint": "shift=3",
    },
    "Atbash": {
        "ciphertext": "GSRH RH Z HVXIVG NVHHZTV",
        "expected": "THIS IS A SECRET MESSAGE",
        "hint": "atbash",
    },
    "Affine": {
        # encrypted with a=5,b=8 from "Affine cipher! This is a test."
        "ciphertext": "Ihhwvc swfrcp! Zrwu wu i zcuz.",
        "expected": "Affine cipher! This is a test.",
        "hint": "a=5,b=8",
    },
    "ROT47": {
        "ciphertext": r"w6==@ (@C=5P",
        "expected": "Hello World!",
        "hint": "rot47",
    },
    "ROT5 (digits)": {
        "ciphertext": "67890 12345",
        "expected": "12345 67890",
        "hint": "rot5",
    },
    "Reverse": {
        "ciphertext": "!dlroW olleH",
        "expected": "Hello World!",
        "hint": "simple reversal",
    },
    "Rail Fence": {
        "ciphertext": "WECRLTEERDSOEEFEAOCAIVDEN",
        "expected": "WEAREDISCOVEREDFLEEATONCE",
        "hint": "rails=3",
    },
    "Try All (Fast)": {
        "ciphertext": "Khoor Zruog! Frgh lv ixq.",
        "expected": "Hello World! Code is fun.",
        "hint": "tries multiple ciphers",
    },
}
