""" Triesonode.py
-----------------
Exports Trie Node class
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, Callable, Self
from abc import ABC, abstractmethod

import random

from .items import create_item, AbstractItem, DataItem
#from .visitors import Visitable, AbstractNodeVisitor
from .traversers import Traversable, AbstractTraverser, CallableTraverser

TERMINATOR = DataItem.key_default

###--- ABSTRACT BASE CLASS --------------------------------------------------

class AbstractTriesonode(ABC, Traversable):
    def __init__(self, parent: Optional[Triesonode] = None, item: Optional[AbstractItem] = None):

        # set item to `item` or use `item` as argument to DataItem constructor
        self._item: AbstractItem = item if isinstance(item, AbstractItem) else DataItem(item)

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
        return self.item.value

    @property
    def data(self):
        return self.item.data

    @data.setter
    def data(self, data: Any):
        self.item.data = data

    @abstractmethod
    def add(self, item: AbstractItem):
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
        return TERMINATOR in self.children

    def get_terminator(self):
        if self.has_terminator(): return self.children[TERMINATOR]

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
        Item value

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
        # data

    #--- GET/SET ------------------------------------------------------------

    def add(self,
            item: AbstractItem = None,
            *,
            chain: bool = True,
    ) -> Triesonode|Self:
        "Add item to children and return added node"

        # add terminating node if no item
        if not item: item = DataItem()

        key = item.key

        # if key already exists, increment count, else add new node
        if key in self:
            self[key].count += 1
        else:
            self[key] = Triesonode(self, item)

        # return child if chaining...
        if chain: return self[key]

        # ... or set chain to False to get same node back
        return self

    def __contains__(self, char) -> bool:
        "See if char in children"

        return self.has(char)

    def has(self,
            key: str|AbstractItem = None,
            n: int = 0
    ) -> bool:
        """
        Check if child node exists. Can pass integer (positive or negative) to
        limit success to children that have at least or at most that count.

        If no char specified, get list of all child keys.
        """

        if not self.children: return False

        if key is None: return list(self.children.values())

        if isinstance(key, AbstractItem): key = key.key

        # standard return
        if not n: return key in self.children

        # bonus 1: return if count is at most n
        elif n < 0: return key in self.children and self.children[key].count <= -n

        # bonus 2: return only if count is at least n
        else: return key in self.children and self.children[key].count >= n

    def __getitem__(self, key: str|AbstractItem) -> Triesonode:
        "Get child by bracket indexing"

        return self.get(key)

    def __setitem__(self, key: str|AbstractItem, node: Triesonode):
        "Set child"

        if isinstance(key, AbstractItem): key = key.key

        self.children[key] = node

    def get(self,
            key: str|AbstractItem = None,
            *,
            weight: int|float = 1,
            exclude: Optional[str|AbstractItem|Sequence[str|AbstractItem]] = None
    ):
        """
        Return specified child node if exists. If no child node specified, get
        a random child node by relative child counts.

        Can exclude children by passing optional `exclude` argument
        containing a sequence of items to exclude.

        Parameters
        ==========

        key: [str|AbstractItem]
            Item to get (by key). Returns None if item doesn't exist. If no item
            specified, returns a random item.

        weight: int|float (default 1)
            Weight for the random selector. 1 is normal weight, 2 is double, 0
            is all even weighting, etc.

        exclude: [str|AbstractItem|Sequence] (default [])
            Keys to exclude from the pool of available children
        """

        # no children? return None
        if not self.children: return None

        if isinstance(key, AbstractItem): key = key.key

        # if no item provided, generate one selected from children
        if key is None:

            # convert to sequence
            match exclude:
                case None: exclude = []
                case str(): exclude = [c for c in exclude]
                case AbstractItem(): exclude = [exclude.key]

            # create exclusion set from keys
            exclude = {i.key if isinstance(i, AbstractItem) else i for i in exclude}

            # get children that aren't excluded
            children = [childnode for childnode in self if childnode.key not in exclude]

            # return None if all are excluded or no children
            if not children: return None

            # get weights of retrieved children
            weights = [childnode.count ** weight for childnode in children]

            # select node by weighted random choice
            return random.choices(children, weights)[0]

        # ... otherwise get item as string and return corresponding node
        else:
            return self.children[key]

    #--- TERMINATING/LEAF NODES ---------------------------------------------

    def terminate(self, data: Any = None):
        "Add a terminating node to children"

        item = DataItem(data)

        # if no terminating node, create one, else update count and data
        if not self.has_terminator():
            self.children[TERMINATOR] = TriesonodeTerminator(self, item)
        else:
            self.children[TERMINATOR].count += 1

            # TODO allow callable to transform data
            if data:
                self.children[TERMINATOR].data = data

    # is_terminator() inherited

    def has_terminator(self):
        "True if terminating node is a child"

        return TERMINATOR in self and isinstance(self[TERMINATOR], TriesonodeTerminator)

    # get_terminator() inherited

###--- TRIESONODETERMINATOR CLASS -------------------------------------------

class TriesonodeTerminator(AbstractTriesonode):
    """
    Represents a terminating node in a trie.

    A terminating node has no children and no value, but can hold data.
    """

    def __init__(self, parent: Optional[Triesonode] = None, data: Any = True):

        # Terminating node only supports DataItem
        if isinstance(data, AbstractItem): data = DataItem(data)

        super().__init__(parent, data)

    def add(self, *args, **kwargs):
        return self

    def has(self, *args, **kwargs):
        return False

    def get(self, *args, **kwargs):
        return None

    def terminate(self, data: Any):
        return self

    def is_terminator(self):
        return True
