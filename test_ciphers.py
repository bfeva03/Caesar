"""
Unit tests for cipher implementations.
Run with: python test_ciphers.py
"""

from __future__ import annotations

import unittest
from cipher import (
    caesar_shift,
    atbash,
    rot47,
    rot5_digits,
    reverse_text,
    affine_transform,
    rail_fence_decrypt,
    brute_force,
)
from scoring import score_english
from analysis_panel import _calculate_ioc, _detect_cipher_type


class TestCaesarCipher(unittest.TestCase):
    """Test Caesar cipher functionality."""

    def test_caesar_basic(self):
        """Test basic Caesar shift."""
        plaintext = "HELLO"
        encrypted = caesar_shift(plaintext, 3)
        self.assertEqual(encrypted, "KHOOR")

        # Decrypt
        decrypted = caesar_shift(encrypted, -3)
        self.assertEqual(decrypted, "HELLO")

    def test_caesar_wrap(self):
        """Test Caesar shift wrapping around alphabet."""
        self.assertEqual(caesar_shift("XYZ", 3), "ABC")
        self.assertEqual(caesar_shift("ABC", -3), "XYZ")

    def test_caesar_preserve_case(self):
        """Test case preservation."""
        text = "Hello World"
        encrypted = caesar_shift(text, 5, keep_case=True)
        self.assertTrue(encrypted[0].isupper())
        self.assertTrue(encrypted[6].isupper())

    def test_caesar_punctuation(self):
        """Test punctuation handling."""
        text = "Hello, World!"
        encrypted = caesar_shift(text, 3, keep_punct=True)
        self.assertIn(",", encrypted)
        self.assertIn("!", encrypted)


class TestAtbash(unittest.TestCase):
    """Test Atbash cipher."""

    def test_atbash_basic(self):
        """Test basic Atbash transformation."""
        plaintext = "ABCXYZ"
        encrypted = atbash(plaintext)
        self.assertEqual(encrypted, "ZYXCBA")

        # Atbash is symmetric
        decrypted = atbash(encrypted)
        self.assertEqual(decrypted, plaintext)

    def test_atbash_sample(self):
        """Test with known sample."""
        ciphertext = "GSRH RH Z HVXIVG"
        plaintext = atbash(ciphertext, keep_case=False, keep_punct=False)
        self.assertIn("THIS", plaintext)
        self.assertIn("SECRET", plaintext)


class TestROT47(unittest.TestCase):
    """Test ROT47 cipher."""

    def test_rot47_basic(self):
        """Test basic ROT47."""
        plaintext = "Hello World!"
        encrypted = rot47(plaintext)
        # Double application should restore
        decrypted = rot47(rot47(plaintext))
        self.assertEqual(decrypted, plaintext)


class TestROT5(unittest.TestCase):
    """Test ROT5 cipher (digits only)."""

    def test_rot5_digits(self):
        """Test ROT5 on digits."""
        plaintext = "12345"
        encrypted = rot5_digits(plaintext)
        self.assertEqual(encrypted, "67890")

        # Double application restores
        decrypted = rot5_digits(encrypted)
        self.assertEqual(decrypted, plaintext)

    def test_rot5_non_digits(self):
        """Test ROT5 preserves non-digits."""
        text = "Test 123"
        encrypted = rot5_digits(text)
        self.assertIn("Test", encrypted)


class TestReverse(unittest.TestCase):
    """Test text reversal."""

    def test_reverse_basic(self):
        """Test basic reversal."""
        plaintext = "Hello World"
        reversed_text = reverse_text(plaintext)
        self.assertEqual(reversed_text, "dlroW olleH")

        # Double reverse restores
        restored = reverse_text(reversed_text)
        self.assertEqual(restored, plaintext)


class TestAffine(unittest.TestCase):
    """Test Affine cipher."""

    def test_affine_encode_decode(self):
        """Test Affine encoding and decoding."""
        plaintext = "HELLO"
        a, b = 5, 8

        # Encode
        encrypted = affine_transform(plaintext, a, b, decode=False)

        # Decode
        decrypted = affine_transform(encrypted, a, b, decode=True)
        self.assertEqual(decrypted, plaintext)

    def test_affine_invalid_a(self):
        """Test Affine with invalid 'a' (not coprime with 26)."""
        plaintext = "HELLO"
        # a=2 is not valid (gcd(2,26) != 1)
        result = affine_transform(plaintext, 2, 5, decode=False)
        # Should return original text when invalid
        self.assertEqual(result, plaintext)


