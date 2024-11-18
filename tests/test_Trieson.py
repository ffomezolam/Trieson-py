from context import Trieson
from context import Trietor
#from context import format_return_item_spec, get_node_attr

from context import Triesonode as TN
from context import comboster as combos

from types import GeneratorType

import os
import unittest

import logging

class Dummy:
    def __init__(self, v = 'dummy'):
        self.v = v

    def __repr__(self):
        return self.v.upper()

class TestHelpers(unittest.TestCase):
    def test_format_return_item_spec(self):
        fric = format_return_item_spec

        with self.subTest('by default should return v and False'):
            self.assertSequenceEqual(fric(), (['v'], False))

        with self.subTest('should override as_str if not returning key'):
            self.assertSequenceEqual(fric(as_str=True), (['v'], False))

        with self.subTest("should ignore invalid specifiers"):
            self.assertSequenceEqual(fric('kbvad'), (['k','v','d'], False))

        with self.subTest("should allow specifiers in any amount and order"):
            self.assertSequenceEqual(fric('KkrzvVV'), (['k','k','v','v','v'], False))

    def test_get_node_attr(self):
        node = TN.Triesonode(None, 'value', 'key', 'DATA')

        with self.subTest("should return data on spec 'd'"):
            self.assertEqual(get_node_attr('d', node), 'DATA')

        with self.subTest("should return key on spec 'k'"):
            self.assertEqual(get_node_attr('k', node), 'key')

        with self.subTest("should return value on spec 'v'"):
            self.assertEqual(get_node_attr('v', node), 'value')

