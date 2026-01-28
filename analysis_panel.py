from __future__ import annotations

import re
from collections import Counter
from tkinter import ttk

_letters_re = re.compile(r"[a-z]", re.IGNORECASE)


def _clean_letters(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.isalpha())


def _calculate_ioc(text: str) -> float:
    """Calculate Index of Coincidence."""
    letters = _clean_letters(text)
    n = len(letters)
    if n < 2:
        return 0.0

    freq = Counter(letters)
    numerator = sum(count * (count - 1) for count in freq.values())
    denominator = n * (n - 1)
    return numerator / denominator if denominator > 0 else 0.0


def _detect_cipher_type(text: str) -> str:
    """Heuristic cipher type detection."""
    letters = _clean_letters(text)
    if not letters:
        return "Unknown"

    ioc = _calculate_ioc(text)

    # English text: IoC ≈ 0.065-0.068
    # Random text: IoC ≈ 0.038
    # Monoalphabetic substitution: IoC ≈ 0.065 (preserves distribution)
    # Polyalphabetic (Vigenère): IoC ≈ 0.038-0.045

    if ioc > 0.060:
        return "Likely monoalphabetic (Caesar/Substitution)"
    elif ioc > 0.045:
        return "Possibly polyalphabetic (Vigenère)"
    elif ioc < 0.040:
        return "Possibly transposition or random"
    else:
        return "Unknown pattern"


def _top_letters(text: str, n: int = 10):
    s = _clean_letters(text)
    c = Counter(s)
    total = sum(c.values()) or 1
    out = []
    for ch, cnt in c.most_common(n):
        out.append((ch.upper(), cnt, (cnt / total) * 100.0))
    return out, total


def _top_bigrams(text: str, n: int = 10):
    s = _clean_letters(text)
    bigrams = [s[i : i + 2] for i in range(len(s) - 1)]
    c = Counter(bigrams)
    total = sum(c.values()) or 1
    out = []
    for bg, cnt in c.most_common(n):
        out.append((bg.upper(), cnt, (cnt / total) * 100.0))
    return out


class AnalysisPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=14)
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Analysis", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        self.lbl_stats = ttk.Label(
            self, text="—", style="Subtle.TLabel", wraplength=520, justify="left"
        )
        self.lbl_stats.grid(row=1, column=0, sticky="w", pady=(6, 10))

        self.lbl_letters = ttk.Label(
            self,
            text="Top letters: —",
            style="Subtle.TLabel",
            wraplength=520,
            justify="left",
        )
        self.lbl_letters.grid(row=2, column=0, sticky="w", pady=(0, 8))

        self.lbl_bigrams = ttk.Label(
            self,
            text="Top bigrams: —",
            style="Subtle.TLabel",
            wraplength=520,
            justify="left",
        )
        self.lbl_bigrams.grid(row=3, column=0, sticky="w")

    def update_text(self, text: str):
        if not text:
            self.lbl_stats.configure(text="—")
            self.lbl_letters.configure(text="Top letters: —")
            self.lbl_bigrams.configure(text="Top bigrams: —")
            return

        length = len(text)
        letters = sum(ch.isalpha() for ch in text)
        spaces = text.count(" ")
        pct_letters = (letters / length) * 100.0 if length else 0.0

        # Calculate IoC and detect cipher type
        ioc = _calculate_ioc(text)
        cipher_hint = _detect_cipher_type(text)

        stats = f"Length: {length} • Letters: {pct_letters:.1f}% • Spaces: {spaces} • IoC: {ioc:.3f}\\n{cipher_hint}"
        self.lbl_stats.configure(text=stats)

        top_letters, _ = _top_letters(text, n=10)
        letters_str = ", ".join(f"{ch}:{pct:.1f}%" for ch, _cnt, pct in top_letters)
        self.lbl_letters.configure(text=f"Top letters: {letters_str}")

        top_bi = _top_bigrams(text, n=10)
        bigrams_str = ", ".join(f"{bg}:{pct:.1f}%" for bg, _cnt, pct in top_bi)
        self.lbl_bigrams.configure(text=f"Top bigrams: {bigrams_str}")
