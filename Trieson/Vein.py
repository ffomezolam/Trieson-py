""" Vein.py
--------------
Defines the object that holds a Trieson query result
"""

from __future__ import annotations

from typing import Optional, Any, Self
from collections.abc import Iterable, Sequence, Callable
from copy import copy

from .vessels import Vessel

import logging

class Vein(Sequence):
    """
    Vein class
    """

    # --- CONSTRUCTOR -------------------------------------------------------

    def __init__(self, items: Optional[Vessel|Sequence[Vessel]] = None):
        self._items = list()
        self._keys = dict()

        if items is not None: self.add(items)

    # --- ADD/REMOVE --------------------------------------------------------

    def copy(self):
        "Make a copy of instance"

        return Vein(copy(self._items))

    def add(self, items: Vessel|Sequence[Vessel]|Vein) -> Self:
        """
        Add item to collection. Can pass a single item, a sequence of items, or
        another Vein instance.
        """

        # add a single item
        if isinstance(items, Vessel):
            item = items

            self._items.append(item)

            # add key to keys dict if necessary
            if item.key not in self._keys: self._keys[item.key] = list()

            # save item index in keys dict
            self._keys[item.key].append(len(self) - 1)

        # add multiple items
        elif isinstance(items, Iterable):
            for item in items:
                self.add(item)

        # invalid item
        else:
            logging.debug(f"Cannot add item {item}")

        return self

    def append(self, *args, **kwargs):
        "Alias for add()"

        return self.add(*args, **kwargs)

    def pop(self) -> Vessel:
        "Remove and return final item"

        item = self._items.pop()
        self._keys[item.key].pop()
        return item

    def clear(self) -> Self:
        "Clear all items"

        self._items.clear()
        self._keys.clear()

        return self

    def __add__(self, other: Vein|Vessel|Sequence[Vessel]) -> Vein:
        "Append Vein instances. Terminal data taken from right operand."

        return self.copy().add(other)

    def __iadd__(self, other: Vein|Vessel|Sequence[Vessel]) -> Self:
        "Add right sequence to collection. Data taken from added sequence."

        self.add(other)

        return self

    # --- DATA --------------------------------------------------------------

    @property
    def keys(self) -> list:
        return [item.key for item in self]

    @property
    def values(self) -> list:
        return [item.value for item in self]

    @property
    def data(self) -> list:
        return [item.data for item in self]

    @property
    def items(self) ->list:
        return self._items

    def __getitem__(self, ix) -> Vein:
        "Get item(s) by index, key, or slice"

        if type(ix) is str:
            return Vein([self.items[x] for x in self._keys[ix]])
        else:
            return Vein(self.items[ix])

    def __iter__(self):
        "Iterate over all data"

        return (item for item in self.items)

    def has_key(self, key: str) -> bool:
        "Test if key in collection"

        return key in self.keys

    def has_value(self, value: Any) -> bool:
        "Test if value in collection"

        return value in self.values

    def has_data(self, data: Any) -> bool:
        "Test if data in collection"

        return data in self.data

    def has_item(self, item: Vessel) -> bool:
        "Test if item in collection by testing for key"

        return any(self.items[ix] == item for ix in self._keys.get(item.key, ()))

    def __contains__(self, key: str) -> bool:
        "See if key is in collection"

        return self.has_key(key)

    def __len__(self):
        "Return length of results"

        return len(self.items)

    def __eq__(self, other: Vein):
        """
        Test for equality by item.
        """

        if not other: return False

        if len(self) != len(other): return False

        return all(self.items[ix] == other.items[ix] for ix in range(len(self)))

    # --- STRING REPRESENTATION ---------------------------------------------

    def as_str(self):
        "Human-readable string representation - concatenated keys"

        return ''.join(self.keys)

    def __repr__(self):
        "Programmatic string representation"

        return f'Vein({self._items})'

    def __str__(self):
        "Alias for as_str()"

        return self.as_str()
