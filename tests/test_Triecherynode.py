from context import Triecherynode, is_primitive, as_key

import itertools

import unittest

class Dummy:
    def __init__(self, v = 'dummy'):
        self.v = v
        self.l = [v]

    def __repr__(self):
        return f'{self.v}'

    def __str__(self):
        return f'Dummy({self.v})'

    def rev(self):
        return reversed(self.v)

class TestHelpers(unittest.TestCase):
    def test_is_primitive(self):
        with self.subTest('integer should return True'):
            self.assertTrue(is_primitive(1))

        with self.subTest('string should return True'):
            self.assertTrue(is_primitive('1'))

        with self.subTest('float should return True'):
            self.assertTrue(is_primitive(2.5))

        with self.subTest('bool should return True'):
            self.assertTrue(is_primitive(False))

        with self.subTest('class should return False'):
            self.assertFalse(is_primitive(Dummy))

        with self.subTest('instance should return False'):
            d = Dummy(1)
            self.assertFalse(is_primitive(d))

    def test_as_key(self):
        i = Dummy(1)
        f = Dummy(1.5)
        s = Dummy('1')
        b = Dummy(False)

        with self.subTest('int should return int'):
            self.assertEqual(as_key(1), 1)

        with self.subTest('float should return float'):
            self.assertEqual(as_key(1.5), 1.5)

        with self.subTest('string should return string'):
            self.assertEqual(as_key('1'), '1')

        with self.subTest('bool should return bool'):
            self.assertEqual(as_key(False), False)

        with self.subTest('instance of int should return repr()'):
            self.assertEqual(as_key(i), '1')

        with self.subTest('instance of float should return repr()'):
            self.assertEqual(as_key(f), '1.5')

        with self.subTest('instance of string should return repr()'):
            self.assertEqual(as_key(s), '1')

        with self.subTest('instance of bool should return repr()'):
            self.assertEqual(as_key(b), 'False')

