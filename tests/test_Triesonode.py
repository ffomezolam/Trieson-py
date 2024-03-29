from context import Triesonode, TriesonodeTerminator, TERMINATOR

import unittest

class TestTriesonode(unittest.TestCase):
    def setUp(self):
        self.node = Triesonode()

    def test_existence(self):
        self.assertIsInstance(self.node, Triesonode)

    def test_add_single(self):
        child = self.node.add('a')

        with self.subTest(child = child):
            self.assertEqual(child._value, 'a')
            self.assertEqual(child._parent, self.node)
            self.assertEqual(len(self.node), 1)
            self.assertEqual(child._count, 1)

        child = self.node.add('b')

        with self.subTest(child = child):
            self.assertEqual(len(self.node), 2)
            self.assertEqual(child._count, 1)

        child = self.node.add('b')

        with self.subTest(child = child):
            self.assertEqual(len(self.node), 2)
            self.assertEqual(child._count, 2)

    def test_add_mult(self):
        self.node.add('ccdddeeee')

        self.assertIn('c', self.node._children)
        self.assertEqual(self.node._children['c']._count, 2)
        self.assertIn('d', self.node._children)
        self.assertEqual(self.node._children['d']._count, 3)
        self.assertIn('e', self.node._children)
        self.assertEqual(self.node._children['e']._count, 4)

    def test_add_chain(self):
        # test chaining
        word = 'argument'

        n = self.node
        for char in word:
            n = n.add(char, chain=True)

        n = self.node
        for char in word:
            with self.subTest(char = char):
                self.assertIn(char, n._children)
                n = n._children[char]
                self.assertEqual(n._value, char)

    def test_has(self):
        self.node.add('abbccdefggh')
        self.assertTrue(self.node.has('a'))
        self.assertTrue(self.node.has('b', 2))
        self.assertTrue(self.node.has('c'))
        self.assertTrue(self.node.has('a', -2))
        self.assertFalse(self.node.has('z'))
        self.assertFalse(self.node.has('g', 3))
        self.assertFalse(self.node.has('c', -1))

    def test_get(self):
        self.node.add('122333444455555')

        # test getting individual characters
        for i in range(1,6):
            with self.subTest(i = i):
                n = self.node.get(str(i))

                self.assertIsInstance(n, Triesonode)
                self.assertEqual(n._value, str(i))
                self.assertEqual(n._count, i)

        # test getting random characters
        # in each instance I'm generating a probability of success based on
        # multiple tries, and comparing it to an arbitrary threshold to
        # determine if the test succeeds

        # Test for standard weight
        tries = 20
        successes = 0
        test_threshold = 0.9

        for x in range(tries):
            counts = [0 for _ in range(6)]
            for _ in range(1000):
                n = self.node.get()

                self.assertIn(n._value, [str(i) for i in range(1,6)])
                counts[int(n._value)] += 1

            for ix in range(1,6):
                if counts[ix] >= counts[ix - 1]: successes += 1

        ratio = (successes / 5) / tries
        self.assertGreaterEqual(ratio, test_threshold)

        # Test for weight 0 (all equal)
        tries = 30
        successes = 0
        delta = 50
        test_threshold = 0.9

        for x in range(tries):
            counts = [0 for _ in range(6)]
            for _ in range(1000):
                n = int(self.node.get(weight=0)._value)
                counts[n] += 1

            for ix in range(2,6):
                if (counts[ix] - delta) <= counts[ix-1] and (counts[ix] + delta) >= counts[ix-1]:
                    successes += 1

        ratio = (successes / 4) / tries
        self.assertGreaterEqual(ratio, test_threshold)

    def test_get_with_exclude(self):
        self.node.add('123')

        with self.subTest("excluding all should return None"):
            self.assertIsNone(self.node.get(exclude_chars = '123'))

        with self.subTest("excluding some should not return them"):
            self.assertEqual(self.node.get(exclude_chars = '12')._value, '3')

        with self.subTest("should work with a set"):
            self.assertEqual(self.node.get(exclude_chars = {'1', '3'})._value, '2')

        with self.subTest("should work with a list"):
            self.assertEqual(self.node.get(exclude_chars = ['2','3'])._value, '1')

    def test_data(self):
        chars = 'abcde'
        data = '54321'
        self.node.add(chars)
        for ix, char in enumerate(chars):
            n = self.node.get(char)
            n.data(data[ix])

        for ix, char in enumerate(chars):
            with self.subTest("should set data", ix = ix, char = char):
                n = self.node.get(char)
                self.assertIsInstance(n, Triesonode)
                self.assertEqual(n.data(), data[ix])

        for ix, char in enumerate(chars):
            with self.subTest("passing a function should change data"):
                n = self.node.get(char)
                def inc(n):
                    return int(n) + 1
                n.data(inc)
                self.assertEqual(n.data(), int(data[ix]) + 1)

    def test_children(self):
        chars = 'abccde'
        self.node.add(chars)
        children = self.node.children()

        self.assertIsInstance(children, list)

        for child in children:
            with self.subTest(child = child):
                self.assertIsInstance(child, Triesonode)
                self.assertIn(child._value, chars)
                if(child._value == 'c'):
                    self.assertEqual(child._count, 2)

    def test_parent(self):
        chars = 'abc'
        self.node.add(chars)
        children = self.node.children()

        self.assertIsNone(self.node.parent())
        for child in children:
            with self.subTest(child = child):
                self.assertIs(child.parent(), self.node)

    def test_traverse(self):
        words = ['acorn', 'accede', 'ascend', 'ban', 'brand', 'corn']
        for word in words:
            n = self.node
            for char in word:
                n = n.add(char, chain=True)

        joined = ''.join(words)

        for item in self.node.traverse():
            with self.subTest(item = item):
                self.assertIn(item._value, joined)

    def test_traverse_proc(self):
        word = 'apple'
        n = self.node
        for char in word:
            n = n.add(char, chain=True)

        # test pre-processing
        tester = ''
        def preproc(node):
            nonlocal tester
            tester = node._value.upper()

        for item in self.node.traverse(preproc):
            with self.subTest(item = item):
                self.assertEqual(tester, item._value.upper())

        # test pre- and post-processing
        tester = ''
        def preproc(node):
            nonlocal tester
            tester += node._value

        def postproc(node):
            nonlocal tester
            tester += node._value

        out = [n._value for n in self.node.traverse(preproc, postproc)]
        self.assertEqual(''.join(out), 'apple')
        self.assertEqual(tester, 'appleelppa')

    def test_magic_len(self):
        chars = '12345'
        self.node.add(chars)
        self.assertEqual(5, len(self.node))

    def test_magic_contains(self):
        chars = 'abcde'
        self.node.add(chars)
        self.assertTrue('b' in self.node)

    def test_magic_bool(self):
        self.assertTrue(self.node)

    def test_magic_getitem(self):
        self.node.add('abcde')
        n = self.node['a']
        self.assertEqual(n._value, 'a')

    def test_magic_iter(self):
        chars = 'abcde'
        self.node.add(chars)
        for child in self.node:
            with self.subTest(child = child):
                self.assertIn(child._value, chars)

