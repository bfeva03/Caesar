from __future__ import annotations

import math
import string
from typing import Dict, List, Optional

from scoring import score_english
from vigenere_detect import ioc_scan

AZ_LOWER = string.ascii_lowercase
AZ_UPPER = string.ascii_uppercase


def _keep_or_drop(ch: str, keep_punct: bool) -> str:
    if keep_punct:
        return ch
    return ""


def caesar_shift(
    text: str, shift: int, keep_case: bool = True, keep_punct: bool = True
) -> str:
    s = shift % 26

    def shift_char(c: str) -> str:
        if c.islower():
            idx = ord(c) - 97
            out = chr(((idx + s) % 26) + 97)
            return out if keep_case else out.upper()
        if c.isupper():
            idx = ord(c) - 65
            out = chr(((idx + s) % 26) + 65)
            return out if keep_case else out.upper()
        return _keep_or_drop(c, keep_punct)

    return "".join(shift_char(c) for c in text)


def atbash(text: str, keep_case: bool = True, keep_punct: bool = True) -> str:
    def flip(c: str) -> str:
        if c.islower():
            idx = ord(c) - 97
            out = chr((25 - idx) + 97)
            return out if keep_case else out.upper()
        if c.isupper():
            idx = ord(c) - 65
            out = chr((25 - idx) + 65)
            return out if keep_case else out.upper()
        return _keep_or_drop(c, keep_punct)

    return "".join(flip(c) for c in text)


def rot47(text: str) -> str:
    # ROT47 over printable ASCII from '!' (33) to '~' (126)
    out = []
    for ch in text:
        o = ord(ch)
        if 33 <= o <= 126:
            out.append(chr(33 + ((o - 33 + 47) % 94)))
        else:
            out.append(ch)
    return "".join(out)


def rot5_digits(text: str) -> str:
    # Rotate digits 0-9 by 5 (a.k.a. ROT5)
    out = []
    for ch in text:
        if "0" <= ch <= "9":
            out.append(chr(ord("0") + ((ord(ch) - ord("0") + 5) % 10)))
        else:
            out.append(ch)
    return "".join(out)


def _modinv(a: int, m: int) -> Optional[int]:
    # Python 3.8+ supports pow(a, -1, m), but guard just in case
    try:
        return pow(a, -1, m)
    except ValueError:
        return None


_VALID_AFFINE_A = [a for a in range(1, 26, 2) if math.gcd(a, 26) == 1]  # 12 values


def affine_transform(
    text: str,
    a: int,
    b: int,
    decode: bool,
    keep_case: bool = True,
    keep_punct: bool = True,
) -> str:
    inv = _modinv(a, 26)
    if inv is None:
        return text

    def transform_char(c: str) -> str:
        if c.islower():
            x = ord(c) - 97
            if decode:
                y = (inv * (x - b)) % 26
            else:
                y = (a * x + b) % 26
            out = chr(y + 97)
            return out if keep_case else out.upper()

        if c.isupper():
            x = ord(c) - 65
            if decode:
                y = (inv * (x - b)) % 26
            else:
                y = (a * x + b) % 26
            out = chr(y + 65)
            return out if keep_case else out.upper()

        return _keep_or_drop(c, keep_punct)

    return "".join(transform_char(c) for c in text)


def reverse_text(text: str, keep_case: bool = True, keep_punct: bool = True) -> str:
    """Simple text reversal."""
    return text[::-1]


def rail_fence_decrypt(text: str, rails: int) -> str:
    """Decrypt rail fence cipher with given number of rails."""
    if rails < 2:
        return text

    # Remove non-letters if punctuation not kept
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1

    # Calculate positions
    for char in text:
        fence[rail].append(None)
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction = -direction

    # Fill fence with characters
    idx = 0
    for r in range(rails):
        for i in range(len(fence[r])):
            if idx < len(text):
                fence[r][i] = text[idx]
                idx += 1

    # Read in zigzag
    result = []
    rail = 0
    direction = 1
    for _ in range(len(text)):
        if fence[rail]:
            result.append(fence[rail].pop(0))
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction = -direction

    return "".join(result)


