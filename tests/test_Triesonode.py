from context import Triesonode, items

import unittest

class Dummy:
    def __init__(self, v = ''):
        self.v = v

    def __repr__(self):
        return f'Dummy({self.v})'

    def __str__(self):
        return self.v.upper()

class TestTriesonode(unittest.TestCase):
    def setUp(self):
        self.node = Triesonode.Triesonode()

    def test__init__(self):
        tn = Triesonode.Triesonode()

        with self.subTest("no args init should create DataItem"):
            self.assertIsInstance(tn._item, items.DataItem)

        with self.subTest("no args init should have None parent"):
            self.assertIsNone(tn._parent)

    def test_add(self):
        item = items.CharItem('a')
        children = self.node.children

        # add one

        self.node.add(item)

        with self.subTest("should have key 'a'"):
            self.assertIn('a', children)

        with self.subTest("item at key 'a' should be CharItem"):
            self.assertIsInstance(children['a'].item, items.CharItem)

        with self.subTest("item at key 'a' should have value 'a'"):
            self.assertEqual(children['a'].value, 'a')

        with self.subTest("item at key 'a' should have root as parent"):
            self.assertEqual(children['a'].parent, self.node)

        # add empty node

        self.node.add()

        with self.subTest("root should have 2 children"):
            self.assertEqual(len(children), 2)

        with self.subTest("root should have empty string key"):
            self.assertIn('', children)

        with self.subTest("item at key '' should be DataItem"):
            self.assertIsInstance(children[''].item, items.DataItem)

        # add second and test chaining

        node = self.node.add(item, chain=True)

        with self.subTest("root should have 2 children"):
            self.assertEqual(len(children), 2)

        with self.subTest("node at key 'a' should have count 2"):
            self.assertEqual(children['a'].count, 2)

        with self.subTest("chain=True should return new node"):
            self.assertIs(children['a'], node)

        # add third and test no chaining

        node = self.node.add(item, chain=False)

        with self.subTest("chain=False should return source node"):
            self.assertIs(self.node, node)

    def test_has(self):
        for c in 'abbccdefggh':
            self.node.add(items.CharItem(c))

        with self.subTest('no args should return list of items'):
            self.assertListEqual(self.node.has(), [items.CharItem(c) for c in ['a','b','c','d','e','f','g','h']])

        for c in 'ac':
            with self.subTest("should be able to test by key and item", c=c):
                self.assertTrue(self.node.has(c))
                self.assertTrue(self.node.has(items.CharItem(c)))

        with self.subTest("existing item with count should return True"):
            self.assertTrue(self.node.has('b', 2))
            self.assertTrue(self.node.has('a', -2))

        with self.subTest("non-existent item should return False"):
            self.assertFalse(self.node.has('z'))

        with self.subTest("existing item without count should return False"):
            self.assertFalse(self.node.has('g', 3))
            self.assertFalse(self.node.has('c', -1))

    def test_get_specific(self):
        chars = '122333444455555'

        for char in chars: self.node.add(items.ArbitraryItem(int(char), key=char))

        # test getting individual characters
        for i in range(1,6):
            n = self.node.get(str(i))

            with self.subTest("should be instance of Triesonode"):
                self.assertIsInstance(n, Triesonode.Triesonode)

            with self.subTest("key should be the number as a string"):
                self.assertEqual(n.key, str(i))

            with self.subTest("value should be the number as an int"):
                self.assertEqual(n.value, i)

            with self.subTest("count should equal number of occurrences"):
                self.assertEqual(n.count, i)

    def test_get_random_normal_weight(self):
        chars = '122333444455555'
        for char in chars:
            self.node.add(items.CharItem(char))

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

                with self.subTest('value should be in range'):
                    self.assertIn(n.value, [str(i) for i in range(1,6)])

                counts[int(n.value)] += 1

            for ix in range(1,6):
                if counts[ix] >= counts[ix - 1]: successes += 1

        ratio = (successes / 5) / tries

        with self.subTest(f"test ratio {ratio} should be within threshold {test_threshold}"):
            self.assertGreaterEqual(ratio, test_threshold)

    def test_get_random_equal_weight(self):
        chars = '122333444455555'
        for char in chars:
            self.node.add(items.CharItem(char))

        # Test for weight 0 (all equal)
        tries = 30
        successes = 0
        delta = 50
        test_threshold = 0.9

        for x in range(tries):
            counts = [0 for _ in range(1,6)]
            for _ in range(1000):
                n = int(self.node.get(weight=0).value)
                counts[n-1] += 1

            for ix in range(1,5):
                if (counts[ix] - delta) <= counts[ix-1] and (counts[ix] + delta) >= counts[ix-1]:
                    successes += 1

        ratio = (successes / 4) / tries
        with self.subTest(f"ratio {ratio} should be more than threshold {test_threshold}"):
            self.assertGreaterEqual(ratio, test_threshold)

    def test_get_with_exclude(self):
        for c in '123':
            self.node.add(items.CharItem(c))

        with self.subTest("excluding all should return None"):
            self.assertIsNone(self.node.get(exclude = [c for c in '123']))

        with self.subTest("excluding some should not return them"):
            self.assertEqual(self.node.get(exclude = ['1','2']).value, '3')

        with self.subTest("should work with a set"):
            self.assertEqual(self.node.get(exclude = {'1', '3'}).value, '2')

        with self.subTest("should work with Item"):
            self.assertIn(self.node.get(exclude = items.CharItem('2')).value, '13')

    @unittest.skip("testing")
    def test_traverse(self):
        words = ['acorn', 'accede', 'ascend', 'ban', 'brand', 'corn']
        for word in words:
            n = self.node
            for char in word:
                n = n.add(char, chain=True)

        joined = ''.join(words)

        for item in self.node.traverse():
            with self.subTest("item is valid", item = item):
                self.assertIn(item._value, joined)

    @unittest.skip("testing")
    def test_traverse_objects(self):
        oblist = [Dummy(i) for i in 'basic']

        n = self.node
        for ob in oblist:
            n = n.add(ob, chain=True)

        for item in self.node.traverse():
            with self.subTest('item is valid', item=item):
                self.assertIn(item._value, oblist)

    @unittest.skip("testing")
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
            with self.subTest("preprocessing function should be run on node", item = item):
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

    @unittest.skip("testing")
    def test_magic_len(self):
        chars = '12345'
        for c in chars: self.node.add(c)
        self.assertEqual(5, len(self.node))

    @unittest.skip("testing")
    def test_magic_contains(self):
        chars = ['b', Dummy('a')]
        for c in chars: self.node.add(c)

        self.assertTrue('b' in self.node)
        self.assertTrue(chars[1] in self.node)

    @unittest.skip("testing")
    def test_magic_bool(self):
        self.assertTrue(self.node)

    @unittest.skip("testing")
    def test_magic_getitem(self):
        for c in 'abcde': self.node.add(c)

        n = self.node['a']

        self.assertEqual(n._value, 'a')

    @unittest.skip("testing")
    def test_magic_iter(self):
        chars = 'abcde'
        for c in chars: self.node.add(c)

        for child in self.node:
            with self.subTest(child = child):
                self.assertIn(child._value, chars)

class TestTriesonodeTerminator(unittest.TestCase):
    def setUp(self):
        self.node = Triesonode.Triesonode(None, 'a')

    @unittest.skip("testing")
    def test_terminate(self):
        TERMINATOR = Triesonode.TERMINATOR

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

    @unittest.skip("testing")
    def test_is_terminator(self):
        self.node.terminate('boo!')

        self.assertFalse(self.node.is_terminator())
        self.assertTrue(self.node._children[''].is_terminator())

    @unittest.skip("testing")
    def test_get_terminator(self):
        self.node.terminate('boring')

        with self.subTest("Should return TriesonodeTerminator instance"):
            self.assertIsInstance(self.node.get_terminator(), Triesonode.TriesonodeTerminator)

        with self.subTest("Returned node should have correct data"):
            self.assertEqual(self.node.get_terminator().data(), 'boring')

    @unittest.skip("testing")
    def test_has_terminator(self):
        self.assertFalse(self.node.has_terminator())

        self.node.terminate('a')
        self.assertTrue(self.node.has_terminator())

if __name__ == '__main__':
    unittest.main()
