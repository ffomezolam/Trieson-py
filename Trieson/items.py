""" items.py
-----------------
Implements various item styles
"""

from __future__ import annotations

import logging

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from typing import Any, Self, Callable, Optional
from collections.abc import Sequence

# --- ITEMS -----------------------------------------------------------------

class AbstractItem(ABC):
    "Abstract base class for Trieson Items"

    @abstractmethod
    def __init__(self):
        pass

    @property
    @abstractmethod
    def key(self):
        pass

    @property
    @abstractmethod
    def value(self):
        pass

    @property
    @abstractmethod
    def data(self):
        pass

    @data.setter
    @abstractmethod
    def data(self, data: Any):
        pass

    def __eq__(self, other: AbstractItem):
        "Test whether items are equal"

        return (self.key == other.key and
                self.value == other.value and
                self.data == other.data)

    def __repr__(self):
        return f'AbstractItem(value = {self.value}, data = {self.data}, key = {self.key})'

    def __str__(self):
        return self.key

    def __getattr__(self, name: str):
        "Set up getter aliases"

        match name.lower():
            case 'k':
                return self.key
            case 'v':
                return self.value
            case 'd':
                return self.data

class DataItem(AbstractItem):
    "Item consisting of data only"

    key_default = ''

    def __init__(self, data: Optional[Any] = None):
        self._data = data

    @property
    def key(self):
        return DataItem.key_default

    @property
    def value(self):
        return None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: Any):
        self._data = data

    def __repr__(self):
        return f'DataItem(data = {self.data})'

class CharItem(DataItem):
    "Item consisting of a single character only"

    def __init__(self, char: str, data: Optional[Any] = None):
        char = str(char)

        self._char = char[0]

        super().__init__(data)

    @property
    def key(self):
        return self._char

    @property
    def value(self):
        return self._char

    def __repr__(self):
        return f'CharItem(char = {self.key}, data = {self.data})'

class StringItem(DataItem):
    "Item consisting of a string of arbitrary length"

    def __init__(self, string: str, data: Optional[Any] = None):
        self._string = str(string)

        super().__init__(data)

    @property
    def key(self):
        return self._string

    @property
    def value(self):
        return self._string

    def __repr__(self):
        return f'StringItem(string = {self.key}, data = {self.data})'

class ArbitraryItem(DataItem):
    "Items consisting of any data"

    default_key_func = lambda v: v.__str__()

    def __init__(self,
                 value: Any,
                 data: Optional[Any] = None,
                 key: Optional[str|Callable[[v], str]] = None
    ):
        if key is None: key = ArbitraryItem.default_key_func

        self._value = value
        self._key = key if type(key) is str else key(value)

        super().__init__(data)

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return f'ArbitraryItem(value = {self.value}, data = {self.data}, key = {self.key})'

# --- FACTORY ---------------------------------------------------------------

def create_item(value: Any = None,
                data: Any = None,
                key: Optional[str|Callable[[Any], str]] = None
) -> AbstractItem:
    "Generate an item from data"

    item = None

    # if key and value are equivalent strings, set key to None
    if isinstance(key, str) and key == value: key = None

    # if key is None
    elif key is None:

        # no key and no value is DataItem
        if value is None:
            item = DataItem(data)

        # no key and value is string ...
        elif isinstance(value, str):

            # ... with length 0 is DataItem
            if len(value) < 1:
                item = DataItem(data)

            # ... with length 1 is CharItem
            elif len(value) == 1:
                item = CharItem(value, data)

            # ... with length > 1 is StringItem
            else:
                item = StringItem(value, data)

        # no key and value is not string
        else:
            item = ArbitraryItem(value, data)

    # if key is callable
    else:
        item = ArbitraryItem(value, data, key)

    return item

class ItemFactory:
    "Factory for creating and caching Items"

    def __init__(self, cache: bool = True):
        self._pool = dict() if cache else None
        self.cache = cache

    def create(self,
               value: Any = None,
               data: Any = None,
               key: Optional[str|Callable[[Any], str]] = None
    ) -> AbstractItem:
        "Factory method to generate appropriate item based on input"

        # if set, then check cache first
        if self.cache:
            lookup_key = key

            # if no key
            if key is None:

                # data only
                if value is None: lookup_key = ''

                # key set from value if value is string
                elif isinstance(value, str): lookup_key = value

                # otherwise use default key-generator function
                else: lookup_key = ArbitraryItem.default_key_func(value)

            # otherwise if key is callable then generate key
            elif isinstance(key, Callable):
                lookup_key = key(value)

            # otherwise key is string so use as is
            else:
                pass

            # if key in pool the use cached item
            if lookup_key in self._pool: return self._pool[lookup_key]

        # generate new item
        item = create_item(value, data, key)

        # only set cache if using it
        if self.cache: self._pool[item.key] = item

        return item

    def get(self, key: str, default: Any = None):
        "Get item from pool or `default` if doesn't exist"

        if not self.cache: return None

        return self._pool.get(key, default)
