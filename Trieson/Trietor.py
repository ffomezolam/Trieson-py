""" Trietor.py
--------------
Defines the object that holds a Trieson query result
"""

from __future__ import annotations

from typing import Optional, Any, Self
from collections.abc import Sequence, Iterable, Callable

import logging

class Trietor(Sequence):
    """
    Trietor class
    """

    def __init__(self, items: Optional[Sequence[Any]] = None, term_data: Any = None):
        self._keys = []
        self._values = []
        self._data = []

        self._term = None

        if items is not None: self.add(items)
        if term_data is not None: self.terminate(term_data)

    def copy(self):
        "Make a copy of instance"

        return Trietor(zip(self._keys, self._values, self._data), self._term)

    def add(self, key: str|Sequence[Sequence[Any]]|Trietor, value: Any = None, data: Any = None) -> Self:
        """
        Add key, value, data to collection.

        Can pass sequence in form [(key, value, data), (key, value, data), ...]
        """

        if type(key) is str:
            self._keys.append(key)
            self._values.append(value)
            self._data.append(data)
        elif isinstance(key, Sequence|Iterable):
            for items in key:
                self.add(*items)
        else:
            logging.debug(f"Cannot add item with key {key} of type {type(key)}")

        return self

    def append(self, *args, **kwargs):
        "Alias for add()"

        return self.add(*args, **kwargs)

    def pop(self) -> tuple:
        "Remove and return final item"

        return (self._keys.pop(), self._values.pop(), self._data.pop())

    def terminate(self, data: Any = True) -> Self:
        "Add terminating data signifying complete sequence"

        self._term = data

        return self

    def has_terminator(self):
        "Whether has terminating data"

        return self._term is not None

    def terminator(self):
        "Terminating data"

        return self._term

    def term_data(self):
        "Alias for terminator()"

        return self.terminator()

    def keys(self, ix: Optional[int|Callable[..., Sequence]] = None):
        "Return key at index, in slice, or all keys"

        return self._keys if ix is None else self._keys[ix]

    def values(self, ix: Optional[int|Callable[..., Sequence]] = None):
        "Return key at index, in slice, or all keys"

        return self._values if ix is None else self._values[ix]

    def data(self, ix: Optional[int|Callable[..., Sequence]] = None):
        "Return data at index, in slice, or all data"

        return self._data if ix is None else self._data[ix]

    def items(self, ix: Optional[int|Callable[..., Sequence]] = None):
        "Return data at index, in slice, or as list of tuples"

        if ix is None or isinstance(ix, slice):
            return list(zip(self.keys(ix), self.values(ix), self.data(ix)))
        else:
            return (self.keys(ix), self.values(ix), self.data(ix))

    def as_str(self):
        "Alias for __str__()"

        return str(self)

    def __eq__(self, other: Trietor|Sequence[Any]):
        """
        Test for equality by key. Objects are equal if keys are the same value
        and in the same order.
        """

        if not other: return False

        # if passing other sequence, check whether its keys or items
        if type(other) is not Trietor:
            if type(other[0]) is str:
                # assume keys
                return self._keys == other
            elif isinstance(other, Sequence|Iterable):
                # assume (key,value,data)
                return self._keys == [i[0] for i in other]
        else:
            # compare keys
            return self._keys == other._keys

    def __add__(self, other: Trietor|Sequence[Any]):
        "Append Trietor instances. Terminal data taken from right operand."

        # no addition, return copy
        if not other: return self.copy()

        # if passing other sequence, make sure it is a sequence of sequences
        if type(other) is not Trietor:
            if type(other[0]) is str:
                other = [other]

            other = Trietor(other)

        keys = self._keys + other._keys
        values = self._values + other._values
        data = self._data + other._data
        term = other._term

        return Trietor(zip(keys, values, data), term)

    def __iadd__(self, other: Trietor|Sequence[Any]):
        "Add right sequence to collection"

        # check for sequence of sequences
        if type(other) is not Trietor:
                if type(other[0]) is str:
                    other = [other]

            other = Trietor(other)

        self.append(other)

        return self

    def __len__(self):
        "Return length of results"

        return len(self._keys)

    def __contains__(self, v: Any) -> bool:
        "See if key or value is in collection"

        return v in self._keys or v in self._values

    def __getitem__(self, ix) -> Sequence:
        "Get item by index, key, or slice"

        return self.items(ix)

    def __iter__(self):
        "Iterate over all data"

        return (self[ix] for ix in range(len(self._keys)))

    def __call__(self):
        "Alias for terminator()"

        return self.terminator()

    def __repr__(self):
        "Programmatic string representation"

        return f'Trietor({list(self.__iter__())}, {self._term})'

    def __str__(self):
        "Human-readable string representation - concatenated keys"

        return ''.join(self._keys)
