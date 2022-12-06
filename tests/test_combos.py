from context import combos

import unittest

class Testcombos(unittest.TestCase):
    def setUp(self):
        self.seqs = ['ahoy', 'ambling', 'ambitious', 'abracadabra']

    def test_seq_all(self):
        for seq in self.seqs:
            out = list(combos.seq_all(seq))
            for combo in out:
                self.assertIn(combo, seq)

            self.assertIn(seq[-2:], out)
            self.assertIn(seq[-4:-2], out)
            self.assertIn(seq[1:4], out)

    def test_seq_to_end(self):
        for seq in self.seqs:
            out = list(combos.seq_to_end(seq))
            for combo in out:
                self.assertIn(combo, seq)

            self.assertNotIn(seq[-4:-2], out)
            self.assertIn(seq[-3:], out)
            self.assertNotIn(seq[0:3], out)
            self.assertIn(seq[0:], out)

    def test_none(self):
        for seq in self.seqs:
            out = list(combos.none(seq))
            self.assertEqual(len(out), 1)
            self.assertEqual(out[0], seq)

if __name__ == '__main__':
    unittest.main()
