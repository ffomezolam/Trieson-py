""" Trieson.py
--------------
Trie class
"""

from .Triesonode import Triesonode
from . import combos

#--- CLASS DEFINITION -------------------------------------------------------
class Trieson():
    "Trie class"

#--- CONSTRUCTOR ------------------------------------------------------------
    def __init__(self, proc=None):
        self._root = Triesonode()
        self._depth = 0
        self.dict = set()
        self._proc = proc or combos.seq_to_end

#--- GET/SET/QUERY METHODS --------------------------------------------------
    def add(self, string, data=True, proc=None):
        """
        Add string(s) to Trie, associate with data.

        Can pass a list of strings or a single string. `proc` argument
        will preprocess each string, and must return a string or list
        of strings to add.
        """
        # default proc if none
        proc = self._proc if not proc else proc

        # convert to list input
        if type(string) == str: string = [string]

        # add to dict
        for s in string: self.dict.add(s)

        # apply proc function
        string = [ps for s in string for ps in proc(s)]

        # add characters for each string
        for s in string:
            node = self._root

            depth = 0
            for c in s:
                node = node.add(c)
                depth += 1

            node.data(data)
            if depth > self._depth: self._depth = depth

        return self

    def _get_node_at_prefix(self, prefix: str, proc = None):
        "Get node corresponding to final charachter of prefix"

        if not prefix: return self._root

        # start at root node
        node = self._root

        # traverse trie
        for char in prefix:
            node = node[char]
            if not node: return None
            if proc: proc(node)

        return node

    def has_prefix(self, prefix):
        "Check for any sequence of characters in Trie"
        return bool(self._get_node_at_prefix(prefix))

    def has(self, string):
        "See if string is in Trie"

        node = self._root
        for char in string:
            node = node[char]
            if not node:
                return False

        if node.data is not None:
            return True
        else:
            return False

    def get(self, string=None):
        "Get data associated with string"

        if not string: return self.make()

        # get node at conclusion of string
        node = self._get_node_at_prefix(string)

        if not node: return None

        # only full string has data
        if not node.data(): return None

        return node.data()

    def substrings(self, prefix=None, limit=None):
        "Collect and return all substrings"
        string = ''
        collection = []
        count = 0
        limit = limit if limit else 0
        root = self._get_node_at_prefix(prefix) if prefix else self._root

        # preprocessing function to add letter to string and check for word
        def preproc(node):
            nonlocal string, collection, count
            string += node._value

            if node.data():
                collection.append(string)
                count += 1

        # postprocessing function to remove letter from string
        def postproc(node):
            nonlocal string
            string = string[:-1]

        for _ in root.traverse(preproc, postproc):
            if limit and count >= limit: break

        return collection

    def match(self, string, limit=None):
        "Get possible matches to string, max <limit>"
        if not self.has_prefix(string): return [string]

        return [string + sub for sub in self.substrings(string, limit)]

    def make(self, prefix = None, weight = 1):
        "Make a random word"
        word = []

        def proc(node):
            nonlocal word
            word.append(node._value)

        node = self._get_node_at_prefix(prefix, proc)

        while True:
            node = node.get(weight = weight)
            if not node: break
            word.append(node._value)

        return ''.join(word)

    def depth(self):
        return self._depth

    def __contains__(self, string):
        "Check if string in Trie"
        return self.has(string)

    def __getitem__(self, string):
        "Get data associated with string. Alias for get(string)"
        return self.get(string)

    def __setitem__(self, string, data):
        "Add item to Trie and associate with data"
        self.add(string, data)

    def __len__(self):
        "Get number of full strings in Trie"
        return len(self.dict)

    def __iter__(self):
        "Iterate through all strings in Trie"
        for s in self.substrings():
            yield s
