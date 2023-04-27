""" Trietor.py
--------------
Defines the object that holds a Trieson query result
"""

from __future__ import annotations

from typing import Optional, Any
from collections.abc import Sequence

class Trietor:
    """
    Trietor class
    """

    def __init__(self, items: Optional[Sequence[Any]] = None):
        self.keys = []
        self.values = []
        self.data = []

    def add(self, key: str, value: Any, data: Any = None):
        pass

    def __getitem__(self):
        "Get item by key or value"
        pass

    def __len__(self):
        "Return length of results"
        pass

    def __repr__(self):
        "Programmatic string representation"
        pass

    def __str__(self):
        "Human-readable string representation"
        pass
