from __future__ import annotations

import math
import re
from collections import Counter
from functools import lru_cache

# English letter frequencies (percentage)
EN_FREQ = {
    "E": 12.70,
    "T": 9.06,
    "A": 8.17,
    "O": 7.51,
    "I": 6.97,
    "N": 6.75,
    "S": 6.33,
    "H": 6.09,
    "R": 5.99,
    "D": 4.25,
    "L": 4.03,
    "C": 2.78,
    "U": 2.76,
    "M": 2.41,
    "W": 2.36,
    "F": 2.23,
    "G": 2.02,
    "Y": 1.97,
    "P": 1.93,
    "B": 1.49,
    "V": 0.98,
    "K": 0.77,
    "J": 0.15,
    "X": 0.15,
    "Q": 0.10,
    "Z": 0.07,
}

# A small but strong word list (fast + high signal)
COMMON_WORDS = {
    "the",
    "be",
    "to",
    "of",
    "and",
    "a",
    "in",
    "that",
    "have",
    "i",
    "it",
    "for",
    "not",
    "on",
    "with",
    "he",
    "as",
    "you",
    "do",
    "at",
    "this",
    "but",
    "his",
    "by",
    "from",
    "they",
    "we",
    "say",
    "her",
    "she",
    "or",
    "an",
    "will",
    "my",
    "one",
    "all",
    "would",
    "there",
    "their",
    "what",
    "so",
    "up",
    "out",
    "if",
    "about",
    "who",
    "get",
    "which",
    "go",
    "me",
    "when",
    "make",
    "can",
    "like",
    "time",
    "no",
    "just",
    "him",
    "know",
    "take",
    "people",
    "into",
    "year",
    "your",
    "good",
    "some",
    "could",
    "them",
    "see",
    "other",
    "than",
    "then",
    "now",
    "look",
    "only",
    "come",
    "its",
    "over",
    "think",
    "also",
    "back",
    "after",
    "use",
    "two",
    "how",
    "our",
    "work",
    "first",
    "well",
    "way",
    "even",
    "new",
    "want",
    "because",
    "any",
    "these",
    "give",
    "day",
    "most",
    "us",
}

COMMON_BIGRAMS = (
    "TH",
    "HE",
    "IN",
    "ER",
    "AN",
    "RE",
    "ON",
    "AT",
    "EN",
    "ND",
    "TI",
    "ES",
    "OR",
    "TE",
    "OF",
    "ED",
    "IS",
    "IT",
    "AL",
    "AR",
    "ST",
    "TO",
    "NT",
    "NG",
    "SE",
    "HA",
    "AS",
    "OU",
    "IO",
    "LE",
    "VE",
)
COMMON_TRIGRAMS = (
    "THE",
    "AND",
    "ING",
    "HER",
    "ERE",
    "ENT",
    "THA",
    "NTH",
    "WAS",
    "ETH",
    "FOR",
    "DTH",
    "HAT",
    "ION",
)

_word_re = re.compile(r"[A-Za-z]+")


def _letters_only(s: str) -> str:
    return "".join(ch for ch in s.upper() if "A" <= ch <= "Z")


def _chi_squared(text: str) -> float:
    letters = _letters_only(text)
    n = len(letters)
    if n == 0:
        return 1e9

    counts = Counter(letters)
    chi = 0.0
    for ch, exp_pct in EN_FREQ.items():
        observed = counts.get(ch, 0)
        expected = n * (exp_pct / 100.0)
        if expected > 0:
            diff = observed - expected
            chi += (diff * diff) / expected
    return chi


def _word_hits(text: str) -> int:
    words = _word_re.findall(text.lower())
    if not words:
        return 0
    hits = 0
    for w in words:
        if w in COMMON_WORDS:
            hits += 1
    return hits


def _ngram_bonus(text: str) -> float:
    s = _letters_only(text)
    if len(s) < 4:
        return 0.0

    # bigram/trigram hits (lightweight counts)
    b = 0.0
    for bg in COMMON_BIGRAMS:
        b += s.count(bg) * 0.18
    for tg in COMMON_TRIGRAMS:
        b += s.count(tg) * 0.45
    return b


def _vowel_penalty(text: str) -> float:
    s = _letters_only(text)
    n = len(s)
    if n < 10:
        return 0.0
    vowels = sum(1 for ch in s if ch in "AEIOU")
    r = vowels / n
    # English tends to sit around ~0.38-0.45 vowels in normal text (varies).
    # Penalize extremes, especially too-low vowels (gibberish).
    if r < 0.24:
        return (0.24 - r) * 40.0
    if r > 0.60:
        return (r - 0.60) * 30.0
    return 0.0


def _nonsense_cluster_penalty(text: str) -> float:
    # Penalize long consonant runs (common in wrong decrypts)
    s = _letters_only(text)
    if len(s) < 12:
        return 0.0
    penalty = 0.0
    run = 0
    for ch in s:
        if ch in "AEIOU":
            run = 0
        else:
            run += 1
            if run >= 5:
                penalty += 1.2
            if run >= 7:
                penalty += 2.0
    return penalty


def _symbol_space_penalty(text: str) -> float:
    if not text:
        return 1e6
    letters = sum(ch.isalpha() for ch in text)
    if len(text) == 0:
        return 1e6
    nonletter_ratio = (len(text) - letters) / len(text)
    penalty = 0.0
    # Too many symbols tends to indicate junk
    if nonletter_ratio > 0.45:
        penalty += (nonletter_ratio - 0.45) * 25.0
    # No spaces in longer strings tends to indicate junk
    if len(text) > 35 and text.count(" ") < 2:
        penalty += 6.0
    return penalty


@lru_cache(maxsize=1024)
def score_english(text: str) -> float:
    """
    Higher is better. Designed to be fast and stable for ranking brute-force outputs.
    Cached for performance.
    """
    if not text or not text.strip():
        return -1e9

    # Base: frequency match (invert chi-squared)
    chi = _chi_squared(text)
    freq_score = 120.0 / (1.0 + chi)

    # Strong signal: real common words
    hits = _word_hits(text)
    word_bonus = hits * 2.8

    # Medium signal: n-grams
    ngram_bonus = _ngram_bonus(text)

    # Penalties
    penalty = 0.0
    penalty += _symbol_space_penalty(text)
    penalty += _vowel_penalty(text)
    penalty += _nonsense_cluster_penalty(text)

    # Slight preference for sensible casing (not ALL CAPS) unless short
    if len(text) > 20:
        letters = sum(ch.isalpha() for ch in text)
        caps = sum(ch.isupper() for ch in text if ch.isalpha())
        if letters > 0:
            cap_ratio = caps / letters
            if cap_ratio > 0.92:
                penalty += 1.8

    return freq_score + word_bonus + ngram_bonus - penalty