class TestRailFence(unittest.TestCase):
    """Test Rail Fence cipher."""

    def test_rail_fence_basic(self):
        """Test basic Rail Fence decryption."""
        ciphertext = "WECRLTEERDSOEEFEAOCAIVDEN"
        decrypted = rail_fence_decrypt(ciphertext, 3)
        self.assertEqual(decrypted, "WEAREDISCOVEREDFLEEATONCE")


class TestScoring(unittest.TestCase):
    """Test English scoring function."""

    def test_score_english_text(self):
        """Test scoring of English text."""
        english = "The quick brown fox jumps over the lazy dog"
        gibberish = "Qrv nzxpd wkbjm gbh yzloc xkvt yis pefa mbt"

        english_score = score_english(english)
        gibberish_score = score_english(gibberish)

        # English should score higher
        self.assertGreater(english_score, gibberish_score)

    def test_score_empty(self):
        """Test scoring of empty text."""
        score = score_english("")
        self.assertLess(score, 0)

    def test_score_caching(self):
        """Test that scoring is cached."""
        text = "Hello World"
        score1 = score_english(text)
        score2 = score_english(text)
        self.assertEqual(score1, score2)


class TestAnalysis(unittest.TestCase):
    """Test analysis functions."""

    def test_ioc_english(self):
        """Test IoC calculation on English text."""
        # Use more varied English text for realistic IoC
        english = (
            "The quick brown fox jumps over the lazy dog. "
            "Pack my box with five dozen liquor jugs. "
            "How vexingly quick daft zebras jump. "
            "Sphinx of black quartz judge my vow. "
        ) * 5
        ioc = _calculate_ioc(english)
        # English IoC varies with text; just ensure reasonable range
        self.assertGreater(ioc, 0.035)
        self.assertLess(ioc, 0.080)

    def test_ioc_random(self):
        """Test IoC on random-like text."""
        # Uniform distribution
        random = "abcdefghijklmnopqrstuvwxyz" * 10
        ioc = _calculate_ioc(random)
        # Should be close to 1/26 ≈ 0.038
        self.assertLess(ioc, 0.042)

    def test_detect_cipher_type(self):
        """Test cipher type detection."""
        # Use varied English text
        english = (
            "The quick brown fox jumps over the lazy dog. "
            "Pack my box with five dozen liquor jugs. "
        ) * 10
        detection = _detect_cipher_type(english)
        # Detection may vary, just ensure it returns something reasonable
        self.assertIsInstance(detection, str)
        self.assertGreater(len(detection), 5)


class TestBruteForce(unittest.TestCase):
    """Test brute force functionality."""

    def test_brute_force_caesar(self):
        """Test Caesar brute force."""
        ciphertext = "KHOOR"  # Caesar shift 3 of "HELLO"
        results = brute_force(ciphertext, "Caesar", "ciphertext")

        # Should return 26 results
        self.assertEqual(len(results), 26)

        # Check that "HELLO" appears in top results (might not be first due to short text)
        found = any("HELLO" in r["text"] for r in results[:5])
        self.assertTrue(found, "HELLO not found in top 5 results")

    def test_brute_force_atbash(self):
        """Test Atbash brute force."""
        ciphertext = "SVOOL"  # Atbash of "HELLO"
        results = brute_force(ciphertext, "Atbash", "ciphertext")

        # Should return 1 result
        self.assertEqual(len(results), 1)
        self.assertIn("HELLO", results[0]["text"])

    def test_brute_force_try_all(self):
        """Test Try All meta-cipher."""
        ciphertext = "KHOOR"  # Caesar shift 3
        results = brute_force(ciphertext, "Try All (Fast)", "ciphertext")

        # Should return multiple results
        self.assertGreater(len(results), 0)

        # Should find the correct decryption
        found_hello = any("HELLO" in r["text"] for r in results[:10])
        self.assertTrue(found_hello)

    def test_brute_force_error_handling(self):
        """Test error handling in brute force."""
        # Should not crash even with invalid input
        results = brute_force("", "Caesar", "ciphertext")
        self.assertIsInstance(results, list)


class TestSamples(unittest.TestCase):
    """Test that all samples decrypt correctly."""

    def test_all_samples(self):
        """Test each sample can be decrypted."""
        from samples import SAMPLES

        for cipher_name, sample in SAMPLES.items():
            if cipher_name == "Substitution (manual)":
                continue  # Skip manual cipher

            with self.subTest(cipher=cipher_name):
                results = brute_force(sample["ciphertext"], cipher_name, "ciphertext")

                # Should have at least one result
                self.assertGreater(len(results), 0)

                # Check if expected text appears in top results
                found = False
                for result in results[:10]:
                    if sample["expected"].upper().replace(" ", "") in result[
                        "text"
                    ].upper().replace(" ", ""):
                        found = True
                        break

                self.assertTrue(found, f"Failed to decrypt {cipher_name} sample")


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
