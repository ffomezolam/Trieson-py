""" Triechery.py
----------------
Defines the Triechery class - a devious upgrade from Trieson!
"""

from typing import Optional, Any, Callable

import logging

from .Trieson import Trieson
from .Triecherynode import Triecherynode
from . import combos

class Triechery(Trieson):
    """
    Trie Class with more treacherous motivations.

    Inherits from Trieson.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._root = Triecherynode()

    def add(self,
            item: Any,
            # TODO: extend to allow per-node data
            data: Any = True,
            proc = None):
        pass
