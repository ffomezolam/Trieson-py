""" traversers.py
---------------
Classes and functions for traversing Tries
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from collections.abc import Iterator

from abc import ABC, abstractmethod

from .Trietor import Trietor
from .items import AbstractItem, CharItem

if TYPE_CHECKING:
    from .Triesonode import AbstractTriesonode

#--- MIXIN ------------------------------------------------------------------

class Traversable():

    def traverse(self, traverser: AbstractTraverser|Callable[[AbstractTriesonode], Any]):
        if isinstance(traverser, Callable):
            traverser = CallableTraverser(traverser)

        yield from traverser.traverse(self)

#--- ABSTRACT BASE CLASS ----------------------------------------------------

class AbstractTraverser(ABC):

    @abstractmethod
    def traverse(self, node: AbstractTriesonode):
        pass

#--- TRAVERSERS -------------------------------------------------------------

class CallableTraverser(AbstractTraverser):
    "Traverser that calls an arbitrary function on each child node"

    def __init__(self, proc: Callable[[AbstractTriesonode], Any] = None):
        self.proc = proc if proc else lambda x: x

    def traverse(self, node: AbstractTriesonode):

        for child in node:
            yield self.proc(child)
            yield from self.traverse(child)

class LevelTraverser(AbstractTraverser):
    "Traverser that yields each child node and trie level"

    def __init__(self, termstr: Optional[str] = None):
        self.level = 0

    def traverse(self, node: AbstractTriesonode):

        for child in node:

            yield (child, self.level)

            self.level += 1

            yield from self.traverse(child)

            self.level -= 1

class SequenceTraverser(AbstractTraverser):
    "Traverser that yields each node in a sequence"

    def __init__(self, seq: str|Sequence[AbstractItem]|Trietor):
        if isinstance(seq, str): seq = [CharItem(c) for c in seq]

        self.seq = seq

    def traverse(self, node: AbstractTriesonode):

        for item in self.seq:
            node = node[item]
            yield node
            if not node: return

class RandomTraverser(AbstractTraverser):
    "Traverser that yields random nodes by weight"

    def __init__(self,
                 weight: int|float = 1,
                 terminators: str|Sequence[AbstractItem|str]|Trietor = [],
    ):
        self.weight = weight

        if isinstance(terminators, str):
            terminators = [c for c in terminators]
        else:
            terminators = [getattr(item, 'key', item) for item in terminators]

        self.terminators = terminators

    def traverse(self, node: AbstractTriesonode):
        node = node.get(weight = self.weight)

        if not node or node.key in self.terminators: return

        yield node

        yield from self.traverse(node)
