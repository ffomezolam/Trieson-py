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

class AbstractItem(ABC):
    "Abstract base class for Trieson Items"

    def __init__(self, data: Optional[Any] = None):
        self._data = data

    @property
    @abstractmethod
    def key(self):
        pass

    @property
    @abstractmethod
    def value(self):
        pass

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: Any):
        self._data = data

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

    def __init__(self, data: Optional[Any] = None):
        super().__init__(data)

    @property
    def key(self):
        return None

    @property
    def value(self):
        return None

    def __repr__(self):
        return f'DataItem(data = {self.data})'

class CharItem(AbstractItem):
    "Item consisting of a single character only"

    def __init__(self, char: str, data: Optional[Any] = None):
        char = str(char)

        self._char = char if len(char) < 2 else char[0]

        super().__init__(data)

    @property
    def key(self):
        return self._char

    @property
    def value(self):
        return self._char

    def __repr__(self):
        return f'CharItem(char = {self.key}, data = {self.data})'

class StringItem(AbstractItem):
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

class ArbitraryItem(AbstractItem):
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
