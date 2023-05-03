from context import Triesonode

import unittest

class Dummy:
    def __init__(self, v = ''):
        self.v = v

    def __repr__(self):
        return f'Dummy({self.v})'

class TestHelpers(unittest.TestCase):
    def test_is_primitive(self):
        is_primitive = Triesonode.is_primitive

        with self.subTest('int should return True'):
            self.assertTrue(is_primitive(1))

        with self.subTest('float should return True'):
            self.assertTrue(is_primitive(1.1))

        with self.subTest('string should return True'):
            self.assertTrue(is_primitive('string'))

        with self.subTest('bool should return True'):
            self.assertTrue(is_primitive(False))

        with self.subTest('list should return false'):
            self.assertFalse(is_primitive([1,2]))

        with self.subTest('dict should return false'):
            self.assertFalse(is_primitive({'a':1, 'b':2}))

        with self.subTest('arbitrary object should return false'):
            d = Dummy('a')
            self.assertFalse(is_primitive(d))

    def test_make_key(self):
        make_key = Triesonode.make_key

        with self.subTest('int should return str(int)'):
            self.assertEqual('1', make_key(1))

        with self.subTest('float should return str(float)'):
            self.assertEqual('1.5', make_key(1.5))

        with self.subTest('string should return string'):
            self.assertEqual('string', make_key('string'))

        with self.subTest('bool should return str(bool)'):
            self.assertEqual('False', make_key(False))

        with self.subTest('default object should return object.__repr__()'):
            self.assertEqual('Dummy(A)', make_key(Dummy('A')))

        with self.subTest('should allow custom key function'):
            self.assertEqual('a', make_key(Dummy('A'), key_func = lambda x: x.v.lower()))

