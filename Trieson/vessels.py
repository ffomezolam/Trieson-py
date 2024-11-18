""" vessels.py
-----------------
A uniform class for representing an item container, and related factory class
"""

from __future__ import annotations

import logging

from typing import Any, Optional
from collections.abc import Collection

# --- GLOBALS ---------------------------------------------------------------

DEFAULT_KEY = ''
DEFAULT_KEY_FUNC = str

# --- HELPERS ---------------------------------------------------------------

def genkey(v, f = DEFAULT_KEY_FUNC):
    return f(v)

# --- ITEMS -----------------------------------------------------------------

class Vessel:
    def __init__(self,
                 value: Any = None,
                 data: Any = None
    ):
        self._key = genkey(value)
        self._value = value
        self._data = data

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, arg: Any):
        if callable(arg):   self._data = arg(self._data)
        else:               self._data = arg

    @data.deleter
    def data(self):
        self._data = None

    def __eq__(self, other: Vessel):
        "Test whether items are equal"

        return (self.key == other.key and self.value == other.value)

    def __repr__(self):
        return f'{type(self).__name__}(value = {repr(self.value)}, key = {repr(self.key)}, data = {repr(self.data)})'

    def __str__(self):
        return self.key

    def __getattr__(self, name: str):
        "getter aliases"

        match name.lower():
            case 'k': return self.key
            case 'v': return self.value
            case 'd': return self.data

# --- FACTORY ---------------------------------------------------------------

class VesselCache(Collection):
    "Vessel cache"

    def __init__(self):
        self._pool = dict()

    def __contains__(self, item: Any):
        "For `in` query"

        key = None

        if isinstance(item, str):
            key = item
        elif isinstance(item, Vessel):
            key = item.key
        else:
            key = genkey(item)

        return key in self._pool

    def get(self, k: Any = DEFAULT_KEY) -> Vessel:
        """
        Get item from pool. String argument will return item with that key.
        Other argument will convert to string key and return item with that
        key.
        """
        if isinstance(k, Vessel):
            k = k.key
        elif not isinstance(k, str):
            k = genkey(k)

        return self._pool[k][0]

    def add(self, item: Vessel) -> int:
        """
        Add item to cache or increase item count.

        Return item count.
        """

        key = item.key

        if key in self:
            self._inc(key)
        else:
            self._pool[key] = [item, 1]

        return self.count(key)

    def _inc(self, key: str):
        self._pool[key][1] += 1

    def count(self, item: Optional[Vessel|str] = None) -> int:
        """
        Get item count. With no arguments get number of items in cache.
        """
        if item is None:
            return len(self._pool)
        else:
            key = item if isinstance(item, str) else genkey(item)
            return self._pool[key][1]

    def __len__(self):
        return self.count()

    def __iter__(self):
        return (item for key, item in self._pool)

    def __bool__(self):
        return True

class VesselFactory:
    """
    Factory for creating and caching items.

    Can turn off cache if just using to create items, but why do that?

    Can call instance as a shortcut for retrieving/creating items.
    """

    def __init__(self, cache: bool = True):
        self._cache = VesselCache() if cache else None

    @property
    def cache(self):
        return self._cache

    def create(self,
               value: Any = None,
               data: Any = None
    ) -> Vessel:
        """
        Create an item with `value` and optional `data`.

        Omitting `data` argument will not change existing data if item exists
        in the cache.
        """
        item: Vessel
        key = genkey(value)

        if self._cache:
            if key in self._cache:
                item = self._cache.get(key)
                if data is not None: item.data = data
            else:
                item = Vessel(value, data)
                self._cache.add(item)
        else:
            item = Vessel(value, data)

        return item

    def __call__(self, v: Any, d: Any = None) -> Vessel:
        return self.create(v, d)
