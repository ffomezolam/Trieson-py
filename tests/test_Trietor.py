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

    def test_as_str(self):
        n = 10

        for i in range(n):
            self.T.add(str(i), i, i*10)

        with self.subTest("as_str should return concatenated keys"):
            self.assertEqual(self.T.as_str(), ''.join(str(x) for x in range(n)))

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

if __name__ == "__main__":
    unittest.main()
