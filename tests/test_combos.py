from context import combos

import unittest

class Testcombos(unittest.TestCase):
    def setUp(self):
        self.seqs = ['ahoy', 'ambling', 'ambitious', 'abracadabra']

    def test_seq_all(self):
        for seq in self.seqs:
            out = combos.seq_all(seq)
            for combo in out:
                self.assertIn(combo, seq)

    def test_seq_to_end(self):
        for seq in self.seqs:
            out = combos.seq_to_end(seq)
            for combo in out:
                self.assertIn(combo, seq)

    def test_none(self):
        for seq in self.seqs:
            out = combos.none(seq)
            self.assertEqual(out[0], seq)

if __name__ == '__main__':
    unittest.main()
