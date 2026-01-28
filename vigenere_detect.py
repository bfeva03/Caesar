from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

_alpha_re = re.compile(r"[A-Z]")


def _only_letters(text: str) -> str:
    return "".join(ch for ch in text.upper() if "A" <= ch <= "Z")


def _ioc(s: str) -> float:
    n = len(s)
    if n < 2:
        return 0.0
    c = Counter(s)
    num = sum(v * (v - 1) for v in c.values())
    den = n * (n - 1)
    return num / den


def ioc_scan(text: str, max_len: int = 20) -> list[tuple[int, float]]:
    s = _only_letters(text)
    out = []
    for k in range(1, max_len + 1):
        cols = [s[i::k] for i in range(k)]
        vals = [_ioc(col) for col in cols if len(col) >= 2]
        score = sum(vals) / len(vals) if vals else 0.0
        out.append((k, score))
    # sort by best IoC (higher is better; english ~0.065)
    return sorted(out, key=lambda x: x[1], reverse=True)


def kasiski(text: str, ngram: int = 3, top: int = 8) -> list[tuple[int, int]]:
    s = _only_letters(text)
    if len(s) < ngram * 3:
        return []

    positions = defaultdict(list)
    for i in range(len(s) - ngram + 1):
        g = s[i : i + ngram]
        positions[g].append(i)

    dists = []
    for g, pos in positions.items():
        if len(pos) >= 3:
            for a, b in zip(pos, pos[1:]):
                dists.append(b - a)

    if not dists:
        return []

    # Count factors of distances (likely key lengths)
    factor_counts = Counter()
    for d in dists:
        for f in range(2, min(30, d) + 1):
            if d % f == 0:
                factor_counts[f] += 1

    return factor_counts.most_common(top)


def summarize(text: str, max_len: int = 20) -> str:
    letters = _only_letters(text)
    if len(letters) < 40:
        return "Vigenère detect: need ~40+ letters for reliable key-length hints."

    ioc_best = ioc_scan(text, max_len=max_len)[:6]
    kas = kasiski(text, ngram=3, top=8)

    ioc_str = ", ".join([f"{k}:{v:.3f}" for k, v in ioc_best])
    kas_str = ", ".join([f"{k}({c})" for k, c in kas]) if kas else "—"

    return (
        "Vigenère key-length hints\n"
        f"IoC best (k:score): {ioc_str}\n"
        f"Kasiski factors (len(count)): {kas_str}\n"
        "Tip: If the same length appears in BOTH lists, it’s a strong candidate."
    )
