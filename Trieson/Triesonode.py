""" Triesonode.py
-----------------
Exports Trie Node class
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, Self
from abc import ABC, abstractmethod
from collections.abc import Collection, Callable

import random

from .vessels import VesselFactory
from .traversers import Traversable

LEAF_KEY = ''

###--- ABSTRACT BASE CLASS --------------------------------------------------

class AbstractTriesonode(ABC, Traversable):

    def __init__(self,
                 parent: Optional[Triesonode] = None,
                 value: Any = None,
                 data: Any = None,
                 *,
                 factory: VesselFactory = VesselFactory(cache = False)
    ):

        # set item to `item`
        self._item = factory(value, data)

        # all nodes start with count 1
        self._count: int = 1

        # node parent is optional - if None means this is root node
        self._parent: Optional[Triesonode] = parent

        # dictionary of child nodes
        self._children: dict = {}

    @property
    def item(self):
        return self._item

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, n: int):
        self._count = n

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    @property
    def key(self):
        return self.item.key

    @property
    def value(self):
        return self.item

    @property
    @abstractmethod
    def data(self):
        pass

    @abstractmethod
    def add(self, item):
        pass

    @abstractmethod
    def has(self, key: str):
        pass

    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def terminate(self, data: Any):
        pass

    def is_terminator(self):
        return False

    def has_terminator(self):
        return LEAF_KEY in self.children

    def get_terminator(self):
        if self.has_terminator(): return self.children[LEAF_KEY]

        return None

    def __len__(self):
        "Number of children"

        return len(self.children)

    def __bool__(self):
        "Always returns True"

        return True

    def __iter__(self):
        "Iterator over children"

        return (childnode for childnode in self.children.values())

    def __repr__(self):
        "String format"

        return f'{type(self).__name__}({repr(self.parent)}, {repr(self.item)})'

    def __str__(self):
        "Pretty string format"

        return f'{type(self).__name__} <{self.value}> x {self.count}, {len(self.children)} children: {list(self.children.keys())}'

###--- TRIESONODE CLASS -----------------------------------------------------

class Triesonode(AbstractTriesonode):
    """
    Represents a node in the Trieson trie. Contains low-level methods for
    manipulating the trie on a node-by-node basis. Includes methods for:
    - Adding child nodes
    - Getting child nodes by key
    - Checking for existence of children
    - Getting and setting node data

    Constructor Parameters
    ======================

    value: Any
        Vessel value

    data: [Any] (default None)
        Data to associate with item
    """

    #--- CONSTRUCTOR --------------------------------------------------------

        # __init__() inherited

    #--- PROPERTIES ---------------------------------------------------------

        # inherited:
        # item
        # count
        # parent
        # children
        # key
        # value

    @property
    def data(self):
        """
        On a node will return terminating node's data only if a leaf node exists.
        """
        if self.has_terminator(): return self.get_terminator().data

        return None

    #--- GET/SET ------------------------------------------------------------

    def add(self,
            item: Any = None,
            *,
            chain: bool = True,
    ) -> Triesonode|Self:
        "Add item to children and return added node"

        # add terminating node if no item
        if not item: return self.terminate()

        key = genkey(item)

        # if key already exists, increment count, else add new node
        if key in self:
            self[key].count += 1
        else:
            self[key] = Triesonode(self, item)

        # return child if chaining...
        if chain: return self[key]

        # ... or set chain to False to get same node back
        return self

    def has(self,
            key: Any = None,
            n: int = 0
    ) -> bool:
        """
        Check if child node exists. Can pass integer (positive or negative) to
        limit success to children that have at least or at most that count.

        If no char specified, get list of all child keys.
        """

        # no children
        if not self.children: return False

        # no key specified
        if key is None: return False

        # convert key to string representation
        key = DEFAULT_KEY_FUNC(key)

        # standard return
        if not n: return key in self.children

        # bonus 1: return if count is at most n
        elif n < 0: return key in self.children and self.children[key].count <= -n

        # bonus 2: return only if count is at least n
        else: return key in self.children and self.children[key].count >= n

    def get(self,
            key: Any = None,
            *,
            weight: int|float = 1,
            exclude: Optional[Any|Sequence[Any]] = None,
            split_str: bool = True
    ):
        """
        Return specified child node if exists. If no child node specified, get
        a random child node by relative child counts.

        Can exclude children by passing optional `exclude` argument
        containing a sequence of items to exclude.

        Parameters
        ==========

        key:
            Vessel to get (by key). Returns None if item doesn't exist. If no item
            specified, returns a random item.

        weight: (default 1)
            Weight for the random selector. 1 is normal weight, 2 is double, 0
            is all even weighting, etc.

        exclude: (default [])
            Keys to exclude from the pool of available children

        split_str: (default True)
            Automatically split string into characters
        """

        # no children? return None
        if not self.children: return None

        # if no item provided, generate one selected from children...
        if key is None:

            # convert exclusion set to sequence
            match exclude:
                case None:
                    exclude = []
                case str():
                    if split_str:
                        exclude = [c for c in exclude]
                    else:
                        exclude = [exclude]
                case Collection():
                    exclude = [DEFAULT_KEY_FUNC(c) for c in exclude]
                case _:
                    exclude = [DEFAULT_KEY_FUNC(exclude)]

            # create exclusion set from keys
            exclude = {i for i in exclude}

            # get children that aren't excluded
            children = [childnode for childnode in self if childnode.key not in exclude]

            # return None if all are excluded or no children
            if not children: return None

            # get weights of retrieved children
            weights = [childnode.count ** weight for childnode in children]

            # select node by weighted random choice
            return random.choices(children, weights)[0]

        # ... otherwise get item key as string
        key = DEFAULT_KEY_FUNC(key)

        # if key exists return the node
        if self.has(key):
            return self.children[key]

        # return None if no child found
        return None

    def __contains__(self, char) -> bool:
        "See if char in children"

        return self.has(char)

    def __getitem__(self, key: Any) -> Triesonode:
        "Get child by bracket indexing"

        return self.get(key)

    def __setitem__(self, key: str, node: Triesonode):
        "Set child"

        self.children[key] = node

    #--- TERMINATING/LEAF NODES ---------------------------------------------

    def terminate(self, data: Any = None):
        "Add a terminating node to children"

        # if no terminating node, create one, else update count and data
        if not self.has_terminator():
            self.children[LEAF_KEY] = TriesonodeTerminator(self, data)
        else:
            self.children[LEAF_KEY].count += 1

        if data is not None:
            self.children[LEAF_KEY].data = data

        return self

    # is_terminator() inherited

    def has_terminator(self):
        "True if terminating node is a child"

        return LEAF_KEY in self and isinstance(self[LEAF_KEY], TriesonodeTerminator)

    # get_terminator() inherited

###--- TRIESONODETERMINATOR CLASS -------------------------------------------

class TriesonodeTerminatorError(Exception):
    pass

class TriesonodeTerminator(AbstractTriesonode):
    """
    Represents a terminating node in a trie.

    A terminating node has no children and no value, but can hold data.
    """

    def __init__(self, parent: Optional[Triesonode] = None, data: Any = True):

        super().__init__(parent)

        self._data = data # terminating node data, not associated with item

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: Any):
        match data:
            case Callable():
                self._data = data(self._data)
            case _:
                self._data = data

    def add(self, *args, **kwargs):
        """
        Cannot add nodes to a terminating node. Will raise an exception.
        """
        return self

    def has(self, *args, **kwargs):
        return False

    def get(self, *args, **kwargs):
        return None

    def terminate(self, data: Any):
        return self

    def is_terminator(self):
        return True