def columnar_decrypt(text: str, key: str) -> str:
    """Decrypt columnar transposition with alphabetic key."""
    if not key or not text:
        return text

    key_len = len(key)
    num_rows = (len(text) + key_len - 1) // key_len

    # Create column order based on alphabetical key
    key_order = sorted(range(key_len), key=lambda k: key[k])

    # Calculate column lengths
    full_cols = len(text) % key_len or key_len
    col_lengths = [num_rows if i < full_cols else num_rows - 1 for i in range(key_len)]

    # Fill columns
    columns = []
    idx = 0
    for i in key_order:
        col_len = col_lengths[i]
        columns.append(text[idx : idx + col_len])
        idx += col_len

    # Reorder columns
    ordered_columns = [""] * key_len
    for i, col in zip(key_order, columns):
        ordered_columns[i] = col

    # Read row by row
    result = []
    for row in range(num_rows):
        for col in ordered_columns:
            if row < len(col):
                result.append(col[row])

    return "".join(result)


def brute_force(
    text: str,
    cipher: str = "Caesar",
    input_mode: str = "ciphertext",
    keep_case: bool = True,
    keep_punct: bool = True,
) -> List[Dict]:
    """
    Returns list of rows, each row:
      { "key": str, "score": float, "text": str, "note": str }
    Sorted best score first.
    """
    try:
        cipher = (cipher or "Caesar").strip()

        # Single-transform ciphers
        if cipher == "Atbash":
            candidate = atbash(text, keep_case=keep_case, keep_punct=keep_punct)
            return [
                {
                    "key": "Atbash",
                    "score": score_english(candidate),
                    "text": candidate,
                    "note": "single transform",
                }
            ]

        if cipher == "ROT47":
            candidate = rot47(text)
            return [
                {
                    "key": "ROT47",
                    "score": score_english(candidate),
                    "text": candidate,
                    "note": "single transform",
                }
            ]

        if cipher == "ROT5 (digits)":
            candidate = rot5_digits(text)
            return [
                {
                    "key": "ROT5",
                    "score": score_english(candidate),
                    "text": candidate,
                    "note": "digits only",
                }
            ]

        if cipher == "Reverse":
            candidate = reverse_text(text, keep_case=keep_case, keep_punct=keep_punct)
            return [
                {
                    "key": "Reverse",
                    "score": score_english(candidate),
                    "text": candidate,
                    "note": "text reversal",
                }
            ]

        # Rail Fence
        if cipher == "Rail Fence":
            rows = []
            for rails in range(2, min(len(text) // 2, 20)):
                try:
                    cand = rail_fence_decrypt(text, rails)
                    rows.append(
                        {
                            "key": f"rails={rails}",
                            "score": score_english(cand),
                            "text": cand,
                            "note": "transposition",
                        }
                    )
                except Exception:
                    continue
            rows.sort(key=lambda r: r["score"], reverse=True)
            return rows[:100]  # Limit results

        # Columnar Transposition (try common short keys)
        if cipher == "Columnar":
            rows = []
            common_keys = ["KEY", "CODE", "CIPHER", "SECRET", "WORD", "ABC", "ABCD"]
            for key in common_keys:
                try:
                    cand = columnar_decrypt(text, key)
                    rows.append(
                        {
                            "key": f"key={key}",
                            "score": score_english(cand),
                            "text": cand,
                            "note": "transposition",
                        }
                    )
                except Exception:
                    continue
            rows.sort(key=lambda r: r["score"], reverse=True)
            return rows

        # Try All (Fast) - runs all fast ciphers
        if cipher == "Try All (Fast)":
            all_results = []
            fast_ciphers = ["Caesar", "Atbash", "ROT47", "ROT5 (digits)", "Reverse"]

            for sub_cipher in fast_ciphers:
                try:
                    sub_results = brute_force(
                        text, sub_cipher, input_mode, keep_case, keep_punct
                    )
                    # Take top 3 from each cipher
                    for result in sub_results[:3]:
                        result["note"] = f"{sub_cipher}: {result['note']}"
                        all_results.append(result)
                except Exception:
                    continue

            # Sort all results by score
            all_results.sort(key=lambda r: r["score"], reverse=True)
            return all_results[:50]  # Return top 50 overall

        # Brute-force families
        if cipher == "Affine":
            rows = []
            decode = input_mode == "ciphertext"
            for a in _VALID_AFFINE_A:
                for b in range(26):
                    cand = affine_transform(
                        text,
                        a=a,
                        b=b,
                        decode=decode,
                        keep_case=keep_case,
                        keep_punct=keep_punct,
                    )
                    rows.append(
                        {
                            "key": f"a={a}, b={b}",
                            "score": score_english(cand),
                            "text": cand,
                            "note": "decode" if decode else "encode",
                        }
                    )
            rows.sort(key=lambda r: r["score"], reverse=True)
            return rows

        # Default: Caesar
        rows = []
        for k in range(26):
            applied_shift = (-k) if input_mode == "ciphertext" else k
            cand = caesar_shift(
                text, shift=applied_shift, keep_case=keep_case, keep_punct=keep_punct
            )
            note = (
                "ROT13"
                if (applied_shift % 26) == 13
                else ("no shift" if k == 0 else "")
            )
            rows.append(
                {
                    "key": f"{applied_shift:+d}",
                    "score": score_english(cand),
                    "text": cand,
                    "note": note,
                }
            )
        rows.sort(key=lambda r: r["score"], reverse=True)
        return rows

    except Exception as e:
        # Return error as result
        return [
            {
                "key": "Error",
                "score": -1e9,
                "text": f"Error: {str(e)}",
                "note": "failed",
            }
        ]


def detect_cipher(
    text: str,
    input_mode: str = "hex",
    keep_case: bool = False,
    keep_punct: bool = False,
) -> Dict[str, object]:
    """
    Automatically detect which cipher was used on input text.
    
    Tests multiple cipher candidates and returns the best match based on scoring.
    Uses heuristics to differentiate between similar scoring ciphers.
    
    Args:
        text: The ciphertext to analyze
        input_mode: "hex" for hexadecimal or "text" for text
        keep_case: Whether to preserve case during analysis
        keep_punct: Whether to preserve punctuation during analysis
    
    Returns:
        Dictionary with keys:
            - "cipher": Best detected cipher name (str)
            - "score": Confidence score (float)
            - "note": Additional information (str)
    """
    if not text.strip():
        return {"cipher": None, "score": 0, "note": "empty text"}
    
    # List of candidates to test (order matters for tie-breaking)
    candidates = [
        "Caesar",
        "Affine",
        "Rail Fence",
        "Columnar",
        "Atbash",
        "Vigenere",
        "ROT47",
        "ROT5",
    ]
    
    results = {}
    detail_results = {}
    
    # Test each candidate cipher
    for cipher_name in candidates:
        try:
            rows = brute_force(
                text=text,
                cipher=cipher_name,
                input_mode=input_mode,
                keep_case=keep_case,
                keep_punct=keep_punct,
            )
            
            # Get best score and details for this cipher
            if rows:
                best_result = rows[0]
                results[cipher_name] = best_result.get("score", -1e9)
                detail_results[cipher_name] = best_result
            else:
                results[cipher_name] = -1e9
        except Exception:
            results[cipher_name] = -1e9
    
    # Find best cipher by score
    if not results or all(v < -1000 for v in results.values()):
        return {"cipher": None, "score": 0, "note": "all ciphers failed"}
    
    best_score = max(results.values())
    
    # Get all ciphers within 0.5 points of best score
    close_ciphers = [(c, s) for c, s in results.items() if s >= best_score - 0.5]
    close_ciphers.sort(key=lambda x: x[1], reverse=True)
    
    # Heuristic: Rail Fence and Columnar produce high scores easily
    # If Rail Fence score is very high (>1.0) and Vigenere is close, prefer Rail Fence
    if len(text) > 40:
        rail_score = results.get("Rail Fence", -1e9)
        vigenere_score = results.get("Vigenere", -1e9)
        columnar_score = results.get("Columnar", -1e9)
        
        # Check IoC to distinguish Vigenere from transpositions
        ioc_results = ioc_scan(text.replace(" ", "").replace("\n", ""), max_len=15)
        if ioc_results:
            key_len, ioc_val = ioc_results[0]
            # High IoC (>0.063) indicates polyalphabetic like Vigenere
            if ioc_val > 0.065 and vigenere_score >= (rail_score - 0.3):
                return {
                    "cipher": "Vigenere",
                    "score": vigenere_score,
                    "note": f"IoC={ioc_val:.3f}, key_len≈{key_len}",
                }
            # Lower IoC suggests transposition (Rail Fence, Columnar)
            elif ioc_val < 0.062 and rail_score > 0.5:
                return {
                    "cipher": "Rail Fence",
                    "score": rail_score,
                    "note": f"IoC={ioc_val:.3f} (transposition)",
                }
    
    # Default: pick cipher with highest score
    best_cipher = max(results, key=results.get)
    
    return {
        "cipher": best_cipher,
        "score": best_score,
        "note": "",
    }


