import math
import random
import tempfile
import unittest
from pathlib import Path

import numpy as np

from crypto_lab.analysis import (autocorr, break_caesar, break_vigenere, entropy, est_key_len,
                                 est_period, friedman, ioc, ngram_counter, profile)
from crypto_lab.ciphers import (adfgvx, adfgvx_dec, adfgvx_square, build_ciphers, caesar,
                                gl_mod26_order, hill, int_det, mat_inv_mod, playfair,
                                playfair_unpad, rand_hill, rot13, transposition,
                                vigenere, xor_cipher, xor_decrypt)
from crypto_lab.cli import main
from crypto_lab.corpus import load_corpora, normalize
from crypto_lab.tasks import selftest

PL = normalize(__import__("crypto_lab.samples", fromlist=["SAMPLES"]).SAMPLES["pl"])


class CipherTests(unittest.TestCase):
    def test_selftest(self):
        selftest.run(verbose=False)

    def test_caesar_rot13(self):
        self.assertEqual(caesar("ABC", 3), "DEF")
        self.assertEqual(rot13(rot13(PL)), PL)
        with self.assertRaises(ValueError):
            caesar("abc", 1)

    def test_vigenere_equivalences(self):
        s = PL[:200]
        self.assertEqual(vigenere(s, "AAAAA"), s)
        self.assertEqual(vigenere(s, "DDDD"), caesar(s, 3))
        self.assertEqual(vigenere(s, "ABAB"), vigenere(s, "AB"))
        with self.assertRaises(ValueError):
            vigenere(s, "")

    def test_playfair_unpad_roundtrip(self):
        for txt in ("BALLOON", "XXAXX", "HELLOWORLD", "ABCDEFGHIKL"):
            dec = playfair(playfair(txt, "MONARCHY"), "MONARCHY", True)
            self.assertEqual(playfair_unpad(dec), txt, txt)

    def test_playfair_no_double_letters(self):
        ct = playfair(PL, "MONARCHY")
        self.assertTrue(all(ct[i] != ct[i + 1] for i in range(0, len(ct), 2)))

    def test_hill_exact_det_and_inverse(self):
        rng = random.Random(0)
        for n in (2, 3, 4):
            for _ in range(20):
                M = rand_hill(n, rng)
                self.assertEqual(int_det(M), int(round(np.linalg.det(M))))
                I = (M @ mat_inv_mod(M)) % 26
                self.assertTrue((I == np.eye(n, dtype=int)).all())

    def test_hill_rejects_singular(self):
        with self.assertRaises(ValueError):
            hill("ABCD", [[2, 4], [1, 2]])

    def test_hill_roundtrip_and_composition(self):
        rng = random.Random(3)
        M1, M2 = rand_hill(2, rng), rand_hill(2, rng)
        s = PL[:100]
        self.assertEqual(hill(hill(s, M1), M2), hill(s, (M2 @ M1) % 26))
        self.assertEqual(hill(hill(s, M1), M1, True), s)

    def test_gl_order(self):
        self.assertEqual(gl_mod26_order(2), 157248)
        self.assertAlmostEqual(gl_mod26_order(3) / 1.63e12, 1.0, places=2)

    def test_transposition_and_adfgvx(self):
        perm = [2, 0, 3, 1, 4]
        s = PL[:100]
        self.assertEqual(transposition(transposition(s, perm), perm, True), s)
        with self.assertRaises(ValueError):
            transposition("ABC", [0, 0, 1])
        sq = adfgvx_square(random.Random(5))
        self.assertEqual(adfgvx_dec(adfgvx(s, sq, [2, 0, 1]), sq, [2, 0, 1], len(s)), s)

    def test_xor_roundtrip(self):
        self.assertEqual(xor_decrypt(xor_cipher(PL, "KEY"), "KEY"), PL)


class AnalysisTests(unittest.TestCase):
    def test_entropy_ioc(self):
        self.assertAlmostEqual(entropy("AB"), 1.0)
        self.assertEqual(ioc("A"), 0.0)
        self.assertAlmostEqual(ioc("AAAA"), 1.0)

    def test_ngram_edge(self):
        self.assertEqual(len(ngram_counter("AB", 3)), 0)

    def test_autocorr_short_text(self):
        self.assertEqual(autocorr("AB", 60), [0.0])
        self.assertEqual(autocorr("A", 60), [])
        self.assertIsNone(est_period([]))
        self.assertIsNone(est_period([0.1, 0.2]))

    def test_est_key_len_returns_tuple(self):
        L, sc = est_key_len("ABC")
        self.assertIsInstance(L, int)
        self.assertIn(L, sc)

    def test_friedman_depends_on_kp(self):
        ct = vigenere(PL, "KLUCZ")
        self.assertNotEqual(friedman(ct, 0.0579), friedman(ct, 0.0667))
        self.assertTrue(math.isnan(friedman(ct, 1 / 26)))

    def test_break_caesar_and_vigenere(self):
        refs = {"pl": profile(PL)}
        k, lang = break_caesar(caesar(PL, 11), refs)
        self.assertEqual((k, lang), (11, "pl"))
        key = "SZYFR"
        ct = vigenere(PL, key)
        L, _ = est_key_len(ct)
        self.assertEqual(break_vigenere(ct, L, refs)[2], key)


class PipelineTests(unittest.TestCase):
    def test_build_ciphers_deterministic(self):
        a = build_ciphers(PL, random.Random(42))
        b = build_ciphers(PL, random.Random(42))
        self.assertEqual([c.symbols for c in a], [c.symbols for c in b])

    def test_normalize(self):
        self.assertEqual(normalize("Zażółć gęślą jaźń ß"), "ZAZOLCGESLAJAZNSS")

    def test_corpus_fallback_on_empty_file(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "pl.txt").write_text("", encoding="utf-8")
            corp, src = load_corpora(d)
            self.assertIn("PROBKA", src["pl"])
            self.assertGreater(len(corp["pl"]), 100)

    def test_full_run_consistent_tables(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(main(["--out", d, "--texts-dir", d]), 0)
            out = Path(d)
            self.assertTrue((out / "raport_wyniki.md").is_file())
            self.assertTrue((out / "2_7_autokorelacja.png").is_file())
            # tabela 2.2 (H) i tabela 2.9 (H) musza opisywac te same szyfrogramy
            import csv
            def read(n):
                with open(out / n, encoding="utf-8") as f:
                    return list(csv.reader(f))[1:]
            t22 = {r[0]: float(r[2]) for r in read("2_2_entropia_szyfry.csv")}
            t29 = {r[0]: float(r[2]) for r in read("2_9_wskazowki.csv")}
            for name, h in t29.items():
                self.assertAlmostEqual(h, t22[name], places=2, msg=name)


if __name__ == "__main__":
    unittest.main()
