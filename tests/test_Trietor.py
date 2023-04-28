from context import Trietor

from types import GeneratorType

import unittest

class TestTrietor(unittest.TestCase):
    def setUp(self):
        self.T = Trietor()

    def test_add_single(self):
        item = ['key', 'value', 'data']

        self.T.add(*item)

        with self.subTest("length of each entry should be 1"):
            self.assertEqual(len(self.T._keys), 1)
            self.assertEqual(len(self.T._values), 1)
            self.assertEqual(len(self.T._data), 1)

        with self.subTest("first entry should equal item entry"):
            self.assertEqual(self.T._keys[0], item[0])
            self.assertEqual(self.T._values[0], item[1])
            self.assertEqual(self.T._data[0], item[2])

    def test_add_mult(self):
        titles = ['key','value','data']
        entries = 3
        items = [[title + str(n) for title in titles] for n in range(entries)]

        with self.subTest("setup should be correct"):
            self.assertEqual(items[0][0], 'key0')
            self.assertEqual(items[0][1], 'value0')
            self.assertEqual(items[0][2], 'data0')

        with self.subTest(f"should be {entries} items to add"):
            self.assertEqual(len(items), entries)

        self.T.add(items)

        with self.subTest(f"length of each entry should be {entries}"):
            self.assertEqual(len(self.T._keys), entries)
            self.assertEqual(len(self.T._values), entries)
            self.assertEqual(len(self.T._data), entries)

        for i in range(entries):
            with self.subTest(f"entries should equal titles + {i}", i=i):
                self.assertEqual(self.T._keys[i], items[i][0])
                self.assertEqual(self.T._values[i], items[i][1])
                self.assertEqual(self.T._data[i], items[i][2])

    def test_pop(self):
        titles = 'key', 'value', 'data'
        entries = 4

        items = [[title + str(n) for title in titles] for n in range(entries)]

        self.T.add(items)

        with self.subTest(f"Length should be {entries}"):
            self.assertEqual(len(self.T), entries)

        item = self.T.pop()

        with self.subTest(f"pop() should reduce length by one"):
            self.assertEqual(len(self.T), entries - 1)

        with self.subTest(f"pop() should return last item"):
            self.assertSequenceEqual(item, [title + str(entries - 1) for title in titles])

    def test_data_retrieval(self):
        titles = 'key','value','data'
        entries = 4
        items = [[title + str(n) for title in titles] for n in range(entries)]

        self.T.add(items)

        for method in 'keys','values','data','items':
            m = getattr(self.T, method)

            with self.subTest(f"{method}() without index should return generator"):
                self.assertIsInstance(m(), GeneratorType)

            with self.subTest(f"{method}() should return items in _{method}"):
                if method != 'items':
                    items = getattr(self.T, '_' + method)
                    self.assertSequenceEqual(list(m()), items)

            for ix in range(entries):
                with self.subTest(f"{method}({ix}) with index should return item at index {ix}"):
                    if method != 'items':
                        items = getattr(self.T, '_' + method)
                        self.assertEqual(m(ix), items[ix])

    def test_termination(self):
        self.T.add('key', 'value', 'data')

        with self.subTest("by default terminating data should be None"):
            self.assertIsNone(self.T._term)

        with self.subTest("has_terminator() should be False if data is None"):
            self.assertFalse(self.T.has_terminator())

        with self.subTest("terminate() should add terminating data"):
            self.T.terminate("OK")
            self.assertEqual(self.T._term, "OK")

        with self.subTest("has_terminator() should be True if data is not None"):
            self.assertTrue(self.T.has_terminator())

        with self.subTest("terminator() should return terminating data"):
            self.assertEqual(self.T.terminator(), "OK")

    def test_as_str(self):
        n = 10

        for i in range(n):
            self.T.add(str(i), i, i*10)

        with self.subTest("as_str should return concatenated keys"):
            self.assertEqual(self.T.as_str(), ''.join(str(x) for x in range(n)))

    def test__add__(self):
        t1 = Trietor([('key1', 'value1', 'data1')], 'term1')
        t2 = Trietor([('key2', 'value2', 'data2')], 'term2')

        tadd = t1 + t2

        with self.subTest("length should be combined length"):
            self.assertEqual(len(tadd), len(t1) + len(t2))

        with self.subTest("terminal data should come from right operand"):
            self.assertEqual(tadd._term, t2._term)

        with self.subTest("keys should be concatenated"):
            self.assertSequenceEqual(tadd._keys, t1._keys + t2._keys)

        with self.subTest("values should be concatenated"):
            self.assertSequenceEqual(tadd._values, t1._values + t2._values)

        with self.subTest("data should be concatenated"):
            self.assertSequenceEqual(tadd._data, t1._data + t2._data)

    def test_magic(self):
        titles = 'key','value','data'
        entries = 4
        items = [[title + str(n) for title in titles] for n in range(entries)]

        self.T.add(items)

        # __len__
        with self.subTest(f"__len__() should return {entries}"):
            self.assertEqual(len(self.T), entries)

        # __getitem__
        for n in range(entries):
            with self.subTest(f"__getitem__() should return item at index {n}"):
                self.assertSequenceEqual(self.T[n], [title + str(n) for title in titles])

        # __iter__
        with self.subTest(f"__iter__() should return generator"):
            self.assertIsInstance(self.T.__iter__(), GeneratorType)

        for count, item in enumerate(self.T):
            with self.subTest(f"__iter__() should iterate over {item}"):
                self.assertSequenceEqual(item, [title + str(count) for title in titles])

    def test_bool_implicit(self):
        with self.subTest("empty object should return False"):
            self.assertFalse(bool(Trietor()))

        with self.subTest("non-empty object should return True"):
            self.assertTrue(bool(Trietor([('k','v','d')])))


if __name__ == "__main__":
    unittest.main()