class TestTriesonode(unittest.TestCase):
    def setUp(self):
        self.node = Triesonode.Triesonode()

    def test_existence(self):
        self.assertIsInstance(self.node, Triesonode.Triesonode)

    def test_add_char(self):
        # add one
        child = self.node.add('a')

        with self.subTest("should have key 'a'"):
            self.assertEqual(child._key, 'a')

        with self.subTest("should have value 'a'"):
            self.assertEqual(child._value, 'a')

        with self.subTest("should have root as parent"):
            self.assertEqual(child._parent, self.node)

        with self.subTest("root should have 1 child"):
            self.assertEqual(len(self.node._children), 1)

        with self.subTest("child should have count of 1"):
            self.assertEqual(child._count, 1)

        # test adding a second node
        child = self.node.add('b')

        with self.subTest("root child count should be 2"):
            self.assertEqual(len(self.node._children), 2)

        with self.subTest("second child should have count of 1"):
            self.assertEqual(child._count, 1)

        # add a repeat node
        child = self.node.add('b')

        with self.subTest("root child count should be 2"):
            self.assertEqual(len(self.node._children), 2)

        with self.subTest("second child should have count of 2"):
            self.assertEqual(child._count, 2)

    def test_add_chain(self):
        # test chaining
        word = 'argument'

        n = self.node
        for char in word:
            n = n.add(char, chain=True)

        n = self.node
        for char in word:
            with self.subTest(f"'{char}' should be in node children", n = n):
                self.assertIn(char, n._children)

            n = n._children[char]

            with self.subTest(f"node key should be '{char}'"):
                self.assertEqual(n._key, char)

            with self.subTest(f"node value should be '{char}'"):
                self.assertEqual(n._value, char)

    def test_add_no_chain(self):
        # test no chaining
        n = self.node.add('a', chain=False)
        with self.subTest("returned node should be the same as processed node"):
            self.assertIs(n, self.node)

    def test_add_object(self):
        a = Dummy('a')

        child = self.node.add(a)

        with self.subTest("root child count should be 1"):
            self.assertEqual(len(self.node._children), 1)

        with self.subTest("child node should have key of Dummy(a)"):
            self.assertEqual(child._key, a.__repr__())

        with self.subTest("child node value should be Dummy('a')"):
            self.assertIs(child._value, a)

        with self.subTest("child should have count of 1"):
            self.assertEqual(child._count, 1)

        # add second node
        child = self.node.add(a)

        with self.subTest("root child count should still be 1"):
            self.assertEqual(len(self.node._children), 1)

        with self.subTest("child node should have key 'Dummy(a)'", child=child):
            self.assertEqual(child._key, a.__repr__())

        with self.subTest("child at key should match child node", child=child):
            self.assertIs(self.node._children[a.__repr__()], child)

        with self.subTest("child node should have count of 2"):
            self.assertEqual(child._count, 2)

    def test_has(self):
        for c in 'abbccdefggh':
            self.node.add(c)

        with self.subTest('no args should return list of keys'):
            self.assertListEqual(self.node.has(), ['a','b','c','d','e','f','g','h'])

        with self.subTest("existing item should return True"):
            self.assertTrue(self.node.has('a'))
            self.assertTrue(self.node.has('c'))

        with self.subTest("existing item with count should return True"):
            self.assertTrue(self.node.has('b', 2))
            self.assertTrue(self.node.has('a', -2))

        with self.subTest("non-existent item should return False"):
            self.assertFalse(self.node.has('z'))

        with self.subTest("existing item without count should return False"):
            self.assertFalse(self.node.has('g', 3))
            self.assertFalse(self.node.has('c', -1))

    def test_data(self):
        chars = 'abcde'
        data = '54321'

        for c in chars:
            self.node.add(c)

        for ix, char in enumerate(chars):
            n = self.node.get(char)
            n.data(data[ix])

        for ix, char in enumerate(chars):
            n = self.node.get(char)
            with self.subTest("should be Triesonode instance"):
                self.assertIsInstance(n, Triesonode.Triesonode)

            with self.subTest("should set data", ix = ix, char = char):
                self.assertEqual(n.data(), data[ix])

        for ix, char in enumerate(chars):
            with self.subTest("passing a function should change data"):
                n = self.node.get(char)

                def inc(n):
                    return int(n) + 1

                n.data(inc)

                self.assertEqual(n.data(), int(data[ix]) + 1)

    def test_children_no_arg(self):
        chars = 'abccde'
        for char in chars: self.node.add(chars)

        children = self.node.children()

        with self.subTest('calling with no arguments should return list'):
            self.assertIsInstance(children, list)

        for child in children:
            with self.subTest('child is Triesonode instance', child = child):
                self.assertIsInstance(child, Triesonode.Triesonode)

            with self.subTest('value is valid'):
                self.assertIn(child._value, chars)

            with self.subTest('if child is "c" count should be 2'):
                if(child._value == 'c'):
                    self.assertEqual(child._count, 2)

    def test_children_str_arg(self):
        chars = 'abccde'

        for char in chars: self.node.add(char)

        child = self.node.children('c')

        with self.subTest('existing child should return Triesonode instance'):
            self.assertIsInstance(child, Triesonode.Triesonode)

        with self.subTest('key should be in children'):
            self.assertIn('c', self.node._children)
            pass

        with self.subTest('existing child should return node'):
            self.assertEqual(child.value(), 'c')
            pass

    def test_parent(self):
        chars = 'abc'

        for c in chars: self.node.add(c)

        children = self.node.children()

        self.assertIsNone(self.node.parent())

        for child in children:
            with self.subTest("parent is root", child = child):
                self.assertIs(child.parent(), self.node)

    def test_get_specific(self):
        chars = '122333444455555'

        for char in chars: self.node.add(int(char))

        # test getting individual characters
        for i in range(1,6):
            n = self.node.get(str(i))

            with self.subTest("should be instance of Triesonode"):
                self.assertIsInstance(n, Triesonode.Triesonode)

            with self.subTest("key should be the number as a string"):
                self.assertEqual(n._key, str(i))

            with self.subTest("value should be the number as an int"):
                self.assertEqual(n._value, i)

            with self.subTest("count should equal number of occurrences"):
                self.assertEqual(n._count, i)

    def test_get_specific_with_object(self):
        items = [Dummy(n) for n in range(1,6)]

        for dummy in items:
            count = 0
            for n in range(1, dummy.v + 1):
                self.node.add(dummy)
                count += 1

            self.assertEqual(n, count)

        for i in range(1,6):
            for k in (str(i), items[i-1]):
                n = self.node.get(k)

                with self.subTest("should be instance of Triesonode"):
                    #self.assertIsInstance(n, Triesonode.Triesonode)
                    pass

                with self.subTest("key should be object as a string"):
                    #self.assertEqual(n._key, str(k))
                    pass

                with self.subTest("value should be object"):
                    #self.assertEqual(n._value, chars[i-1])
                    pass

                with self.subTest("count should equal number of occurrences"):
                    #self.assertEqual(n._count, i)
                    pass

    def test_get_random_normal_weight(self):
        chars = '122333444455555'
        for char in chars:
            self.node.add(char)

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
                    self.assertIn(n._value, [str(i) for i in range(1,6)])

                counts[int(n._value)] += 1

            for ix in range(1,6):
                if counts[ix] >= counts[ix - 1]: successes += 1

        ratio = (successes / 5) / tries

        with self.subTest(f"test ratio {ratio} should be within threshold {test_threshold}"):
            self.assertGreaterEqual(ratio, test_threshold)

    def test_get_random_equal_weight(self):
        chars = '122333444455555'
        for char in chars:
            self.node.add(char)

        # Test for weight 0 (all equal)
        tries = 30
        successes = 0
        delta = 50
        test_threshold = 0.9

        for x in range(tries):
            counts = [0 for _ in range(1,6)]
            for _ in range(1000):
                n = int(self.node.get(weight=0).value())
                counts[n-1] += 1

            for ix in range(1,5):
                if (counts[ix] - delta) <= counts[ix-1] and (counts[ix] + delta) >= counts[ix-1]:
                    successes += 1

        ratio = (successes / 4) / tries
        with self.subTest(f"ratio {ratio} should be more than threshold {test_threshold}"):
            self.assertGreaterEqual(ratio, test_threshold)

    def test_get_with_objects(self):
        chars = '122333444455555'
        for char in chars:
            self.node.add(Dummy(char))

        tries = 20
        successes = 0
        test_threshold = 0.9

        for x in range(tries):
            counts = [0 for _ in range(6)]
            for _ in range(1000):
                n = self.node.get()

                with self.subTest('value should be in range'):
                    self.assertIn(n._value.v, [str(i) for i in range(1,6)])

                counts[int(n._value.v)] += 1

            for ix in range(1,6):
                if counts[ix] >= counts[ix - 1]: successes += 1

        ratio = (successes / 5) / tries

        with self.subTest(f"test ratio {ratio} should be within threshold {test_threshold}"):
            self.assertGreaterEqual(ratio, test_threshold)

    def test_get_with_exclude(self):
        for c in '123':
            self.node.add(c)

        with self.subTest("excluding all should return None"):
            self.assertIsNone(self.node.get(exclude = '123'))

        with self.subTest("excluding some should not return them"):
            self.assertEqual(self.node.get(exclude = '12')._value, '3')

        with self.subTest("should work with a set"):
            self.assertEqual(self.node.get(exclude = {'1', '3'})._value, '2')

        with self.subTest("should work with a list"):
            self.assertEqual(self.node.get(exclude = ['2','3'])._value, '1')

    def test_get_with_exclude_on_object(self):
        obs = [Dummy(i) for i in '123']
        for ob in obs:
            self.node.add(ob)

        with self.subTest("excluding all should return None"):
            self.assertIsNone(self.node.get(exclude = obs))

        with self.subTest("exclusing some should not return them"):
            self.assertEqual(self.node.get(exclude = obs[0:2])._value, obs[2])

        with self.subTest("should be able to exclude by key instead of value"):
            self.assertEqual(self.node.get(exclude = [ob.__repr__() for ob in obs[0:2]])._value, obs[2])

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

    def test_traverse_objects(self):
        oblist = [Dummy(i) for i in 'basic']

        n = self.node
        for ob in oblist:
            n = n.add(ob, chain=True)

        for item in self.node.traverse():
            with self.subTest('item is valid', item=item):
                self.assertIn(item._value, oblist)

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

    def test_magic_len(self):
        chars = '12345'
        for c in chars: self.node.add(c)
        self.assertEqual(5, len(self.node))

    def test_magic_contains(self):
        chars = ['b', Dummy('a')]
        for c in chars: self.node.add(c)

        self.assertTrue('b' in self.node)
        self.assertTrue(chars[1] in self.node)

    def test_magic_bool(self):
        self.assertTrue(self.node)

    def test_magic_getitem(self):
        for c in 'abcde': self.node.add(c)

        n = self.node['a']

        self.assertEqual(n._value, 'a')

    def test_magic_iter(self):
        chars = 'abcde'
        for c in chars: self.node.add(c)

        for child in self.node:
            with self.subTest(child = child):
                self.assertIn(child._value, chars)

class TestTriesonodeTerminator(unittest.TestCase):
    def setUp(self):
        self.node = Triesonode.Triesonode(None, 'a')

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

    def test_is_terminator(self):
        self.node.terminate('boo!')

        self.assertFalse(self.node.is_terminator())
        self.assertTrue(self.node._children[''].is_terminator())

    def test_get_terminator(self):
        self.node.terminate('boring')

        with self.subTest("Should return TriesonodeTerminator instance"):
            self.assertIsInstance(self.node.get_terminator(), Triesonode.TriesonodeTerminator)

        with self.subTest("Returned node should have correct data"):
            self.assertEqual(self.node.get_terminator().data(), 'boring')

    def test_has_terminator(self):
        self.assertFalse(self.node.has_terminator())

        self.node.terminate('a')
        self.assertTrue(self.node.has_terminator())

if __name__ == '__main__':
    unittest.main()