@unittest.skip("unused")
class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = Trieson(combos.none)

    def test_existence(self):
        self.assertIsInstance(self.trie, Trieson)
        self.assertIs(self.trie._proc['proc'], combos.none)

    @unittest.skip("unused")
    def test_add_string(self):
        strings = ['apple', 'apply', 'apiary', 'ankle']

        for ix, string in enumerate(strings):
            # add string
            self.trie.add(string)

            n = ix + 1 # number of entries

            with self.subTest(f"root should have 1 child"):
                self.assertEqual(len(self.trie._root.children()), 1)

            with self.subTest(f"root child 'a' should have {n} count"):
                self.assertEqual(self.trie._root.children()[0]._count, n)

        # check first child
        node = self.trie._root.get('a')

        with self.subTest(f"root child 'a' should have two children"):
            self.assertEqual(len(node.children()), 2)

        for c in { w[1] for w in strings }:
            with self.subTest(f"root child 'a' should have {c}"):
                self.assertIn(c, node._children)

        # check all words
        for string in strings:
            node = self.trie._root

            for c in string:
                with self.subTest(f"node {node} should have child {c}"):
                    self.assertTrue(node.has(c))
                node = node[c]

            with self.subTest(f"final character should have terminating node"):
                self.assertTrue(node.has_terminator())

    @unittest.skip("unused")
    def test_add_object(self):
        seqs = [[Dummy(c) for c in seq] for seq in ('first', 'fight', 'father')]

        for seq in seqs: self.trie.add(seq)

        with self.subTest("root should have 'F' in child keys"):
            self.assertIn('F', self.trie._root._children)

        with self.subTest("root should have 1 child"):
            self.assertEqual(len(self.trie._root._children), 1)

        with self.subTest("first child should be Dummy instance"):
            self.assertIsInstance(self.trie._root._children['F'].value(), Dummy)

        with self.subTest("first child should have count 3"):
            self.assertEqual(3, self.trie._root._children['F']._count)

        with self.subTest("first child should have value Dummy(f)"):
            self.assertEqual(self.trie._root._children['F'].value().v, seqs[0][0].v)

        node = self.trie._root._children['F']

        with self.subTest("first child should have 2 children"):
            self.assertEqual(len(node._children), 2)

        with self.subTest("first child's children keys should be 'I' and 'A'"):
            self.assertIn('I', node._children)
            self.assertIn('A', node._children)

        for child in node._children.values():
            with self.subTest("first childs children values should be Dummy instances", child=child):
                self.assertIsInstance(child.value(), Dummy)

            with self.subTest("first childs children should have keys 'I' and 'A'"):
                self.assertIn(child.key(), 'IA')

    @unittest.skip("unused")
    def test_add_with_key_func(self):
        words = 'apple', 'approach'
        items = [[Dummy(c) for c in word] for word in words]
        key_func = lambda x: "!" + x.v.upper()

        for item in items: self.trie.add(item, key_func = key_func)

        for word in words:
            with self.subTest("key_func should convert word length to key"):
                self.assertIn(''.join("!" + c for c in word.upper()), self.trie.dict)

        with self.subTest("child keys should follow key_func"):
            self.assertEqual(self.trie._root.children()[0].key(), "!A")

    @unittest.skip("unused")
    def test__get_node_at_prefix(self):
        items = ['apple', [Dummy(c) for c in 'apiary']]

        for item in items:
            self.trie.add(item)

        with self.subTest("no argument should return root"):
            self.assertEqual(self.trie._get_node_at_prefix(), self.trie._root)

        node = self.trie._get_node_at_prefix('appl')

        with self.subTest("should return Triesonode instance"):
            self.assertIsInstance(node, TN.Triesonode)

        with self.subTest("for strings node key should equal node value should equal final character"):
            self.assertEqual(node.key(), node.value())
            self.assertEqual('l', node.key())

        # get sequence of items corresponding to 'api' prefix
        node = self.trie._get_node_at_prefix([items[1][ix] for ix in range(0,len('api'))])

        with self.subTest("for objects node value should equal object"):
            self.assertEqual(node.value(), items[1][2])

        with self.subTest("for object node key should equal __repr__()"):
            self.assertEqual(node.key(), 'I')

        # get sequence of keys that correspond to 'api' prefix
        node = self.trie._get_node_at_prefix(['A', 'P', 'I'])

        with self.subTest("trie should be traversable by key for objects"):
            self.assertEqual(node.key(), 'I')

        with self.subTest("trie traversed by key should have object as value"):
            self.assertEqual(node.value(), items[1][2])

        # get sequence that doesn't exist
        node = self.trie._get_node_at_prefix('appr')

        with self.subTest("non-existent prefix should return None"):
            self.assertIsNone(node)

    @unittest.skip("unused")
    def test_has_prefix(self):
        words = ['apple', 'apiary', 'append', 'baby', 'bonus', 'colab']
        for word in words:
            self.trie.add(word)

        with self.subTest("should have prefix app"):
            self.assertTrue(self.trie.has_prefix('app'))

        with self.subTest("should have prefix ba"):
            self.assertTrue(self.trie.has_prefix('ba'))

        with self.subTest("should not have prefix bond"):
            self.assertFalse(self.trie.has_prefix('bond'))

        with self.subTest("should not have prefix zom"):
            self.assertFalse(self.trie.has_prefix('zom'))

        obword = [Dummy(c) for c in 'crazy']
        self.trie.add(obword)

        with self.subTest("should be able to test for object prefix with keys"):
            self.assertTrue(self.trie.has_prefix('CRAZ'))

        with self.subTest("should be able to test for object prefix with object"):
            self.assertTrue(self.trie.has_prefix(obword[0:3]))

    @unittest.skip("unused")
    def test_has(self):
        ss = ['apple', 'acorn']
        for s in ss:
            self.trie.add(s)

        for s in ss:
            with self.subTest(f'should return true if {s} in trie', s = s):
                self.assertTrue(self.trie.has(s))

        with self.subTest("should return false if word not in trie"):
            self.assertFalse(self.trie.has('amble'))

        obword = [Dummy(c) for c in 'adorn']

        self.trie.add(obword)

        with self.subTest("should return true if seq in trie"):
            self.assertTrue(self.trie.has(obword))

        with self.subTest("should be able to test for seq by key sequence"):
            self.assertTrue(self.trie.has('ADORN'))

    @unittest.skip("unused")
    def test_get(self):
        ss = {
            'apple': 'fruit',
            'acorn': 'nut',
            'alice': 'name'
        }

        for k, v in ss.items():
            self.trie.add(k, v)

        with self.subTest(f'get() should return Trietor instance'):
            self.assertIsInstance(self.trie.get('apple'), Trietor)

        for k, v in ss.items():
            with self.subTest(f"Get {k} should return Trietor with terminal data {v}", k = k, v = v):
                self.assertEqual(self.trie.get(k).term_data(), v)

        for k in ss.keys():
            r = self.trie.get(k[:3])

            with self.subTest("Getting a substring should return Trietor instance"):
                self.assertIsInstance(r, Trietor)

            with self.subTest("Getting a substring should return empty collection by default", k = k):
                self.assertFalse(r)

            r = self.trie.get(k[:3], partial=True)

            with self.subTest("Getting substring with `partial` flag should return collection"):
                self.assertTrue(r)

            with self.subTest("Collection should contain substring"):
                self.assertEqual(r.as_str(), k[:3])

        ob1 = [Dummy(c) for c in 'antarctica']
        self.trie.add(ob1, 'place')

        with self.subTest("Getting by object should return Trietor with correct terminal data"):
            self.assertEqual(self.trie.get(ob1).term_data(), 'place')

        with self.subTest("Getting object by key should return Trietor with correct terminal data"):
            self.assertEqual(self.trie.get('ANTARCTICA').term_data(), 'place')

        with self.subTest("Object substring should return empty collection by default"):
            self.assertFalse(self.trie.get(ob1[:3]))

        with self.subTest("Object substring with partial should return filled collection"):
            self.assertEqual(self.trie.get(ob1[:3], partial=True).as_str(), 'ANT')

    @unittest.skip("unused")
    def test_substrings(self):
        words = ['apple', 'apiary', 'applicable', 'ambient', 'amuse', 'broken']

        for word in words: self.trie.add(word)

        result = list(self.trie.substrings('a', 1))

        with self.subTest("valid result with limit 1 should return one result"):
            self.assertEqual(len(result), 1)

        with self.subTest("valid result on 'a' with limit 1 should return 'pple'"):
            self.assertEqual(result[0].as_str(), 'pple')

        result = list(self.trie.substrings('ap'))

        with self.subTest("valid result on 'ap' should return 3 results"):
            self.assertEqual(len(result), 3)

        for item in result:
            with self.subTest(f"'ap' results should start {item}", item = item):
                self.assertIn(item.as_str(), [w[2:] for w in words if w.startswith('ap')])

        result = list(self.trie.substrings('brok'))

        with self.subTest("'brok' should yield 'en'"):
            self.assertEqual(result[0].as_str(), 'en')

    @unittest.skip("unused")
    def test_subsequences(self):
        words = ['apple', 'apiary', 'applicable', 'ambient', 'amuse', 'broken']
        obwords = [[Dummy(c) for c in word] for word in words]

        for obword in obwords: self.trie.add(obword)

        with self.subTest("valid object prefix should return valid subsequences"):
            r = list(self.trie.subsequences(obwords[5][:4]))
            self.assertSequenceEqual(list(r[0].values()), obwords[5][4:])

        with self.subTest("valid key prefix should return valid subsequences"):
            r = list(self.trie.subsequences('BROK'))
            self.assertSequenceEqual(list(r[0].values()), obwords[5][4:])

        for subseq in self.trie.subsequences('AP'):
            with self.subTest("subsequences should be of type Trietor"):
                self.assertIsInstance(subseq, Trietor)

            with self.subTest("should work with multiple subsequences", subseq=subseq):
                self.assertIn(subseq.as_str(), [word[2:].upper() for word in words if word.startswith('ap')])

    @unittest.skip("unused")
    def test_match_string(self):
        words = ['apple', 'apiary', 'append', 'absolute', 'abhor', 'baby']

        for word in words:
            self.trie.add(word)

        matches = self.trie.match('ap')

        with self.subTest("should return generator"):
            self.assertIsInstance(matches, GeneratorType)

        with self.subTest("'ap' should have 3 matches"):
            self.assertEqual(len(list(matches)), 3)

        for match in matches:
            with self.subTest("match should be in source list", match = match):
                self.assertIn(match.as_str(), [w for w in words if w.startswith('ap')])

        matches = self.trie.match('ab')

        with self.subTest("'ab' should have 2 matches"):
            self.assertEqual(len(list(matches)), 2)

        matches = self.trie.match('a', 2)

        with self.subTest("match should limit output if specified"):
            self.assertEqual(len(list(matches)), 2)

        for match in matches:
            with self.subTest("match should be in source list", match = match):
                self.assertIn(match.as_str(), [w for w in words if w.startswith('a')])

    @unittest.skip("unused")
    def test_match_object(self):
        words = ['apple', 'apiary', 'append', 'absolute', 'abhor', 'baby']
        obwords = [[Dummy(c) for c in word] for word in words]

        for word in obwords: self.trie.add(word)

        matches = self.trie.match(obwords[0][:3])

        with self.subTest("APP should have 2 matches"):
            self.assertEqual(len(list(matches)), 2)

        for match in matches:
            with self.subTest("match prefix should be APP"):
                self.assertSequenceEqual(match[:3], obwords[0][:3])

            with self.subTest("index 3 should be L or E"):
                self.assertIn(match.values()[3], [obwords[0][3], obwords[2][3]])

            with self.subTest("index 4 should be E or N"):
                self.assertIn(match.values()[4], [obwords[0][4], obwords[2][4]])

        # object key test
        matches = self.trie.match(obwords[0][:2])

        with self.subTest("AP shold have 3 matches"):
            self.assertEqual(len(list(matches)), 3)

        for match in matches:
            with self.subTest("match should be in source list"):
                self.assertIn(match.as_str(), [w.upper() for w in words if w.startswith('ap')])

    @unittest.skip("unused")
    def test_make(self):
        words = ['any', 'and', 'arm', 'are', 'air', 'ago', 'age', 'bon', 'bog']

        for word in words: self.trie.add(word)

        for _ in range(4):
            with self.subTest("should make full words if no prefix"):
                self.assertIn(self.trie.make(), words)

        for _ in range(4):
            with self.subTest("Should make words starting with prefix"):
                self.assertEqual('air', self.trie.make('ai'))

        for _ in range(4):
            with self.subTest("Should make words starting with prefix"):
                self.assertIn(self.trie.make('b'), [w for w in words if w.startswith('b')])

        with self.subTest("Should return empty string if prefix doesn't exist"):
            self.assertEqual('', self.trie.make('z'))

    @unittest.skip("unused")
    def test_make_lookahead(self):
        words = ['ble', 'len', 'end']

        self.trie.add(words)

        with self.subTest("Lookahead should look ahead"):
            self.assertEqual(self.trie.make('bl', lookahead = 2), 'blend')

        with self.subTest("Should not allow excessive lookahead"):
            self.assertEqual('ble', self.trie.make('bl', lookahead=5))

        with self.subTest("Should adjust lookahead if fails"):
            self.assertEqual('blend', self.trie.make('b', lookahead=1))

    @unittest.skip("unused")
    def test_make_max_len(self):
        words = ['bowling']

        self.trie.add(words)

        with self.subTest("Should return empty string if strict and cannot make word"):
            self.assertEqual(self.trie.make(max_len=3, strict=True), '')

        with self.subTest("fail_str should return prepended word on failure"):
            self.assertEqual(self.trie.make(max_len=3, fail_str='#', strict=True), '#bow')

        with self.subTest("Should succeed with large enough length"):
            self.assertEqual(self.trie.make(max_len=7, strict=True), 'bowling')

        with self.subTest("Should not fail if not in strict mode"):
            self.assertEqual(self.trie.make(max_len=4, strict=False), 'bowl')

    @unittest.skip("unused")
    def test_make_min_len(self):
        words = ['box']

        self.trie.add(words)

        with self.subTest("Should be ok if word above min_len"):
            self.assertEqual(self.trie.make(min_len=3, strict=True), 'box')

        with self.subTest("Should fail if cannot reach min_len"):
            self.assertEqual(self.trie.make(min_len=4, strict=True), '')

        with self.subTest("Should return as is if not strict"):
            self.assertEqual(self.trie.make(min_len=4, strict=False), 'box')

    @unittest.skip("unused")
    def test_make_min_max_len(self):
        words = ['box', 'boxer', 'bomb', 'bomber']

        self.trie.add(words)

        with self.subTest("Should be ok if applicable word in trie"):
            self.assertEqual(self.trie.make(min_len=4, max_len=4), 'bomb')

        with self.subTest("Min and max should be min and max"):
            self.assertIn(self.trie.make(min_len=5, max_len=4), ['bomb', 'boxer'])

        with self.subTest("Should return empty string if strict and cannot make word"):
            self.assertEqual(self.trie.make(min_len=7, max_len=9), '')

    @unittest.skip("unused")
    def test_make_end_char(self):
        words = ['bandages']

        self.trie.add(words)

        with self.subTest("Should return ban with end_char n"):
            self.assertEqual(self.trie.make(end_chars='n'), 'ban')

        with self.subTest("Should return bandag with end_char g"):
            self.assertEqual(self.trie.make(end_chars='g'), 'bandag')

        self.trie.add('ball')
        with self.subTest("Should allow multiple end_chars"):
            self.assertIn(self.trie.make(end_chars='nl'), ['ban', 'bal'])

    @unittest.skip("unused")
    def test_depth(self):
        self.trie.add('abba')
        self.assertEqual(self.trie.depth(), 4)
        self.trie.add('abbalicious')
        self.assertEqual(self.trie.depth(), len('abbalicious'))

    @unittest.skip("unused")
    def test_magic_contains(self):
        words = ['apple', 'cucumber', 'parrot']
        for word in words:
            self.trie.add(word)

        for word in words:
            with self.subTest(f"word {word} should be in trie", word = word):
                self.assertIn(word, self.trie)

        with self.subTest("non-existent word should not be in trie"):
            self.assertNotIn('wombat', self.trie)

    @unittest.skip("unused")
    def test_magic_getitem(self):
        words = ['apple', 'cucumber', 'wombat']
        data = ['baseball', 'basketball', 'foosball']

        for i in range(3):
            word = words[i]
            datum = data[i]
            self.trie.add(word, datum)

        for i, word in enumerate(words):
            datum = data[i]
            results = self.trie[word]

            with self.subTest("should return Trietor instance"):
                self.assertIsInstance(results, Trietor)

            with self.subTest(f"results terminating data should be {datum}"):
                self.assertEqual(results.terminator(), datum)

            with self.subTest(f"results as string should be {word}"):
                self.assertEqual(results.as_str(), word)

    @unittest.skip("unused")
    def test_magic_setitem(self):
        items = {
            'apple': 'crunchy',
            'orange': 'citrusy',
            'blueberry': 'blue',
            'lime': 'sour'
        }
        for k, v in items.items():
            self.trie[k] = v

        for k, v in items.items():
            with self.subTest(f"item {k} should have data {v}", k = k, v = v):
                self.assertEqual(self.trie.get(k).terminator(), v)

    @unittest.skip("unused")
    def test_magic_len(self):
        words = ['apple', 'apiary', 'ghost', 'morph', 'solo', 'apple']
        for word in words: self.trie.add(word)
        self.assertEqual(len(self.trie), 5)

    @unittest.skip("unused")
    def test_magic_iter(self):
        words = ['boring', 'almost', 'tryagain', 'maybenexttime', 'oops']
        for word in words: self.trie.add(word)

        for word in self.trie:
            with self.subTest("should iterate through words", word = word):
                self.assertIn(word.as_str(), words)

