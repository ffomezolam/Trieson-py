from context import Trieson
from context import Triesonode
from context import combos

import unittest

class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = Trieson.Trieson(combos.none)

    def test_existence(self):
        self.assertIsInstance(self.trie, Trieson.Trieson)
        self.assertIs(self.trie._proc, combos.none)

    def test_add(self):
        s = 'apple'
        self.trie.add(s)
        n = self.trie._root
        self.assertIsInstance(n, Triesonode)
        self.assertTrue(n.has(s[0]))
        self.assertFalse(n.has(s[1]))

        for char in s:
            with self.subTest(char = char):
                self.assertTrue(n.has(char))
                n = n.get(char)
                self.assertIsInstance(n, Triesonode)

        s2 = 'acorn'
        self.trie.add(s2)
        n = self.trie._root
        self.assertEqual(n.get(s2[0])._count, 2)

        for char in s2:
            with self.subTest(char = char):
                self.assertTrue(n.has(char))
                n = n.get(char)

        ss = ['amble', 'able']
        self.trie.add(ss)
        for s in ss:
            n = self.trie._root

            for char in s:
                with self.subTest(char = char):
                    self.assertTrue(n.has(char))
                    n = n.get(char)

    def test_has_prefix(self):
        words = ['apple', 'apiary', 'append', 'baby', 'bonus', 'colab']
        self.trie.add(words)
        self.assertTrue(self.trie.has_prefix('app'))
        self.assertTrue(self.trie.has_prefix('ba'))
        self.assertFalse(self.trie.has_prefix('bond'))
        self.assertFalse(self.trie.has_prefix('zom'))

    def test_has(self):
        ss = ['apple', 'acorn']
        for s in ss:
            self.trie.add(s)

        for s in ss:
            with self.subTest(s = s):
                self.assertTrue(self.trie.has(s))

        self.assertFalse(self.trie.has('amble'))

    def test_get(self):
        ss = {
            'apple': 'fruit',
            'acorn': 'nut',
            'alice': 'name'
        }

        for k, v in ss.items():
            self.trie.add(k, v)

        for k, v in ss.items():
            with self.subTest(k = k, v = v):
                self.assertEqual(self.trie.get(k), v)

        for k in ss.keys():
            with self.subTest(k = k):
                self.assertFalse(self.trie.get(k[:3]))

    def test_substrings(self):
        words = ['apple', 'apiary', 'applicable', 'ambient', 'amuse', 'broken']
        self.trie.add(words)
        result = self.trie.substrings('a', 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'pple')

        result = self.trie.substrings('ap')
        self.assertEqual(len(result), 3)
        for item in result:
            with self.subTest(item = item):
                self.assertIn(item, [w[2:] for w in words if w.startswith('ap')])

        result = self.trie.substrings('brok')
        self.assertEqual(result[0], 'en')

    def test_match(self):
        words = ['apple', 'apiary', 'append', 'absolute', 'abhor', 'baby']
        self.trie.add(words)

        matches = self.trie.match('ap')
        self.assertEqual(len(matches), 3)
        for match in matches:
            with self.subTest(match = match):
                self.assertIn(match, [w for w in words if w.startswith('ap')])

        matches = self.trie.match('ab')
        self.assertEqual(len(matches), 2)

        matches = self.trie.match('a', 2)
        self.assertEqual(len(matches), 2)
        for match in matches:
            with self.subTest(match = match):
                self.assertIn(match, [w for w in words if w.startswith('a')])

    def test_make(self):
        words = ['any', 'and', 'arm', 'are', 'air', 'ago', 'age', 'bon', 'bog']
        self.trie.add(words)
        for _ in range(5):
            self.assertIn(self.trie.make(), words)

        for _ in range(10):
            self.assertEqual('air', self.trie.make('ai'))

        for _ in range(10):
            self.assertIn(self.trie.make('b'), [w for w in words if w.startswith('b')])

    def test_depth(self):
        self.trie.add('abba')
        self.assertEqual(self.trie.depth(), 4)
        self.trie.add('abbalicious')
        self.assertGreater(self.trie.depth(), 4)

    def test_magic_contains(self):
        words = ['apple', 'cucumber', 'parrot']
        self.trie.add(words)
        for word in words:
            with self.subTest(word = word):
                self.assertIn(word, self.trie)

        self.assertNotIn('wombat', self.trie)

    def test_magic_getitem(self):
        words = ['apple', 'cucumber', 'wombat']
        data = ['baseball', 'basketball', 'foosball']
        for i in range(3):
            word = words[i]
            datum = data[i]
            self.trie.add(word, datum)

        for i, word in enumerate(words):
            datum = data[i]
            with self.subTest(datum = datum, word = word):
                self.assertEqual(datum, self.trie[word])

    def test_magic_setitem(self):
        items = {
            'apple': 'crunchy',
            'orange': 'citrusy',
            'blueberry': 'blue',
            'lime': 'sour'
        }
        for k, v in items.items():
            self.trie[k] = v

        for k, v in items.items():
            with self.subTest(k = k, v = v):
                self.assertEqual(self.trie.get(k), v)

    def test_magic_len(self):
        words = ['apple', 'apiary', 'ghost', 'morph', 'solo', 'apple']
        self.trie.add(words)
        self.assertEqual(len(self.trie), 5)

    def test_magic_iter(self):
        words = ['boring', 'almost', 'tryagain', 'maybenexttime', 'oops']
        self.trie.add(words)
        for word in self.trie:
            with self.subTest(word = word):
                self.assertIn(word, words)

class TestTrieson(unittest.TestCase):
    """
    Quick added test to make sure alternate seq_to_end combo works as expected
    with the Trie.
    """
    def setUp(self):
        self.trie = Trieson.Trieson() # default seq_to_end combos

    def test_proc(self):
        self.assertEqual(self.trie._proc.__name__, 'seq_to_end')

    def test_add(self):
        ss = ['apple', 'angel', 'bagel']

        for s in ss:
            self.trie.add(s)

        for s in ss:
            for ix in range(0, -2):
                with self.subTest(s = s, ix = ix):
                    self.assertTrue(self.trie.has(s[ix:]))

            with self.subTest(s = s):
                self.assertFalse(self.trie.has(s[1:-2]))

if __name__ == '__main__':
    unittest.main()