class TestTriecherynode(unittest.TestCase):
    def setUp(self):
        self.node = Triecherynode()

    def test_existence(self):
        self.assertIsInstance(self.node, Triecherynode)

    def test_add_single(self):
        hellodummy = Dummy('hello')
        child = self.node.add(hellodummy)

        with self.subTest(child = child):
            self.assertEqual(child._value, 'hello')
            self.assertEqual(child._item, hellodummy)
            self.assertEqual(child._parent, self.node)
            self.assertEqual(len(self.node), 1)
            self.assertEqual(child._count, 1)

        child = self.node.add(Dummy('bye'))

        with self.subTest(child = child):
            self.assertEqual(len(self.node), 2)
            self.assertEqual(child._count, 1)

        child = self.node.add(hellodummy)

        with self.subTest(child = child):
            self.assertEqual(len(self.node), 2)
            self.assertEqual(child._count, 2)

    def test_add_chain(self):
        # test chaining
        items = [Dummy('a'), Dummy('b'), Dummy('c')]

        n = self.node
        for item in items:
            n = n.add(item, chain=True)

        n = self.node
        for item in items:
            with self.subTest(item = item):
                self.assertIn(item.__repr__(), n._children)
                n = n._children[item.__repr__()]
                self.assertEqual(n._item, item)

    def test_add_primitive(self):
        items = ['a', 1, True]

        for item in items:
            self.node.add(item)

        self.assertIn('a', self.node._children)
        self.assertIn(1, self.node._children)
        self.assertIn(True, self.node._children)

    def test_has(self):
        a = Dummy('a')
        b = Dummy('b')
        c = Dummy('c')
        d = Dummy('d')
        e = Dummy('e')
        f = Dummy('f')

        items = [a,b,b,c,c,d,e, 'a']

        for item in items:
            self.node.add(item)

        self.assertTrue(self.node.has(a))
        self.assertTrue(self.node.has(b, 2))
        self.assertTrue(self.node.has(c))
        self.assertTrue(self.node.has(a, -2))
        self.assertTrue(self.node.has('a'))
        self.assertFalse(self.node.has(f))
        self.assertFalse(self.node.has(c, 3))
        self.assertFalse(self.node.has(c, -1))

    def test_get_specific(self):
        a = Dummy(1)
        b = Dummy(2)
        c = Dummy(3)
        d = Dummy(4)
        e = Dummy('e')

        obs = [a,b,c,d,e]
        items = [a,b,b,c,c,c,d,d,d,d,e,e,e,e,e]

        for item in items:
            self.node.add(item)

        # test getting individual characters
        for i in range(5):
            with self.subTest(i = i):
                n = self.node.get(obs[i])

                self.assertIsInstance(n, Triecherynode)
                self.assertEqual(n._item, obs[i])
                self.assertEqual(n._count, i+1)

    def test_get_normal_weight(self):
        # test getting random characters.
        # in each instance I'm generating a probability of success based on
        # multiple tries, and comparing it to an arbitrary threshold to
        # determine if the test succeeds. not totally sophisticated but gets
        # the most basic job done
        # TODO: can test actual ratios between the various key counts to see
        # if they approximate the proportions of items added

        values = [1,2,3,4,'e']
        obs = {str(k): Dummy(k) for k in values}

        items = itertools.chain.from_iterable([[obs[str(values[i])]] * (i + 1) for i in range(len(values))])

        for item in items:
            self.node.add(item)

        tries = 20
        successes = 0
        test_threshold = 0.9

        for x in range(tries):
            # keep tally of counts
            counts = { str(k): 0 for k in values }

            # run get 1000 times and keep tally of each value we get
            for _ in range(1000):
                n = self.node.get()

                self.assertIn(n._value, [str(v) for v in values])
                counts[n._value] += 1

            # if counts increase by key then it's a success
            scounts = 0
            for ix in range(1,5):
                key = str(values[ix])
                pkey = str(values[ix - 1])
                if counts[key] >= counts[pkey]:
                    scounts += 1

            if scounts >= 4:
                successes += 1

        # final ratio is number of successful tries over total tries
        ratio = successes / tries

        self.assertGreaterEqual(ratio, test_threshold)

    def test_get_equal_weight(self):
        # Test for weight 0 (all equal)
        # The method is a bit unsophisticated but gets the point across. I'm
        # testing for how varied the counts are for each key compared to the
        # previous key and if they are under an arbitrary threshold then I
        # consider that attempt a success. A certain number of successes is good
        # enough for me.

        values = [1,2,3,4,'e']
        obs = {str(k): Dummy(k) for k in values}

        items = itertools.chain.from_iterable([[obs[str(values[i])]] * (i + 1) for i in range(len(values))])

        for item in items:
            self.node.add(item)

        tries = 20
        successes = 0
        delta = 35
        test_threshold = 0.6

        for x in range(tries):
            # keep tally of counts
            counts = { str(k): 0 for k in values }

            # run get 1000 times and keep tally of each value we get
            for _ in range(1000):
                n = self.node.get(weight=0)

                self.assertIn(n._value, [str(v) for v in values])
                counts[n._value] += 1

            # if counts are about equal then it's a success
            scounts = 0
            for ix in range(1,5):
                key = str(values[ix])
                pkey = str(values[ix - 1])
                if counts[key] + delta >= counts[pkey] and counts[key] - delta <= counts[pkey]:
                    scounts += 1

            if scounts >= 4:
                successes += 1

        # final ratio is number of successful tries over total tries
        ratio = successes / tries

        self.assertGreaterEqual(ratio, test_threshold)

    def test_get_with_exclude(self):
        items = [Dummy(1), Dummy(2), Dummy(3)]

        for item in items:
            self.node.add(item)

        with self.subTest("excluding all should return None"):
            self.assertIsNone(self.node.get(exclude_items = items))

        with self.subTest("excluding some should not return them"):
            self.assertEqual(self.node.get(exclude_items = items[:2])._item, items[2])

        with self.subTest("should work with a set"):
            self.assertEqual(self.node.get(exclude_items = {items[0], items[2]})._item, items[1])

    def test_data(self):
        items = [Dummy(1), Dummy(2), Dummy(3)]
        data = '321'

        for item in items:
            self.node.add(item)

        for ix, item in enumerate(items):
            n = self.node.get(item)
            # set data for node
            n.data(data[ix])

        for ix, item in enumerate(items):
            with self.subTest("should set data", ix = ix, item = item):
                n = self.node.get(item)
                self.assertIsInstance(n, Triecherynode)
                self.assertEqual(n.data(), data[ix])

        for ix, item in enumerate(items):
            with self.subTest("passing a function should change data"):
                n = self.node.get(item)
                def inc(n):
                    return int(n) + 1
                n.data(inc)
                self.assertEqual(n.data(), int(data[ix]) + 1)

    def test_children(self):
        items = [Dummy(i) for i in range(3)]
        items.append(Dummy(0))

        for item in items:
            self.node.add(item)

        children = self.node.children()

        self.assertIsInstance(children, list)

        for child in children:
            with self.subTest("children should be Triecherynode instance", child = child):
                self.assertIsInstance(child, Triecherynode)
            with self.subTest("children should have correct items"):
                self.assertIn(child._item, items)
                if(child._item == Dummy(0)):
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
                n = n.add(Dummy(char), chain=True)

        joined = ''.join(words)

        for item in self.node.traverse():
            with self.subTest(item = item):
                self.assertIn(item._value, joined)

    def test_traverse_proc(self):
        word = 'apple'
        n = self.node
        for char in word:
            n = n.add(Dummy(char), chain=True)

        # test pre-processing
        tester = ''
        def preproc(node):
            nonlocal tester
            tester = node._item.v.upper()

        for item in self.node.traverse(preproc):
            with self.subTest(item = item):
                self.assertEqual(tester, item._item.v.upper())

        # test pre- and post-processing
        tester = ''
        def preproc(node):
            nonlocal tester
            tester += node._item.v

        def postproc(node):
            nonlocal tester
            tester += node._item.v

        out = [n._item.v for n in self.node.traverse(preproc, postproc)]
        self.assertEqual(''.join(out), 'apple')
        self.assertEqual(tester, 'appleelppa')

    def test_magic_len(self):
        chars = '12345'
        for char in chars:
            self.node.add(Dummy(char))
        self.assertEqual(5, len(self.node))

    def test_magic_contains(self):
        chars = 'abcde'
        for char in chars:
            self.node.add(Dummy(char))
        self.assertTrue(Dummy('b') in self.node)

    def test_magic_bool(self):
        self.assertTrue(self.node)

    def test_magic_getitem(self):
        for char in 'abcde':
            self.node.add(Dummy(char))
        n = self.node[Dummy('a')]
        self.assertEqual(n._item.v, 'a')

    def test_magic_iter(self):
        chars = 'abcde'
        for char in chars:
            self.node.add(Dummy(char))

        for child in self.node:
            with self.subTest(child = child):
                self.assertIn(child._item.v, chars)

if __name__ == '__main__':
    unittest.main()
