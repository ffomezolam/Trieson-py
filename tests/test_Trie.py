from context import Trie

import unittest

class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = Trie.Trie()

    def test_add(self):
        self.trie.add('apple')

        with self.subTest("root should have 1 child"):
            self.assertEqual(len(self.trie._root._children), 1)

        node = self.trie._root

        for char in 'apple':
            self.assertIn(char, node._children)
            node = node.get(char)

    def test_match(self):
        words = ['apple', 'boston']
        for word in words:
            self.trie.add(word)

        with self.subTest("Should return all if no prefix"):
            self.assertListEqual(self.trie.match(), words)

        for word in words:
            prefix = word[0]
            with self.subTest("Should limit return if prefix"):
                self.assertListEqual(self.trie.match(prefix), [word])

if __name__ == '__main__':
    unittest.main()
