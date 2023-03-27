""" trie.py
-----------------
Basic trie implementation
"""

class Trie:
    def __init__(self):
        self._root = Node()

    def add(self, string):
        node = self._root

        for char in string:
            node = node.add(char)

        # add terminating node
        node.add('')

        return self

    def match(self, prefix = ''):
        node = self._root
        chars = []
        collection = []

        # recursive function
        def _next(node):
            for char in node.chars():
                chars.append(char) # add character to list

                if not char: # match ''
                    # terminate and add to collection
                    collection.append(''.join(chars))
                else:
                    _next(node.get(char))

                chars.pop()

        # collect prefix chars - ensure they are in trie
        for char in prefix:
            node = node.get(char)

            if not node: break

            chars.append(char)

        if node: _next(node)

        return collection

class Node:
    def __init__(self, parent = None):
        self._children = dict()
        self._parent = parent

    def add(self, char):
        if char not in self._children:
            self._children[char] = Node(self)

        return self._children[char]

    def get(self, char):
        if char in self._children: return self._children[char]

        return None

    def has(self, char):
        return char in self._children

    def chars(self):
        return list(self._children.keys())

    def __getitem__(self, char):
        return get(char)

    def __contains__(self, char):
        return self.has(char)

    def __iter__(self):
        return (char for char in self._children)
