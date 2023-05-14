from context import items

import unittest

class TestDataItem(unittest.TestCase):
    def setUp(self):
        self.data = True
        self.item = items.DataItem(self.data)

    def test(self):
        with self.subTest("key should be None"):
            self.assertIsNone(self.item.key)

        with self.subTest("value should be None"):
            self.assertIsNone(self.item.value)

        with self.subTest("data should be set"):
            self.assertEqual(self.item.data, self.data)

class TestCharItem(unittest.TestCase):
    def setUp(self):
        self.inputs = ['a', 'baby', 1]

    def test(self):
        for s in self.inputs:
            i = items.CharItem(s)

            with self.subTest("should add first character of input to key"):
                self.assertEqual(i.key, str(s)[0])

            with self.subTest("should add first character of input to value"):
                self.assertEqual(i.value, str(s)[0])

class TestStringItem(unittest.TestCase):
    def setUp(self):
        self.inputs = ['a', 'baby', 1, 3.14]

    def test(self):
        for s in self.inputs:
            i = items.StringItem(s)

            with self.subTest("should add full string to key"):
                self.assertEqual(i.key, str(s))

            with self.subTest("should add full string to value"):
                self.assertEqual(i.value, str(s))

class TestArbitraryItem(unittest.TestCase):
    def setUp(self):
        self.inputs = ['a', 'string', (1,2,3)]
        self.keys = ['k1', 'k2', 'k3']
        self.key_funcs = [lambda x: x.upper(), lambda x: x.title(), lambda x: str(max(x))]

    def test_default_key(self):
        for s in self.inputs:
            i = items.ArbitraryItem(s)

            with self.subTest("should add input to value"):
                self.assertEqual(i.value, s)

            with self.subTest("should generate key from __str__"):
                self.assertEqual(i.key, str(s))

    def test_specified_key(self):
        for s, k in zip(self.inputs, self.keys):
            i = items.ArbitraryItem(s, key=k)

            with self.subTest("should add input to value"):
                self.assertEqual(i.value, s)

            with self.subTest("should set key"):
                self.assertEqual(i.key, k)

    def test_key_func(self):
        for s, f in zip(self.inputs, self.key_funcs):
            i = items.ArbitraryItem(s, key=f)

            with self.subTest("should add input to value"):
                self.assertEqual(i.value, s)

            with self.subTest("should generate key from function"):
                self.assertEqual(i.key, f(s))

if __name__ == "__main__":
    unittest.main()
