""" TriesonodeCache.py
----------------------
Class for caching Triesonode data.

CURRENTLY NOT USED
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Triesonode import Triesonode

class TriesonodeCache:
    "Cache for Triesonode data"

    def __init__(self, node: Triesonode, mult = 1):
        self._node = node
        self._mult = mult

        self.chars = list()
        self.counts = list()

    def refresh(self):
        children = self._node.children()
        self.chars = [c._value for c in children]
        self.counts = [c._count ** self._mult for c in children]

    def set_mult(self, mult):
        self._mult = 1
        return self