@unittest.skip("unused")
class TestTrieson(unittest.TestCase):
    """
    Quick added test to make sure alternate seq_to_end combo works as expected
    with the Trie.
    """
    def setUp(self):
        self.trie = Trieson() # default seq_to_end combos

    @unittest.skip("unused")
    def test_proc(self):
        self.assertEqual(self.trie._proc['proc'].__name__, 'seq_to_end')

    @unittest.skip("unused")
    def test_add(self):
        ss = ['apple', 'angel', 'bagel']

        for s in ss:
            self.trie.add(s)

        for s in ss:
            for ix in range(0, -2):
                with self.subTest("Trie should contain substrings to end", s = s, ix = ix):
                    self.assertTrue(self.trie.has(s[ix:]))

            with self.subTest("All substrings should go to end of word", s = s, t=s[1:-2]):
                self.assertFalse(self.trie.has(s[1:-2]))

    @unittest.skip("unused")
    def test_get_node_at_prefix(self):
        pass

    @unittest.skip("unused")
    def test_has_prefix(self):
        pass

    @unittest.skip("unused")
    def test_has(self):
        pass

    @unittest.skip("unused")
    def test_get(self):
        pass

    @unittest.skip("unused")
    def test_substrings(self):
        pass

    @unittest.skip("unused")
    def test_match(self):
        pass

    @unittest.skip("unused")
    def test_make(self):
        pass

    @unittest.skip("unused")
    def test_make_next(self):
        pass

    @unittest.skip("unused")
    def test_depth(self):
        pass

    @unittest.skip("unused")
    def test_magic(self):
        with self.subTest("contains"):
            pass

        with self.subTest("getitem"):
            pass

        with self.subTest("setitem"):
            pass

        with self.subTest("len"):
            pass

        with self.subTest("iter"):
            pass

if __name__ == '__main__':
    unittest.main()
