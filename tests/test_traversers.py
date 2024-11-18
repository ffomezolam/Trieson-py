from context import Triesonode, traversers, items

import unittest

class TestTriesonode(unittest.TestCase):
    def setUp(self):
        self.node = Triesonode.Triesonode()
        self.letters = set()

        self.words = ['and', 'any', 'annoy', 'andrew', 'anywhere', 'android', 'ants', 'bot']

        for word in self.words:
            node = self.node

            for c in word:
                node = node.add(c)
                self.letters.add(c)

    def test_CallableTraverser(self):
        CT = traversers.CallableTraverser

        def callable(node):
            return node.value.upper()

        t = CT(callable)

        for c in self.node.traverse(t):
            with self.subTest("result should be in set of letters"):
                self.assertIn(c.lower(), self.letters)

            with self.subTest("should return result of callable", c=c):
                self.assertTrue(c.isupper())

    def test_NodeTraverser(self):
        NT = traversers.NodeTraverser

        t = NT()

        for node in self.node.traverse(t):
            with self.subTest("result should be of type Triesonode"):
                self.assertIsInstance(node, Triesonode.Triesonode)

            with self.subTest("node value should be in set of letters"):
                self.assertIn(node.value, self.letters)

    def test_SequenceTraverser(self):
        ST = traversers.SequenceTraverser

        test_success = ['an', 'bot', 'anno', 'and', 'anywhere', 'ant','a']
        test_fail = ['droid', 'drew', 'angle', 'annoys', 'bottom', 'r', '']

        for test in test_success:
            t = ST(test)

            result = list(self.node.traverse(t))
            with self.subTest("final item in traversal should not be None"):
                self.assertIsNotNone(result[-1])

            with self.subTest("returned string should match success string"):
                self.assertIn(''.join([n.value for n in result]), test_success)

        for test in test_fail:
            t = ST(test)

            result = list(self.node.traverse(t))

            with self.subTest("final item in traversal should be None"):
                self.assertIsNone(result[-1] if result else None)

    def test_RandomTraverser(self):
        RT = traversers.RandomTraverser

        runs = 10
        results = set()

        t = RT()

        for run in range(runs):
            result = ''.join(node.value for node in list(self.node.traverse(t)))
            results.add(result)

            with self.subTest("result should be in word list"):
                self.assertIn(result, self.words)

        with self.subTest("should get more than one word"):
            self.assertGreater(len(results), 1)

if __name__ == '__main__':
    unittest.main()
