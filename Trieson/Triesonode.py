""" Triesonode.py
-----------------
Exports Trie Node class
"""

from __future__ import annotations
from typing import Optional, Any, Callable, Iterable
from types import FunctionType
import random

TERMINATOR = ''
DEFAULT_KEY_FUNC = lambda x: x.__repr__()

###--- HELPERS --------------------------------------------------------------

def is_primitive(item = None):
    "Helper function to determine whether item is simple primitive type"

    return type(item) in (str, int, float, bool)

def make_key(item, key_func: Callable[[Any], str] = DEFAULT_KEY_FUNC):
    "Helper function to return string representation of item"

    if item is None: return None

    if is_primitive(item): return str(item)
    else: return key_func(item)

###--- TRIESONODE CLASS -----------------------------------------------------

class Triesonode:
    """
    Represents a node in the Trieson trie. Contains low-level methods for
    manipulating the trie on a node-by-node basis. Includes methods for:
    - Adding child nodes
    - Getting child nodes by key
    - Checking for existence of children
    - Getting and setting node data

    Constructor Parameters
    ==========

    value: Any
        Item value

    data: [Any] (default None)
        Data to associate with item
    """

    #--- CONSTRUCTOR --------------------------------------------------------

    def __init__(self,
                 parent: Optional[Triesonode] = None,
                 value: Any = '',
                 data: Optional[Any] = None,
                 *,
                 # can avoid call overhead by passing key string directly
                 key: str|Callable[[Any], str] = DEFAULT_KEY_FUNC
    ):
        self._key = key if type(key) is str else make_key(value, key)
        self._value = value
        self._data = data

        self._count = 1

        self._children: dict = {}
        self._parent = parent

    #--- GET/SET ------------------------------------------------------------

    def add(self, item: Any, chain: bool = True,
            *,
            key_func: Callable[[Any], str] = DEFAULT_KEY_FUNC,
            data: Any = None
    ):
        "Add item to children and return added node"

        # generate key
        key = make_key(item, key_func)

        # if key already exists, increment count, else add new node
        if key in self._children:
            self._children[key]._count += 1
        else:
            self._children[key] = Triesonode(self, item, data, key=key)

        # return child if chaining...
        if chain: return self._children[key]

        # ... or set chain to False to get same node back
        return self

    def terminate(self, data = None):
        "Add a terminating node to children"

        # if no terminating node, create one, else update count and data
        if TERMINATOR not in self._children:
            self._children[TERMINATOR] = TriesonodeTerminator(self, data)
        else:
            self._children[TERMINATOR]._count += 1
            if data:
                self._children[TERMINATOR].data(data)

    def has(self,
            item: Optional[Any] = None,
            n: int = 0,
            *,
            key_func: Callable[[Any], str] = DEFAULT_KEY_FUNC
    ):
        """
        Check if child node exists. Can pass integer (positive or negative) to
        limit success to children that have at least or at most that count.

        If no char specified, get list of all child keys.
        """

        if item is None: return list(self._children.keys())

        key = make_key(item, key_func)

        # standard return
        if not n: return key in self._children
        # bonus 1: return if count is at most n
        elif n < 0: return key in self._children and self._children[key]._count <= -n
        # bonus 2: return only if count is at least n
        else: return key in self._children and self._children[key]._count >= n

    def get(self,
            item: Any = None,
            weight: int|float = 1,
            *,
            key_func: Callable[[Any], str] = DEFAULT_KEY_FUNC,
            exclude: Optional[Any] = None
    ):
        """
        Return specified child node if exists. If no child node specified, get
        a random child node by relative child counts.

        Can exclude children by passing optional `exclude_chars` argument
        containing an iterable of items or item keys to exclude.

        Parameters
        ==========

        item: [Any]
            Item to get. Returns None if item doesn't exist. If no item
            specified, returns a random item.

        weight: int|float (default 1)
            Weight for the random selector. 1 is normal weight, 2 is double, 0
            is all even weighting, etc.

        key_func: callable (default calls __repr__() method of `item`)
            Function to convert non-primitive item into a string to use as key

        exclude: [Any] (default [])
            Items or keys to exclude from the pool of available children
        """

        # no children? return None
        if not self._children: return None

        # ensure exclude is a sequence
        if not exclude: exclude = []

        # if no item provided, generate one selected from children
        if item is None:
            # get children that aren't excluded
            children = [childnode for childnode in self.children() if childnode.key() not in exclude and childnode.value() not in exclude]

            # return None if all are excluded or no children
            if not children: return None

            # get weights of retrieved children
            weights = [childnode.count() ** weight for childnode in children]

            # select node by weighted random choice
            return random.choices(children, weights)[0]

        # ... otherwise get item as string and return corresponding node
        else:
            key = make_key(item, key_func)

            return self.children(key)

    def key(self):
        "Get key associated with node"

        return self._key

    def value(self):
        "Get value associated with node"

        return self._value

    def data(self, data: Any = None):
        """
        Get or set data for node

        Pass a function to manipulate existing data.
        """

        if data is None: return self._data

        if isinstance(data, FunctionType):
            # call function on data
            self._data = data(self._data)
        else:
            # set data to new value
            self._data = data

        return self

    def count(self):
        "Get value count"

        return self._count

    def children(self, key: Optional[str|Sequence] = None):
        "Get single child, multiple children, or all child nodes as list"

        # No argument - return all child nodes
        if key is None:
            return list(self._children.values())

        # string argument - return single child or None if not in children
        if type(key) is str:
            return self._children[key] if key in self._children else None

        # iterable argument - return all specified children
        else:
            return [self._children[k] for k in key if k in self._children]

        return None

    def parent(self):
        "Return parent node; will return None if root"

        return self._parent

    def is_terminator(self):
        "Check if this is a terminating node"
        return False

    def has_terminator(self):
        "True if terminating node is a child"
        return TERMINATOR in self

    def get_terminator(self):
        "Get terminator child if exists or None"
        return self[TERMINATOR] if TERMINATOR in self else None

    #--- TRAVERSAL ---------------------------------------------------------

    def traverse(self, pre=None, post=None):
        "Recursive depth-first traversal over all nodes"
        for node in self._children:
            child = self._children[node]

            # preprocess if exists
            if pre: pre(child)

            yield child
            if not child.is_terminator():
                yield from child.traverse(pre, post)

            # postprocess if exists
            if post: post(child)

    #--- SPECIAL INFO -------------------------------------------------------

    def __len__(self):
        "Number of children"
        return len(self._children)

    def __contains__(self, char):
        "See if char in children"
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
        return f'Triesonode <{self._value}> x {self._count}, {len(self._children)} children: {list(self._children.keys())}'

###--- TRIESONODETERMINATOR CLASS -------------------------------------------

class TriesonodeTerminator(Triesonode):
    """
    Represents a terminating node in a trie.

    A terminating node has no children and no value, but can hold data.
    """

    def __init__(self, parent: Optional[Triesonode] = None, data = True):
        self._key = ''
        self._value = ''
        self._count = 1
        self._parent = parent
        self._data = None
        self._children: dict = {}

        self.data(data)

    def add(self):
        pass

    def terminate(self, unused):
        pass

    def get(self):
        pass

    def has(self):
        pass

    def children(self):
        pass

    def traverse(self, unused_pre, unused_post):
        yield self

    def is_terminator(self):
        return True

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
