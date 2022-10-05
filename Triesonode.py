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

        if char in self._children:
            self._children[char]._inc()
        else:
            self._children[char] = Triesonode(self, char)

        # return child if chaining
        if chain: return self._children[char]

        # ... or set chain to False to get same node back
        return self

    def get(self, char=None, w=1):
        """
        Return specified child node if exists.
        If no child node specified, get a random node by relative child counts.
        """

        # no children? return None
        if not self._children: return None

        if char == None:
            children = list(self._children.values())
            weights = [child._count ** w for child in children]

            char = random.choices(children, weights)[0]._value

        try:
            return self._children[char]
        except KeyError:
            return None

    def has(self, char=None):
        """
        Check if child node exists.
        If no char specified, get list of all child keys.
        """
        if not char: return list(self._children.keys())

        return char in self._children

    def set_data(self, data=True):
        "Set data for node"
        self._data = data
        return self

    def data(self):
        "Get data for node"
        return self._data

    def children(self):
        "Get child nodes as list"
        return list(self._children.values())

    def parent(self):
        "Return parent node; will return None if root"
        return self._parent

    #--- TRAVERSAL ---------------------------------------------------------
    def traverse(self, proc=None):
        "Recursive depth-first traversal over all nodes"
        for node in self._children:
            child = self._children[node]
            # apply process if exists
            if proc: proc(child)
            yield child
            yield from child.traverse(proc)

    def substrings(self, limit=None):
        "Collect and return all substrings"
        string = ''
        collection = []
        count = 0
        limit = limit if limit else 0

        # recursive function for depth-first traversal
        def travel(node):
            nonlocal string, limit, count, collection

            for child in node:
                string += child._value

                if child.data():
                    collection.append(string)
                    count += 1
                    if limit and count >= limit: return True

                travel(child)

            string = string[:-1]

        travel(self)
        return collection

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
        "Boolean access always returns True"
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
