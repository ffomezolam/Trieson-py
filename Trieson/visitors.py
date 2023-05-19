""" visitors.py
---------------
Classes and functions for visiting Triesonodes
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Callable

from .Triesonode import AbstractTriesonode, Triesonode, TriesonodeTerminator
from .Trietor import Trietor
from .items import AbstractItem, CharItem

#--- MIXIN ------------------------------------------------------------------

class Visitable():

    @abstractmethod
    def accept(self, visitor: AbstractNodeVisitor):
        pass

#--- ABSTRACT BASE CLASS ----------------------------------------------------

class AbstractNodeVisitor(ABC):

    @abstractmethod
    def visit_node(self, node: Triesonode):
        pass

    @abstractmethod
    def visit_terminator(self, node: TriesonodeTerminator):
        pass

class PrintKeyVisitor(AbstractNodeVisitor):

    def __init__(self):
        self.level = 0

    def _visit(self, node: AbstractTriesonode):
        if node.key: print("  " * self.level, node.key)

        self.level += 1

        for c in node: c.accept(self)

        self.level -= 1

    def visit_node(self, node: Triesonode) -> None:
        self._visit(node)

    def visit_terminator(self, node: TriesonodeTerminator) -> None:
        self._visit(node)

class TraverseNodesVisitor(AbstractNodeVisitor):

    def __init__(self, proc: Callable = None):
        self.proc = proc
        self.node = None

    def visit_node(self, node: Triesonode):
        for childnode in node:
            if self.proc: self.proc(childnode)
            childnode.accept(self)

    def visit_terminator(self, node: TriesonodeTerminator):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        return 'a'

class TraverseSequenceVisitor(AbstractNodeVisitor):

    def __init__(self, seq: str|Sequence[AbstractItem]|Trietor, proc: Callable = None):

        # if string, convert to character sequence
        if isinstance(seq, str): seq = [CharItem(c) for c in seq]

        # if sequence, convert to Trietor instance
        if not isinstance(seq, Trietor): seq = Trietor(seq)

        self.seq = seq
        self._ix = 0
        self.proc = proc

    def visit_node(self, node: Triesonode):
        "Traverse nodes matching `seq`"

        if self.seq:
            # get key for lookup
            item = self.seq[self._ix]

            if not node.has(item): return None

            if proc: proc(node[item])


        for item in self.seq:

            if not node.has(item): return None

            if proc: proc(node[item])

            node = node[item]

        return node

    def visit_terminator(self, node: TriesonodeTerminator):
        pass
