""" strategies.py
-----------------
Implements strategies for generating sequences.
"""

from __future__ import annotations

import logging

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from typing import Any, Self, Callable, Optional
from collections.abc import Sequence

from .Trieson import Trieson
from .Trietor import Trietor
from .Triesonode import Triesonode

class AbstractMakeStrategy(ABC):
    "Abstract base class for Trieson make() strategies"

    def __init__(self, trie: Trieson):
        if not isinstance(trie, Trieson): raise TypeError("Invalid trie type! Must pass Trieson instance")
        if not trie: raise ValueError("Trie is empty! Cannot pass empty trie")

        self.trie = trie

    @abstractmethod
    def apply(self,
              prefix: Sequence = [],
              weight: float|int = 1,
              lookahead: int = 0
    ) -> Trietor:
        "Generate and return the final sequence as Trietor instance"

        pass

class ArbitraryMakeStrategy(AbstractMakeStrategy):
    "Strategy for arbitrary element types"

    @dataclass
    class GenItems:
        _post: Trietor = field(default_factory=Trietor, init=False)
        _pre: Trietor = field(default_factory=Trietor, init=False)
        _visited: list = field(default_factory=list, init=False)

        def __len__(self) -> int:
            return len(self.pre) + len(self.post)

        def join(self) -> Trietor:
            return self.pre + self.post

        def clear(self) -> self:
            self.post.clear()
            self.pre.clear()

            return self

        @property
        def post(self) -> Trietor:
            return self._post

        @property
        def pre(self) -> Trietor:
            return self._pre

        @property
        def visited(self) -> list:
            if not len(self._visited): self._visited.append(Trietor())

            return self._visited[-1]

        def add(self, item: Any) -> Self:
            "Add item to post container"

            logging.debug(f'  * adding {item} to {self.join()}')
            self.post.append(item)
            self.visited[-1].append(item)

            return self

        def __iadd__(self, item: Any):
            "Alias for add()"

            self.add(item)

    @dataclass
    class Lookahead:
        items: ArbitraryStrategy.GenItems
        original: int = field(default=0, init=False)
        current: int = field(default=0, init=False)

        def init(self, v: int) -> Self:
            self.original = v
            self.set()
            return self

        def limit(self) -> Self:
            if self.out_of_bounds():
                self.current = len(self.items)

            logging.debug(f'\t* lookahead set to {self.current} (original {self.original})')

            return self

        def set(self, v: Optional[int] = None) -> Self:
            if v is None: v = self.original
            self.current = v

            return self.limit()

        def reset(self) -> Self:
            self.set()

            return self

        def out_of_bounds(self, inc = False) -> bool:
            "Test whether lookahead exceeds word length"

            if (self.current and
                ((self.current > len(self.items) or
                (self.current == len(self.items and inc))))
            ):
                return True

            return False

    @dataclass
    class MinMax:
        _min: int = field(default=0, init=False)
        _max: int = field(default=0, init=False)

        def _validate(self) -> Self:
            "Ensure min is less than max if neither are 0"

            if self._min and self._max and self._min > self._max:
                self._min, self._max = self._max, self._min

            return self

        def _set(self, attr: str, v: int) -> Self:
            setattr(self, '_' + attr, v)
            return self._validate()

        def minmax(self, min: Optional[int] = None, max: Optional[int] = None) -> Self:
            if min is not None: self.min(min)
            if max is not None: self.max(max)

            return self

        @property
        def min(self) -> int:
            return self._min

        @min.setter
        def min(self, v: int) -> Self:
            return self._set('min', v)

        @property
        def max(self) -> int:
            return self._max

        @max.setter
        def max(self, v: int) -> Self:
            return self._set('max', v)

    def __init__(self, trie: Trieson):
        super().__init__(trie)

        # item collections
        self.gen = ArbitraryMakeStrategy.GenItems()
        self.cache = None

        # generation options
        self.weight = 1
        self.lookahead = ArbitraryMakeStrategy.Lookahead(self.gen)

        # validation options
        self.stopitems = []
        self.limits = ArbitraryMakeStrategy.MinMax()
        self.strict = True
        self.failitem = None

    def init(self,
             weight: Optional[float|int] = None,
             lookahead: Optional[int] = None,
             *,
             maxlen: Optional[int] = None,
             minlen: Optional[int] = None,
             strict: Optional[bool] = None,
             failitem: Optional[Any] = None,
             stopitems: Optional[Sequence] = None,
             proc: Optional[Callable[[Triesonode], Any]] = None
    ) -> Self:
        "Initialize instance variables"

        # set weight
        if weight is not None: self.weight = weight

        # set lookahead
        if lookahead is not None: self.lookahead.init(lookahead)

        # set limits
        self.limits.minmax(minlen, maxlen)

        # set strict
        if strict is not None: self.strict = strict

        # set failitem
        if failitem is not None: self.failitem = failitem

        # set stopitems
        if stopitems is not None: self.stopitems = stopitems

        # proc
        # TODO

        return self

    def apply(self, prefix: Optional[Sequence[Any]] = None) -> Trietor:
        "Run algorithm"

        # clear any previously generated items
        self.gen.clear()
        self.cache = None

        # if prefix supplied, get and store - throw error if not in trie
        if prefix is not None:
            if not self.trie.has_prefix(prefix):
                raise ValueError(f"Prefix {prefix} does not exist in trie")
            else:
                self.gen.pre.clear().append(self.trie.get(prefix, partial=True))

        # log start of algo
        logging.debug(f'> START: prefix {self.gen.pre.as_str()}')

        # success flag
        success = False

        # MAIN LOOP
        count = 1
        while count <= 100:
            logging.debug(f'LOOP START ({count})')
            # (1) INIT GENERATOR PARAMS

            # limit lookahead to word length
            self.lookahead.limit()

            # get new prefix based on lookahead
            prefix = self.gen.join().values()[-self.lookahead.current:]

            # (2) GET STARTING NODE AND VALIDATE

            # get node corresponding to last item of prefix
            node = self.trie._get_node_at_prefix(prefix)
            logging.debug(f'> PREFIX: {prefix}, last node: {node}')

            # if invalid node, prefix does not exist in trie
            if not node:
                logging.debug(f'\t! prefix {prefix} (lookahead {self.lookahead}) does not exist in trie!')

                # if lookahead is at maximum, then algorithm has failed - there
                # is no entry in the trie for the sequence starting at prefix
                # start and ending at generated sequence end
                if self.lookahead.out_of_bounds(True):

                    # generate best possible item
                    # TODO

                    # if strict mode on, then fail
                    if strict:

                        # if failitem specified then prepend failitem and return
                        if fail_item:
                            # TODO
                            pass

                    # end loop
                    break

                # ... otherwise we can increase lookahead and try again
                # - needed in event that substrings are not all included in
                # root of trie, for example: 'app' is only string in trie from
                # root and algorithm tries to generate next char with prefix of
                # 'ap' and lookahead 1; it will look for 'p' at root of trie
                # but 'p' does not exist, so can backtrack to 'ap' to get valid
                # next node of 'p'
                else:
                    logging.debug(f'\t! increasing lookahead from {self.lookahead} to {self.lookahead + 1}')

                    self.lookahead.current += 1

                    # restart loop
                    continue

            # ... otherwise node is valid
            else:
                # reset lookahead
                self.lookahead.reset()

            # (3) GENERATE NEXT NODE AND VALIDATE

            node = node.get(weight = self.weight, exclude = self.gen.visited.keys())
            logging.debug(f'> NEXT: {node}')

            # if nothing returned then can't get additional items from this
            # prefix - have to try another option
            if not node:
                logging.debug(f'\t! options exhausted for node {node}')

                # remove last item to try to generate another item
                self.gen.post.pop()
                continue

            # otherwise node is valid - if not terminator can add to generated
            if not node.is_terminator():
                logging.debug(f'\t* adding {node.key()} to {self.gen.join().as_str()}')

                # add to generated items collection
                self.gen.add([(node.key(), node.value(), node.data())])

            # (4) CHECK FOR STOP CONDITION

            # (a) node is terminating node or node key/value in stopitems collection
            if (node.is_terminator() or
                (self.stopitems and
                    (node.value() in self.stopitems or
                     node.key() in self.stopitems)
                )
            ):
                logging.debug(f'> STOP: got terminating node')

                # if sequence too short then need to try a different item
                if self.limits.min and len(self.gen) < self.limits.min:
                    logging.debug(f'\t! sequence length {len(self.gen)} too short with min {self.limits.min}')

                    # cache sequence if longer than previous cached sequence
                    if len(self.gen) > len(self.cache):
                        self.cache = self.gen.join()
                        logging.debug(f'\t! cached {self.cache}')

                    # remove item from sequence to try another
                    self.gen.post.pop()
                    continue

                # ... otherwise we are OK and can return generated sequence
                else:
                    success = True

            # (b) we have a specified maximum limit
            elif self.limits.max:

                # (b1) generated sequence is at specified limit
                if len(self.gen) == self.limits.max:

                    # if node has terminator then we can consider this the end
                    if not node.has_terminator():
                        success = True

                    # ... otherwise we'll be too long next round,
                    else:
                        self.gen.post.pop()
                        continue

                # (b2) generated sequence exceeds specified limit
                elif len(self.gen) > self.limits.max:
                    pass

            if success:
                logging.debug(f'* GENERATED: {self.gen.join()}')
                return self.gen.join()

            logging.debug(f'LOOP END ({count})')
            logging.debug(f'  pre: {self.gen.pre}')
            logging.debug(f'  post: {self.gen.post}')
            logging.debug(f'  visited: {self.gen.visited}\n')

            count += 1
