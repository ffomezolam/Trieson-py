from context import Trietor
from context import items

import unittest

class TestTrietor(unittest.TestCase):
    def setUp(self):
        self.T = Trietor.Trietor()

    # --- ADD/REMOVE --------------------------------------------------------

    def test_add_single(self):
        item = items.ArbitraryItem('v', 'd', 'k')

        self.T.add(item)

        with self.subTest("length of items should be 1"):
            self.assertEqual(len(self.T._items), 1)

        with self.subTest("first entry should equal item entry"):
            self.assertEqual(self.T._items[0], item)

    def test_add_seq(self):
        titles = ['value','data','key']
        entries = 3
        itemz = [items.ArbitraryItem(*[title + str(n) for title in titles]) for n in range(entries)]

        with self.subTest("setup should be correct"):
            self.assertEqual(itemz[0].key, 'key0')
            self.assertEqual(itemz[0].value, 'value0')
            self.assertEqual(itemz[0].data, 'data0')

        with self.subTest(f"should be {entries} items to add"):
            self.assertEqual(len(itemz), entries)

        self.T.add(itemz)

        with self.subTest(f"length of Trietor should be {entries}"):
            self.assertEqual(len(self.T._items), entries)

        for i in range(entries):
            with self.subTest(f"entries should equal titles + {i}", i=i):
                item = itemz[i]
                titlez = { title: title + str(i) for title in titles }
                for title in titles:
                    self.assertEqual(getattr(item, title), titlez[title])

    def test_add_Trietor(self):
        entries = 3
        newT = Trietor.Trietor([items.ArbitraryItem(*[title + str(i) for title in ['v','d','k']]) for i in range(entries)])

        self.T.add(newT)

        with self.subTest(f'should have {entries} items'):
            self.assertEqual(len(self.T._items), entries)

        for ix, item in enumerate(self.T._items):
            with self.subTest(f'Item should have proper values'):
                self.assertEqual(item.key, 'k' + str(ix))
                self.assertEqual(item.value, 'v' + str(ix))
                self.assertEqual(item.data, 'd' + str(ix))

    def test_pop(self):
        titles = 'v', 'd', 'k'
        entries = 4

        itemz = [items.ArbitraryItem(*[title + str(n) for title in titles]) for n in range(entries)]

        self.T.add(itemz)

        with self.subTest(f"Length should be {entries}"):
            self.assertEqual(len(self.T._items), entries)

        item = self.T.pop()

        with self.subTest(f"pop() should reduce length by one"):
            self.assertEqual(len(self.T._items), entries - 1)

        with self.subTest(f"pop() should return last item"):
            self.assertEqual(item, itemz[entries - 1])

    def test__len__(self):
        entries = 3

        self.T.add([items.CharItem('c' + str(n)) for n in range(entries)])

        with self.subTest(f"__len__() should return {entries}"):
            self.assertEqual(len(self.T), entries)

    def test_copy(self):
        entries = 5
        self.T.add([items.CharItem('a' + str(n)) for n in range(entries)])

        copy = self.T.copy()

        with self.subTest("copy should be Trietor instance"):
            self.assertIsInstance(copy, Trietor.Trietor)

        with self.subTest("copy should have same length as original"):
            self.assertEqual(len(self.T), len(copy))

        for i in range(entries):
            with self.subTest("copy item should equal original item"):
                self.assertEqual(self.T._items[i], copy._items[i])

    def test_clear(self):
        entries = 4
        self.T.add([items.CharItem(str(i)) for i in range(entries)])

        with self.subTest(f'collection should have length {entries}'):
            self.assertEqual(len(self.T), entries)

        self.T.clear()

        with self.subTest(f'cleared collection should have length 0'):
            self.assertEqual(len(self.T), 0)

        with self.subTest(f'cleared collection should have 0 items'):
            self.assertEqual(len(self.T._items), 0)

    # --- DATA --------------------------------------------------------------

    def test_keys_values_data_items(self):
        k = 'abcde'
        v = range(5)
        d = range(0,10,2)

        self.T.add([items.ArbitraryItem(val, data, key) for val, data, key in zip(v,d,k)])

        with self.subTest("keys should return list of keys"):
            self.assertSequenceEqual(self.T.keys, list(k))

        with self.subTest("values should return list of values"):
            self.assertSequenceEqual(self.T.values, list(v))

        with self.subTest("data should return list of data"):
            self.assertSequenceEqual(self.T.data, list(d))

        with self.subTest("items should return list of items"):
            self.assertSequenceEqual(self.T.items, [items.ArbitraryItem(val, data, key) for val, data, key in zip(v,d,k)])

    def test__getitem__(self):
        self.T.add([items.CharItem(c) for c in 'value vim'])

        with self.subTest("should be able to get items by index"):
            self.assertEqual(self.T[0], Trietor.Trietor(items.CharItem('v')))

        with self.subTest("should be able to get items by slice"):
            self.assertEqual(self.T[1:3], Trietor.Trietor([items.CharItem(c) for c in 'al']))

        with self.subTest("should be able to get items by key"):
            self.assertEqual(self.T['v'], Trietor.Trietor([items.CharItem(c) for c in 'vv']))

    def test_has_key_value_data_item(self):
        self.T.add([items.ArbitraryItem(v, d, k) for k, v, d in zip('value', 'apple', 'bored')])

        with self.subTest("should fail if key not in collection"):
            self.assertFalse(self.T.has_key('m'))

        with self.subTest("should succeed if key in collection"):
            self.assertTrue(self.T.has_key('v'))

        with self.subTest("should fail if value not in collection"):
            self.assertFalse(self.T.has_value('m'))

        with self.subTest("should succeed if value in collection"):
            self.assertTrue(self.T.has_value('p'))

        with self.subTest("should fail if data not in collection"):
            self.assertFalse(self.T.has_data('a'))

        with self.subTest("should succeed if data in collection"):
            self.assertTrue(self.T.has_data('b'))

        with self.subTest("should fail if item not in collection"):
            self.assertFalse(self.T.has_item(items.ArbitraryItem('z', 'b', 'v')))

        with self.subTest("should succeed if item in collection"):
            self.assertTrue(self.T.has_item(items.ArbitraryItem('a', 'b', 'v')))

    def test__len__(self):
        self.T.add([items.CharItem(c) for c in 'char'])
        self.assertEqual(len(self.T), 4)

    def test__eq__(self):
        self.T.add([items.ArbitraryItem({ c: 1, 'r': 2 }) for c in 'happy'])
        newT = Trietor.Trietor([items.ArbitraryItem({c:1, 'r':2}) for c in 'happy'])
        difT = Trietor.Trietor([items.ArbitraryItem({ c: 1, 'r': 2}) for c in 'dappy'])

        with self.subTest("collections with same keys, values, data, and order are equal"):
            self.assertEqual(self.T, newT)

        with self.subTest("collections with different items are not equal"):
            self.assertNotEqual(self.T, difT)

    def test_bool_implicit(self):
        with self.subTest("empty object should return False"):
            self.assertFalse(bool(self.T))

        with self.subTest("non-empty object should return True"):
            self.assertTrue(bool(self.T.add(items.CharItem('c'))))

    # --- STRING REP --------------------------------------------------------

    def test_as_str(self):
        n = 10

        for i in range(n):
            self.T.add(items.ArbitraryItem(i, i*10, str(i)))

        with self.subTest("as_str should return concatenated keys"):
            self.assertEqual(self.T.as_str(), ''.join(str(x) for x in range(n)))

if __name__ == "__main__":
    unittest.main()
