from context import Triesonode

import unittest

class Dummy:
    def __init__(self, v = ''):
        self.v = v

    def __repr__(self):
        return f'Dummy({self.v})'

    def __str__(self):
        return self.v

class TestTriesonode(unittest.TestCase):
    def setUp(self):
        self.root = Triesonode.Triesonode()

    @unittest.skip("test")
    def test_add(self):
        item_str = 'a'
        item_obj = Dummy('b')
        item_num = 1

        children = self.root.children

        # add one

        self.root.add(item_str)

        with self.subTest('should have 1 child'):
            self.assertEqual(1, len(children))

        with self.subTest("should have key 'a'"):
            self.assertIn('a', children)

        with self.subTest("item with key 'a' should have value 'a'"):
            self.assertEqual(children['a'].value, 'a')

        with self.subTest("item at key 'a' should have root as parent"):
            self.assertEqual(children['a'].parent, self.root)

        # add terminating (empty) node

        self.root.add()

        with self.subTest("root should have 2 children"):
            self.assertEqual(len(children), 2)

        with self.subTest("root should have empty string key"):
            self.assertIn('', children)

        with self.subTest("node should have None for value/data"):
            self.assertIsNone(children[''].value)
            self.assertIsNone(children[''].data)

        # add second and test chaining

        node = self.root.add(item_str, chain=True)

        with self.subTest("root should have 2 children"):
            self.assertEqual(len(children), 2)

        with self.subTest("node at key 'a' should have count 2"):
            self.assertEqual(children['a'].count, 2)

        with self.subTest("chain=True should return new node"):
            self.assertIs(children['a'], node)

        # add third and test no chaining

        node = self.root.add(item_str, chain=False)

        with self.subTest("chain=False should return source node"):
            self.assertIs(self.root, node)

        # add non-string node

        self.root.add(item_obj)

        with self.subTest("object should generate key from string rep"):
            self.assertIn('b', children)
            self.assertEqual('b', children['b'].key)

        with self.subTest("node value should be object"):
            self.assertIs(children['b'].value, item_obj)

        self.root.add(item_num)

        with self.subTest("node value should be number"):
            self.assertIs(children['1'].value, item_num)

    @unittest.skip("test")
    def test_has(self):
        with self.subTest('no children should return false'):
            self.assertFalse(self.root.has('a'))

        for c in 'abbccdefggh':
            self.root.add(c)

        with self.subTest('no args should return false'):
            self.assertFalse(self.root.has())

        for c in 'ac':
            with self.subTest("should be able to test by key and item", c=c):
                self.assertTrue(self.root.has(c))
                self.assertTrue(self.root.has(Dummy(c)))

        with self.subTest("existing item with count should return True"):
            self.assertTrue(self.root.has('b', 2))
            self.assertTrue(self.root.has('a', -2))

        with self.subTest("non-existent item should return False"):
            self.assertFalse(self.root.has('z'))

        with self.subTest("existing item without count should return False"):
            self.assertFalse(self.root.has('g', 3))
            self.assertFalse(self.root.has('c', -1))

    @unittest.skip("test")
    def test_get_specific(self):
        chars = '122333444455555'

        for char in chars: self.root.add(int(char))

        # test getting individual numbers
        for i in range(1,6):
            n = self.root.get(str(i))

            with self.subTest("should be instance of Triesonode"):
                self.assertIsInstance(n, Triesonode.Triesonode)

            with self.subTest("key should be the number as a string"):
                self.assertEqual(n.key, str(i))

            with self.subTest("value should be the number as an int"):
                self.assertEqual(n.value, i)

            with self.subTest("count should equal number of occurrences"):
                self.assertEqual(n.count, i)

    @unittest.skip("test")
    def test_get_random_normal_weight(self):
        chars = '122333444455555'
        for char in chars:
            self.root.add(char)

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
                n = self.root.get()

                with self.subTest('value should be in range'):
                    self.assertIn(n.value, [str(i) for i in range(1,6)])

                counts[int(n.value)] += 1

            for ix in range(1,6):
                if counts[ix] >= counts[ix - 1]: successes += 1

        ratio = (successes / 5) / tries

        with self.subTest(f"test ratio {ratio} should be within threshold {test_threshold}"):
            self.assertGreaterEqual(ratio, test_threshold)

    @unittest.skip("test")
    def test_get_random_equal_weight(self):
        chars = '122333444455555'
        for char in chars:
            self.root.add(char)

        # Test for weight 0 (all equal)
        tries = 30
        successes = 0
        delta = 50
        test_threshold = 0.9

        for x in range(tries):
            counts = [0 for _ in range(1,6)]
            for _ in range(1000):
                n = int(self.root.get(weight=0).value)
                counts[n-1] += 1

            for ix in range(1,5):
                if (counts[ix] - delta) <= counts[ix-1] and (counts[ix] + delta) >= counts[ix-1]:
                    successes += 1

        ratio = (successes / 4) / tries
        with self.subTest(f"ratio {ratio} should be more than threshold {test_threshold}"):
            self.assertGreaterEqual(ratio, test_threshold)

    @unittest.skip("test")
    def test_get_with_exclude(self):
        for c in '123':
            self.root.add(c)

        with self.subTest("excluding all should return None"):
            self.assertIsNone(self.root.get(exclude = [c for c in '123']))

        with self.subTest("excluding some should not return them"):
            self.assertEqual(self.root.get(exclude = ['1','2']).value, '3')

        with self.subTest("should work with a set"):
            self.assertEqual(self.root.get(exclude = {'1', '3'}).value, '2')

        with self.subTest("should work with Item"):
            self.assertIn(self.root.get(exclude = '2').value, '13')

    @unittest.skip("test")
    def test_magic_len(self):
        chars = '12345'
        for c in chars: self.root.add(c)
        self.assertEqual(5, len(self.root))

    @unittest.skip("test")
    def test_magic_contains(self):
        chars = ['b', Dummy('a')]
        for c in chars: self.root.add(c)

        for c in chars:
            with self.subTest(f'{c} is in node'):
                self.assertTrue(c in self.root)

    @unittest.skip("test")
    def test_magic_bool(self):
        self.assertTrue(self.root)

    @unittest.skip("test")
    def test_magic_getitem(self):
        for c in 'abcde': self.root.add(c)

        n = self.root['a']

        self.assertEqual(n.value, 'a')

    @unittest.skip("test")
    def test_magic_iter(self):
        chars = 'abcde'
        for c in chars: self.root.add(c)

        for child in self.root:
            with self.subTest(child = child):
                self.assertIn(child.value, chars)

