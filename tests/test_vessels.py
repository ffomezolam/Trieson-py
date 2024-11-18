from context import vessels

import unittest

class TestVessel(unittest.TestCase):
    def test_init_none(self):
        i = vessels.Vessel()

        with self.subTest("key should be empty string"):
            self.assertEqual(i.key, str(None))

        with self.subTest("value should be None"):
            self.assertIsNone(i.value)

        with self.subTest("data should be None"):
            self.assertIsNone(i.data)

    def test_value(self):
        i = vessels.Vessel('a')
        j = vessels.Vessel(['value'])

        with self.subTest("key should equal string value"):
            self.assertEqual(i.key, 'a')

        with self.subTest("key should be string of value"):
            self.assertEqual(j.key, str(j.value))

    def test_data(self):
        d1 = 1
        d2 = lambda x: x + 1

        i = vessels.Vessel('a', d1)

        with self.subTest("data should store exactly"):
            self.assertEqual(i.data, d1)

        with self.subTest("data should be manipulable by callable"):
            i.data = d2
            self.assertEqual(i.data, d1 + 1)

        with self.subTest("data should be deletable"):
            del i.data
            self.assertIsNone(i.data)

    def test_getters(self):
        i = vessels.Vessel(1, 'data')

        with self.subTest("key should return key"):
            self.assertEqual(i.key, "1")

        with self.subTest("k should return key"):
            self.assertEqual(i.k, "1")

        with self.subTest("value should return value"):
            self.assertEqual(i.value, 1)

        with self.subTest("v should return value"):
            self.assertEqual(i.v, 1)

        with self.subTest("data should return data"):
            self.assertEqual(i.data, 'data')

        with self.subTest("d should return data"):
            self.assertEqual(i.d, 'data')

    def test_equality(self):
        i1 = vessels.Vessel(1, 'd1')
        i2 = vessels.Vessel(1, 'd2')
        i3 = vessels.Vessel(2, 'd3')

        self.assertEqual(i1, i2)
        self.assertNotEqual(i1, i3)

class TestVesselCache(unittest.TestCase):
    def test(self):
        c = vessels.VesselCache()

        i1k = 'a'
        i1 = vessels.Vessel(i1k)
        i2k = 'b'
        i2 = vessels.Vessel(i2k)

        c.add(i1)

        with self.subTest('item should exist in cache'):
            self.assertEqual(c.get(i1k), i1)

        with self.subTest('item count should be 1'):
            self.assertEqual(c.count(i1k), 1)

        c.add(i1)

        with self.subTest('item count should be 2'):
            self.assertEqual(c.count(i1k), 2)

        c.add(i2)

        with self.subTest('new item should exist in cache'):
            self.assertEqual(c.get(i2k), i2)

        with self.subTest('new item count should be 1'):
            self.assertEqual(c.count(i2k), 1)

        with self.subTest('old item count should be 2'):
            self.assertEqual(c.count(i1k), 2)

        # test `in`

        with self.subTest(f'{i1k} should exist in cache'):
            self.assertTrue(i1 in c)

        with self.subTest(f'{i2k} should exist in cache'):
            self.assertTrue(i2k in c)

        with self.subTest('non-existent-string should not exist in cache'):
            self.assertFalse('non-existent-string' in c)

class TestVesselFactory(unittest.TestCase):
    def test_with_cache(self):
        f = vessels.VesselFactory()

        i1 = f.create('a')

        with self.subTest("cache should have 1 item"):
            self.assertEqual(f.cache.count(), 1)

        i2 = f.create('a')

        with self.subTest("cache should still have 1 item"):
            self.assertEqual(f.cache.count(), 1)

        i3 = f.create('b')

        with self.subTest("cache should have 2 vessels"):
            self.assertEqual(f.cache.count(), 2)

        with self.subTest("data argument should replace item data"):
            i4 = f.create('b', 'data')
            self.assertEqual(i4.data, 'data')

        with self.subTest("no data argument should retain item data"):
            i5 = f.create('b')
            self.assertEqual(i5.data, 'data')

        with self.subTest("should be able to call instance as shorthand"):
            i6 = f('b')
            i7 = f.create('b')
            self.assertEqual(i6, i7)

if __name__ == "__main__":
    unittest.main()
