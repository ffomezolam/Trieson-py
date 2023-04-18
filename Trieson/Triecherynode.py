""" Triecherynode.py
--------------------
Node for Triechery class
"""

from __future__ import annotations
from typing import Optional, Any
from types import FunctionType
import random

from .Triesonode import Triesonode

def is_primitive(item = None):
    "Helper function to determine whether item is primitive type"
    return type(item) in [int, float, str, bool]

def as_key(item = None, str_func = lambda x: x.__repr__()):
    "Helper function to get item as primitive"

    if item is None: return None

    return item if is_primitive(item) else str_func(item)

class Triecherynode(Triesonode):
    """
    Represents a node in the Triechery trie.

    Inherits from Triesonode.
    """

    def __init__(self,
                 parent: Triecherynode = None,
                 value: str = '',
                 item: Any = None,
                 data: Any = None
    ):
        super().__init__(parent, value, data)
        self._item = item

    def add(self, item, chain = True, *, str_func = lambda x: x.__repr__(), data: Any = None):
        """
        Add item to children and return added node.

        If item is not a primitive, `str_func` argument accepts a function
        with `item` as an argument that should return the string representation
        that will be used as a key.
        """

        key = as_key(item, str_func)

        # if item key already exists, increment count, else add new node
        if key in self._children:
            self._children[key]._count += 1
        else:
            self._children[key] = Triecherynode(self, key, item, data)

        if chain: return self._children[key]

        return self

    def has(self, item=None, n=0, *, str_func = lambda x: x.__repr__()):
        """
        Test for existence of item in children. Second argument will limit
        success to children with at least or at most that count.

        If no item specified, get list of all child values.
        """

        if item is None: return [i._item for i in self._children.values()]

        key = as_key(item, str_func)

        return super().has(key, n)

    def get(self, item = None, weight: int|float = 1,
            *,
            exclude_items: list|tuple|set = [], str_func = lambda x: x.__repr__()):
        """
        Return specified child node if exists. If not specified, get a random
        node by relative child counts.

        Can exclude children by passing optional `exclude_items` argument.
        """

        key = as_key(item, str_func)
        exclude_chars = [as_key(i, str_func) for i in exclude_items]

        return super().get(key, weight, exclude_chars = exclude_chars)

    # Inherited from Triesonode
    # data(data)
    # children()
    # parent()
    # is_terminator()
    # has_terminator()
    # get_terminator()
    # traverse(pre, post)

    def __call__(self):
        "Returns item"
        return self._item

    # Magic methods inherited from Triesonode
    # __len__
    # __contains__
    # __bool__
    # __getitem__
    # __iter__
    # __repr__

    def __str__(self):
        string = super().__str__()
        string = string[:12] + f'{self._item}:' + string[12:]
        string = string.replace('Triesonode', 'Triecherynode')
        return string