class TestTriesonodeTerminator(unittest.TestCase):
    def setUp(self):
        self.node = Triesonode.Triesonode(None, 'a')

    @unittest.skip("test")
    def test_terminate(self):
        TERMINATOR = Triesonode.LEAF_KEY

        self.node.terminate('boo!')

        with self.subTest("Should have a terminating key"):
            self.assertIn(TERMINATOR, self.node._children)

        with self.subTest("Should set data"):
            self.assertEqual(self.node._children[TERMINATOR].data, 'boo!')

        with self.subTest("Should increment count"):
            self.assertEqual(self.node._children[TERMINATOR]._count, 1)

        self.node.terminate('bah')

        with self.subTest("Should increment count again"):
            self.assertEqual(self.node._children[TERMINATOR]._count, 2)

        with self.subTest("Should replace data"):
            self.assertEqual(self.node._children[TERMINATOR].data, 'bah')

        with self.subTest("Should be able to adjust data"):
            self.node.terminate(lambda x: x.upper())
            self.assertEqual(self.node._children[TERMINATOR].data, 'BAH')

    @unittest.skip("test")
    def test_is_terminator(self):
        self.node.terminate('boo!')

        self.assertFalse(self.node.is_terminator())
        self.assertTrue(self.node._children[''].is_terminator())

    @unittest.skip("test")
    def test_get_terminator(self):
        self.node.terminate('boring')

        with self.subTest("Should return TriesonodeTerminator instance"):
            self.assertIsInstance(self.node.get_terminator(), Triesonode.TriesonodeTerminator)

        with self.subTest("Returned node should have correct data"):
            self.assertEqual(self.node.get_terminator().data, 'boring')

    @unittest.skip("test")
    def test_has_terminator(self):
        self.assertFalse(self.node.has_terminator())

        self.node.terminate('a')
        self.assertTrue(self.node.has_terminator())

if __name__ == '__main__':
    unittest.main()
