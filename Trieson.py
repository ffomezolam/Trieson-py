""" Trieson.py
--------------
Trie class
"""

from TriesonHistory import TriesonHistory
from Triesonode import Triesonode
from TriesonTraveler import TriesonTraveler

#--- PROC FUNCTIONS ---------------------------------------------------------
def all_seq_combos(seq, min=2):
    """
    Get all sequential combinations of sequence. For example:
    'abcd' -> ['a','ab','abc','abcd','bc','bcd','cd','d']
    """
    slen = len(seq)
    return (seq[i:j] for i in range(slen) for j in range(i + 1, slen + 1) if (j - i) >= min)

def seq_combos(seq, min=2):
    """
    Get sequential combinations of sequence. For example:
    'abcd' -> ['abcd','bcd','cd','d']
    """
    slen = len(seq)
    return (seq[i:] for i in range(slen) if (slen - i) >= min)

def no_combos(seq):
    "Return sequence as list. For example: 'a' -> ['a']"
    return [seq]

#--- CLASS DEFINITION -------------------------------------------------------
class Trieson():
    """
    Trie Class
    add(string, [data], [proc])
    get([string])
    """

#--- CONSTRUCTOR ------------------------------------------------------------
    def __init__(self, *, opts: dict | None = None):
        self._root = Triesonode()
        self._count = 0
        self._depth = 0
        self.history = TriesonHistory()
        self.dict = set()

        self.opts = {
            'default_proc': seq_combos
        }

        self.set_opts(opts)

#--- GET/SET/QUERY METHODS --------------------------------------------------
    def add(self, string, data=True, proc=None):
        """
        Add string(s) to Trie, associate with data.

        Can pass a list of strings or a single string. `proc` argument
        will preprocess each string, and must return a string or list
        of strings to add.
        """
        # default proc if none
        proc = self.opts['default_proc'] if not proc else proc

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

            node.set_data(data)
            if depth > self._depth: self._depth = depth

        return self

    def get(self, string=None):
        "Get data associated with string"

        if not string: return self.make()

        self.history.new()

        # start at root node
        node = self._root

        # traverse trie
        for char in string:
            node = node[char]
            if node:
                self.history.add(char)
            else:
                return None

        # only full string has data
        if not node.data():
            return None

        return node.data()

    def has(self, string):
        "See if string is in Trie"

        self.history.new()

        node = self._root
        for char in string:
            node = node[char]
            if node: self.history.add(char)
            else: return False

        return True

    def match(self, string, limit=None):
        "Get possible matches to string, max <limit>"
        if string not in self: return [string]

        node = self._root
        for c in string:
            node = node.get(c)

        return [string + sub for sub in node.substrings(limit)]

    def make(self, prefix = None, w = 1):
        "Make a random word"
        node = self._root

        word = []
        while True:
            node = node.get(w=w)
            if not node: break
            print(node)
            word.append(node._value)

        return ''.join(word)

    def set_opts(self, opts: dict | None):
        "Set global instance options"
        if opts:
            for opt in opts:
                if opt in self.opts: self.opts[opt] = opts[opt]

        return self

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
        return self._count

    def __iter__(self):
        "Iterate through all strings in Trie"
        for s in self._root.substrings():
            yield s