class TestTriesonodeTerminator(unittest.TestCase):
    def setUp(self):
        self.node = Triesonode(None, 'a')

    def test_terminate(self):
        self.node.terminate('boo!')
        with self.subTest("Should have a terminating key"):
            self.assertIn(TERMINATOR, self.node._children)

        with self.subTest("Should set data"):
            self.assertEqual(self.node._children[TERMINATOR].data(), 'boo!')

        with self.subTest("Should increment count"):
            self.assertEqual(self.node._children[TERMINATOR]._count, 1)

        self.node.terminate('bah')

        with self.subTest("Should increment count again"):
            self.assertEqual(self.node._children[TERMINATOR]._count, 2)

        with self.subTest("Should replace data"):
            self.assertEqual(self.node._children[TERMINATOR].data(), 'bah')

    def test_is_terminator(self):
        self.node.terminate('boo!')

        self.assertFalse(self.node.is_terminator())
        self.assertTrue(self.node._children[''].is_terminator())

    def test_get_terminator(self):
        self.node.terminate('boring')

        with self.subTest("Should return TriesonodeTerminator instance"):
            self.assertIsInstance(self.node.get_terminator(), TriesonodeTerminator)

        with self.subTest("Returned node should have correct data"):
            self.assertEqual(self.node.get_terminator().data(), 'boring')

    def test_has_terminator(self):
        self.assertFalse(self.node.has_terminator())

        self.node.terminate('a')
        self.assertTrue(self.node.has_terminator())

if __name__ == '__main__':
    unittest.main()
