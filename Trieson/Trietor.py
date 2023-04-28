""" Trietor.py
--------------
Defines the object that holds a Trieson query result
"""

from __future__ import annotations

from typing import Optional, Any, Self
from collections.abc import Sequence

class Trietor:
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

    def add(self, key: str|Sequence[Sequence[str,Any,Any]], value: Any = None, data: Any = None) -> Self:
        """
        Add key, value, data to collection.

        Can pass sequence in form [(key, value, data), (key, value, data), ...]
        """

        if type(key) is str:
            self._keys.append(key)
            self._values.append(value)
            self._data.append(data)
        else:
            for items in key:
                self.add(*items)

        return self

    def append(self, *args, **kwargs):
        "Alias for add()"

        return self.add(*args, **kwargs)

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

    def keys(self, ix: Optional[int] = None):
        "Return key at index or all keys as iterator"

        return (k for k in self._keys) if ix is None else self._keys[ix]

    def values(self, ix: Optional[int] = None):
        "Return key at index or all keys as iterator"

        return (v for v in self._values) if ix is None else self._values[ix]

    def data(self, ix: Optional[int] = None):
        "Return data at index or all data as iterator"

        return (d for d in self._data) if ix is None else self._data[ix]

    def items(self, ix: Optional[int] = None):
        "Return all data at index or as list of tuples"

        return self.__iter__() if ix is None else self[ix]

    def as_str(self):
        "Alias for __str__()"

        return str(self)

    def __add__(self, other: Trietor):
        "Append Trietor instances. Terminal data taken from right operand."

        keys = self._keys + other._keys
        values = self._values + other._values
        data = self._data + other._data
        term = other._term

        return Trietor(zip(keys, values, data), term)

    def __len__(self):
        "Return length of results"

        return len(self._keys)

    def __getitem__(self, ix):
        "Get item by index"

        return (self.keys(ix), self.values(ix), self.data(ix))

    def __iter__(self):
        "Iterate over all data"

        return (self[ix] for ix in range(len(self._keys)))

    def __call__(self):
        "Alias for terminator()"

        return self.terminator()

    def __repr__(self):
        "Programmatic string representation"

        return f'Trietor({list(self.__iter__())})'

    def __str__(self):
        "Human-readable string representation - concatenated keys"

        return ''.join(self._keys)
