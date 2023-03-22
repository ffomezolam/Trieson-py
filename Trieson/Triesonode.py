""" Triesonode.py
-----------------
Exports Trie Node class
"""

from __future__ import annotations
from typing import Optional
import random

###--- TRIESONODE CLASS -----------------------------------------------------

class Triesonode:
    """
    Represents a node in the Trieson trie. Contains low-level methods for
    manipulating the trie on a node-by-node basis. Includes methods for:
    - Adding child nodes
    - Getting child nodes by char
    - Checking for existence of children
    - Getting and setting node data
    """

    #--- CONSTRUCTOR --------------------------------------------------------

    def __init__(self, parent: Triesonode = None, value: str = ''):
        self._value = value
        self._count = 1
        self._children = {}
        self._parent = parent
        self._data = None

    #--- GET/SET ------------------------------------------------------------

    def add(self, char, chain=True):
        "Add char to children and return added node"

        # convenience for passing more than one char to add:
        # will add each char to this node (will return this node)
        if len(char) > 1:
            for c in char:
                self.add(c, chain=False)
            return self

        # if char already exists, increment count, else add new node
        if char in self._children:
            self._children[char]._count += 1
        else:
            self._children[char] = Triesonode(self, char)

        # return child if chaining...
        if chain: return self._children[char]

        # ... or set chain to False to get same node back
        return self

    def terminate(self, data = True):
        "Add a terminating node to children"

        # if no terminating node, create one, else update count and data
        if None not in self._children:
            self._children[None] = TriesonodeTerminator(data)
        else:
            self._children[None]._count += 1
            self._children[None].data(data)

    def get(self, char: Optional[str] = None, weight: int|float = 1,
            *,
            exclude_chars: Optional[str|list|tuple|set] = ''
    ):
        """
        Return specified child node if exists.
        If no child node specified, get a random node by relative child counts.

        Can exclude children by passing optional `exclude_chars` argument containing an iterable of characters to exclude.
        """

        # no children? return None
        if not self._children: return None

        # if no char provided, generate one selected from children
        if char == None:
            # get children that aren't excluded
            children = [childnode for childnode in self._children.values() if childnode._value not in exclude_chars]

            # return None if all are excluded or no children
            if not children: return None

            # create weights for random selection
            weights = [child._count ** weight for child in children if child._value not in exclude_chars]

            # select by weighted choice
            char = random.choices(children, weights)[0]._value

        return self._children[char] if char in self._children else None

    def has(self, char=None, n=0):
        """
        Check if child node exists. Can pass integer (positive or negative) to
        limit success to children that have at least or at most that count.

        If no char specified, get list of all child keys.
        """

        if not char: return list(self._children.keys())

        # standard return
        if not n: return char in self._children
        # bonus 1: return if count is at most n
        elif n < 0: return char in self._children and self._children[char]._count <= -n
        # bonus 2: return only if count is at least n
        else: return char in self._children and self._children[char]._count >= n

    def data(self, data=None):
        "Get or set data for node"

        if data is None: return self._data

        self._data = data

        return self

    def children(self):
        "Get child nodes as list"

        return list(self._children.values())

    def parent(self):
        "Return parent node; will return None if root"

        return self._parent

    def is_terminator(self):
        "Check if this is a terminating node"
        return isinstance(self, TriesonodeTerminator)

    #--- TRAVERSAL ---------------------------------------------------------

    def traverse(self, pre=None, post=None):
        "Recursive depth-first traversal over all nodes"
        for node in self._children:
            child = self._children[node]

            # preprocess if exists
            if pre: pre(child)

            yield child
            yield from child.traverse(pre, post)

            # postprocess if exists
            if post: post(child)

    #--- SPECIAL INFO -------------------------------------------------------

    def __len__(self):
        "Number of children"
        return len(self._children)

    def __contains__(self, char):
        "See if char in children. Alias for self.has(char)"
        return self.has(char)

    def __bool__(self):
        "Always true, to allow get() to return falsey if no child exists"
        return True

    #--- SPECIAL ACCESSORS --------------------------------------------------

    def __getitem__(self, char):
        "Get child by bracket indexing. Alias for self.get(char)"
        return self.get(char)

    def __iter__(self):
        "Iterator over children"
        for child in self._children.values():
            yield child

    def __call__(self):
        "call returns value"
        return self._value

    #--- STRING REPRESENTATION ----------------------------------------------

    def __repr__(self):
        "String format"
        return f'{self}'

    def __str__(self):
        "Pretty string format"
        return f'Triesonode <{self._value}> x {self._count}, {len(self._children)} children'

###--- TRIESONODETERMINATOR CLASS -------------------------------------------

class TriesonodeTerminator(Triesonode):
    """
    Represents a terminating node in a trie.

    A terminating node has no children and no value, but can hold data.
    """

    def __init__(self, parent: Triesonode = None, data = True):
        self._count = 1
        self._parent = parent
        self._data = None

        self.data(data)

    def add(self):
        pass

    def get(self):
        pass

    def has(self):
        pass

    def children(self):
        pass

    def traverse(self):
        pass

    def __len__(self):
        pass

    def __contains__(self, unused):
        pass

    def __getitem__(self, unused):
        pass

    def __iter__(self):
        pass

    def __call__(self):
        return None

    def __str__(self):
        return f'TriesonodeTerminator data: {self._data}'
