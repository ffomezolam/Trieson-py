""" Triesonode.py
-----------------
Exports Trie Node class
"""

from __future__ import annotations
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

    def __init__(self, parent:Triesonode = None, value: str = ''):
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
            self._children[char]._inc()
        else:
            self._children[char] = Triesonode(self, char)

        # return child if chaining...
        if chain: return self._children[char]

        # ... or set chain to False to get same node back
        return self

    def get(self, char=None, weight=1):
        """
        Return specified child node if exists.
        If no child node specified, get a random node by relative child counts.
        """

        # no children? return None
        if not self._children: return None

        # if no char provided, generate one selected from children
        if char == None:
            children = list(self._children.values())

            # create weights for random selection
            weights = [child._count ** weight for child in children]

            # select by weighted choice
            char = random.choices(children, weights)[0]._value

        # return node or None
        try:
            return self._children[char]
        except KeyError:
            return None

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

    #--- PRIVATE -----------------------------------------------------------

    def _inc(self):
        "Increment count by 1"
        self._count += 1
        return self

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

    #--- STRING REPRESENTATION ----------------------------------------------

    def __repr__(self):
        "String format"
        return f'Triesonode <{self._value}> x {self._count}, {len(self._children)} children'
