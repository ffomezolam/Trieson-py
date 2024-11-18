from context import Vein
from context import items

import unittest

class TestVein(unittest.TestCase):
    def setUp(self):
        self.T = Vein.Vein()

    # --- ADD/REMOVE --------------------------------------------------------

    def test_add_single(self):
        item = items.Item('v')

        self.T.add(item)

        with self.subTest("length of items should be 1"):
            self.assertEqual(len(self.T._items), 1)

        with self.subTest("first entry should equal item entry"):
            self.assertEqual(self.T._items[0], item)

    def test_add_seq(self):
        titles = ['value','data']
        entries = 3
        itemz = [items.Item(*[title + str(n) for title in titles]) for n in range(entries)]

        with self.subTest("setup should be correct"):
            self.assertEqual(itemz[0].key, 'value0')
            self.assertEqual(itemz[0].value, 'value0')
            self.assertEqual(itemz[0].data, 'data0')

        with self.subTest(f"should be {entries} items to add"):
            self.assertEqual(len(itemz), entries)

        self.T.add(itemz)

        with self.subTest(f"length of Vein should be {entries}"):
            self.assertEqual(len(self.T._items), entries)

        for i in range(entries):
            with self.subTest(f"entries should equal titles + {i}", i=i):
                item = itemz[i]
                self.assertEqual(item.key, 'value' + str(i))
                self.assertEqual(item.value, 'value' + str(i))
                self.assertEqual(item.data, 'data' + str(i))

    def test_add_Vein(self):
        entries = 3
        newT = Vein.Vein([items.Item(*[title + str(i) for title in ['v','d']]) for i in range(entries)])

        self.T.add(newT)

        with self.subTest(f'should have {entries} items'):
            self.assertEqual(len(self.T._items), entries)

        for ix, item in enumerate(self.T._items):
            with self.subTest(f'Item should have proper values'):
                self.assertEqual(item.key, 'v' + str(ix))
                self.assertEqual(item.value, 'v' + str(ix))
                self.assertEqual(item.data, 'd' + str(ix))

    def test_pop(self):
        titles = 'v', 'k'
        entries = 4

        itemz = [items.Item(*[title + str(n) for title in titles]) for n in range(entries)]

        self.T.add(itemz)

        with self.subTest(f"Length should be {entries}"):
            self.assertEqual(len(self.T._items), entries)

        item = self.T.pop()

        with self.subTest(f"pop() should reduce length by one"):
            self.assertEqual(len(self.T._items), entries - 1)

        with self.subTest(f"pop() should return last item"):
            self.assertEqual(item, itemz[entries - 1])

    def test_copy(self):
        entries = 5
        self.T.add([items.Item('a' + str(n)) for n in range(entries)])

        copy = self.T.copy()

        with self.subTest("copy should be Vein instance"):
            self.assertIsInstance(copy, Vein.Vein)

        with self.subTest("copy should have same length as original"):
            self.assertEqual(len(self.T), len(copy))

        for i in range(entries):
            with self.subTest("copy item should equal original item"):
                self.assertEqual(self.T._items[i], copy._items[i])

    def test_clear(self):
        entries = 4
        self.T.add([items.Item(str(i)) for i in range(entries)])

        with self.subTest(f'collection should have length {entries}'):
            self.assertEqual(len(self.T), entries)

        self.T.clear()

        with self.subTest(f'cleared collection should have length 0'):
            self.assertEqual(len(self.T), 0)

        with self.subTest(f'cleared collection should have 0 items'):
            self.assertEqual(len(self.T._items), 0)

    # --- DATA --------------------------------------------------------------

    def test_keys_values_data_items(self):
        v = range(5)
        d = range(0,10,2)
        keys = [str(n) for n in v]

        self.T.add([items.Item(val, data) for val, data in zip(v,d)])

        with self.subTest("keys should return list of keys"):
            self.assertSequenceEqual(self.T.keys, keys)

        with self.subTest("values should return list of values"):
            self.assertSequenceEqual(self.T.values, list(v))

        with self.subTest("data should return list of data"):
            self.assertSequenceEqual(self.T.data, list(d))

        with self.subTest("items should return list of items"):
            self.assertSequenceEqual(self.T.items, [items.Item(val, data) for val, data in zip(v,d)])

    def test__getitem__(self):
        self.T.add([items.Item(c) for c in 'value vim'])

        with self.subTest("should be able to get items by index"):
            self.assertEqual(self.T[0], Vein.Vein(items.Item('v')))

        with self.subTest("should be able to get items by slice"):
            self.assertEqual(self.T[1:3], Vein.Vein([items.Item(c) for c in 'al']))

        with self.subTest("should be able to get items by key"):
            self.assertEqual(self.T['v'], Vein.Vein([items.Item(c) for c in 'vv']))

    def test_has_key_value_data_item(self):
        self.T.add([items.Item(v, d) for v, d in zip('apple', 'bored')])

        with self.subTest("should fail if key not in collection"):
            self.assertFalse(self.T.has_key('m'))

        with self.subTest("should succeed if key in collection"):
            self.assertTrue(self.T.has_key('p'))

        with self.subTest("should fail if value not in collection"):
            self.assertFalse(self.T.has_value('m'))

        with self.subTest("should succeed if value in collection"):
            self.assertTrue(self.T.has_value('p'))

        with self.subTest("should fail if data not in collection"):
            self.assertFalse(self.T.has_data('a'))

        with self.subTest("should succeed if data in collection"):
            self.assertTrue(self.T.has_data('b'))

        with self.subTest("should fail if item not in collection"):
            self.assertFalse(self.T.has_item(items.Item('z', 'b')))

        with self.subTest("should succeed if item in collection"):
            self.assertTrue(self.T.has_item(items.Item('a', 'b')))

    def test__len__(self):
        self.T.add([items.Item(c) for c in 'char'])
        self.assertEqual(len(self.T), 4)

    def test__eq__(self):
        self.T.add([items.Item({ c: 1, 'r': 2 }) for c in 'happy'])
        newT = Vein.Vein([items.Item({c:1, 'r':2}) for c in 'happy'])
        difT = Vein.Vein([items.Item({ c: 1, 'r': 2}) for c in 'dappy'])

        with self.subTest("collections with same keys, values, data, and order are equal"):
            self.assertEqual(self.T, newT)

        with self.subTest("collections with different items are not equal"):
            self.assertNotEqual(self.T, difT)

    def test_bool_implicit(self):
        with self.subTest("empty object should return False"):
            self.assertFalse(bool(self.T))

        with self.subTest("non-empty object should return True"):
            self.T.add(items.Item('c'))
            self.assertTrue(bool(self.T))

    # --- STRING REP --------------------------------------------------------

    def test_as_str(self):
        n = 10

        for i in range(n):
            self.T.add(items.Item(i, str(i)))

        with self.subTest("as_str should return concatenated keys"):
            self.assertEqual(self.T.as_str(), ''.join(str(x) for x in range(n)))

    def test__str__(self):
        n = 10

        for i in range(n): self.T.add(items.Item(i))

        with self.subTest("str() should return concatenated keys"):
            self.assertEqual(str(self.T), ''.join(str(x) for x in range(n)))

if __name__ == "__main__":
    unittest.main()
