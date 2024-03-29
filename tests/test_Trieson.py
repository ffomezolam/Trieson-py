from context import Trieson
from context import Triesonode
from context import combos

import os
import unittest

import logging

class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = Trieson.Trieson(combos.none)

    def test_existence(self):
        self.assertIsInstance(self.trie, Trieson.Trieson)
        self.assertIs(self.trie._proc['proc'], combos.none)

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
        for _ in range(4):
            with self.subTest("should make full words if no prefix"):
                self.assertIn(self.trie.make(), words)

        for _ in range(4):
            with self.subTest("Should make words starting with prefix"):
                self.assertEqual('air', self.trie.make('ai'))

        for _ in range(4):
            with self.subTest("Should make words starting with prefix"):
                self.assertIn(self.trie.make('b'), [w for w in words if w.startswith('b')])

        with self.subTest("Should return empty string if prefix doesn't exist"):
            self.assertEqual('', self.trie.make('z'))

    def test_make_lookahead(self):
        words = ['ble', 'len', 'end']

        self.trie.add(words)

        with self.subTest("Lookahead should look ahead"):
            self.assertEqual(self.trie.make('bl', lookahead = 2), 'blend')

        with self.subTest("Should not allow excessive lookahead"):
            self.assertEqual('ble', self.trie.make('bl', lookahead=5))

        with self.subTest("Should adjust lookahead if fails"):
            self.assertEqual('blend', self.trie.make('b', lookahead=1))

    def test_make_max_len(self):
        words = ['bowling']

        self.trie.add(words)

        with self.subTest("Should return empty string if strict and cannot make word"):
            self.assertEqual(self.trie.make(max_len=3, strict=True), '')

        with self.subTest("fail_str should return prepended word on failure"):
            self.assertEqual(self.trie.make(max_len=3, fail_str='#', strict=True), '#bow')

        with self.subTest("Should succeed with large enough length"):
            self.assertEqual(self.trie.make(max_len=7, strict=True), 'bowling')

        with self.subTest("Should not fail if not in strict mode"):
            self.assertEqual(self.trie.make(max_len=4, strict=False), 'bowl')

    def test_make_min_len(self):
        words = ['box']

        self.trie.add(words)

        with self.subTest("Should be ok if word above min_len"):
            self.assertEqual(self.trie.make(min_len=3, strict=True), 'box')

        with self.subTest("Should fail if cannot reach min_len"):
            self.assertEqual(self.trie.make(min_len=4, strict=True), '')

        with self.subTest("Should return as is if not strict"):
            self.assertEqual(self.trie.make(min_len=4, strict=False), 'box')

    def test_make_min_max_len(self):
        words = ['box', 'boxer', 'bomb', 'bomber']

        self.trie.add(words)

        with self.subTest("Should be ok if applicable word in trie"):
            self.assertEqual(self.trie.make(min_len=4, max_len=4), 'bomb')

        with self.subTest("Min and max should be min and max"):
            self.assertIn(self.trie.make(min_len=5, max_len=4), ['bomb', 'boxer'])

        with self.subTest("Should return empty string if strict and cannot make word"):
            self.assertEqual(self.trie.make(min_len=7, max_len=9), '')

    def test_make_end_char(self):
        words = ['bandages']

        self.trie.add(words)

        with self.subTest("Should return ban with end_char n"):
            self.assertEqual(self.trie.make(end_char='n'), 'ban')

        with self.subTest("Should return bandag with end_char g"):
            self.assertEqual(self.trie.make(end_char='g'), 'bandag')

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
        self.assertEqual(self.trie._proc['proc'].__name__, 'seq_to_end')

    def test_add(self):
        ss = ['apple', 'angel', 'bagel']

        for s in ss:
            self.trie.add(s)

        for s in ss:
            for ix in range(0, -2):
                with self.subTest("Trie should contain substrings to end", s = s, ix = ix):
                    self.assertTrue(self.trie.has(s[ix:]))

            with self.subTest("All substrings should go to end of word", s = s, t=s[1:-2]):
                self.assertFalse(self.trie.has(s[1:-2]))

    def test_get_node_at_prefix(self):
        pass

    def test_has_prefix(self):
        pass

    def test_has(self):
        pass

    def test_get(self):
        pass

    def test_substrings(self):
        pass

    def test_match(self):
        pass

    def test_make(self):
        pass

    def test_make_next(self):
        pass

    def test_depth(self):
        pass

    def test_magic(self):
        with self.subTest("contains"):
            pass

        with self.subTest("getitem"):
            pass

        with self.subTest("setitem"):
            pass

        with self.subTest("len"):
            pass

        with self.subTest("iter"):
            pass

if __name__ == '__main__':
    unittest.main()
