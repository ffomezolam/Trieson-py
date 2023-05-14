""" Trieson.py
--------------
Trie class
"""

from __future__ import annotations

from typing import Optional, Any, Callable
from collections.abc import Sequence

import logging

from .Triesonode import Triesonode, DEFAULT_KEY_FUNC
from .Trietor import Trietor
from . import combos
#from . import strategies

#--- CONSTANTS --------------------------------------------------------------

ITEM_SPEC_CHARS = ('k','v','d','K','V','D')
ITEM_SPEC_ATTRS = { 'k': 'key', 'v': 'value', 'd': 'data' }

#--- HELPERS ----------------------------------------------------------------

def format_return_item_spec(return_items: str|Sequence[str] = 'v', as_str: bool = False):
    # collect return item specifiers
    return_items = [i[0].lower() for i in return_items if i.startswith(ITEM_SPEC_CHARS)]

    # as_str must be false if we have more than one item or first item is not k
    if len(return_items) == 1 and return_items[0] != 'k': as_str = False

    return return_items, as_str

def get_node_attr(spec: str, node: Triesonode):
    return getattr(node, ITEM_SPEC_ATTRS[spec])()

#--- CLASS DEFINITION -------------------------------------------------------

class Trieson:
    """
    Trieson class with triesonous intent. Allows for weighted random traversal
    of arbitrary data. Can be used not only with characters of words, but any
    arbitrary data type, whether separate or mixed. Keys are automatically
    generated from objects via a specified function (`__repr__()` by default)
    unless the added data is a string, in which event the string is both the
    key and the value. Items may be obtained by key or value.

    Constructor Parameters
    ----------------------
    proc: callable
        Optional preprocessing function for added strings
    proc_args: list|tuple
        Arguments for preprocessing function
    proc_kwargs: dict
        Keyword arguments for preprocessing function
    """
    # TODO: maybe `on_add` event method - for logging additional data?
    # TODO: matches should return separate Match object which allows for
    # gathering various data from matches

    # CONSTRUCTOR ------------------------------------------------------------

    def __init__(self,
                 proc = None,
                 proc_args: list|tuple = [],
                 proc_kwargs: dict = {},
                 *,
                 key_func: Callable[[Any], str] = DEFAULT_KEY_FUNC
    ):
        self._root = Triesonode()
        self._depth = 0
        self.dict = set()
        self._proc = {
            "proc": proc or combos.seq_to_end,
            "args": proc_args,
            "kwargs": proc_kwargs
        }
        self._key_func = key_func

    # GET/SET/QUERY METHODS --------------------------------------------------

    def add(self,
            sequence: Any,
            # TODO: extend to allow per-node data
            data: Any = True,
            *,
            proc: Optional[Callable[[Sequence[Any], ...], Sequence[Any]]] = None,
            proc_args: list|tuple = [],
            proc_kwargs: dict = {},
            key_func: Optional[Callable[[Any], str]] = None
    ):
        """
        Add sequence to Trie, associate with data.

        Parameters
        ==========
        data: Any (default True)
            Data to associate with sequence

        Keyword-Only Parameters
        -----------------------
        proc: [Callable] (default None)
            Optional procedure to call on sequence before adding to trie. Must
            accept sequence as first argument and return a list of sequences to
            add.

        proc_args: [list|tuple] (default [])
            Optional additional positional arguments to `proc`.

        proc_kwargs: [dict] (default {})
            Optional additional keyword arguments to `proc`.

        key_func: [Callable] (default __repr__())
            Optional procedure to convert sequence item to string key. This is
            called on each item in the sequence.
        """

        # default proc if none
        proc = proc or self._proc['proc']
        proc_args = proc_args or self._proc['args']
        proc_kwargs = proc_kwargs or self._proc['kwargs']

        # default key_func if none
        key_func = key_func or self._key_func

        # add sequence as string to dict
        self.dict.add(sequence if type(sequence) is str else ''.join(key_func(item) for item in sequence))

        # apply proc function to sequence
        sequence = [ps for ps in proc(sequence, *proc_args, **proc_kwargs)]

        # add items for each sequence
        for subseq in sequence:
            node = self._root
            depth = 0

            for item in subseq:
                node = node.add(item, key_func = key_func)
                depth += 1

            node.terminate(data)

            if depth > self._depth: self._depth = depth

        return self

    def _get_node_at_prefix(self, prefix: Sequence[Any] = '', proc: Callable[Triesonode, Any] = None):
        "Get node corresponding to final item of prefix"

        if not prefix: return self._root

        # start at root node
        node = self._root

        # traverse trie
        for item in prefix:
            node = node[item]
            if not node: return None
            if proc: proc(node)

        return node

    def has_prefix(self, prefix: Sequence[Any]):
        "Check for any sequence of items in Trie"

        return bool(self._get_node_at_prefix(prefix))

    def has(self, seq: Sequence[Any]):
        "See if string is in Trie"

        node = self._root
        for item in seq:
            node = node[item]
            if not node:
                return False

        return node.has_terminator()

    def get(self,
            seq: Optional[Sequence[Any]] = None,
            *,
            partial: bool = False,
            proc: Optional[Callable[[Triesonode], Any]] = None
    ) -> Trietor:
        "Get data associated with sequence items"

        # generate random sequence if not specified
        if seq is None: return self.make(proc = proc)

        # prepare container
        t = Trietor()

        # start at root node
        node = self._root

        # traverse trie
        for item in seq:
            node = node[item]

            # if `seq` not in trie, return empty match unless `partial` is True
            if not node:
                if partial: return t
                else: return Trietor()

            if proc: proc(node)

            t.add(node.key(), node.value(), node.data())

        # get terminating node, or return based on `partial` argument
        if node.has_terminator():
            t.terminate(node.get_terminator().data())
            return t
        else:
            if partial: return t
            return Trietor()

    def subsequences(self,
                     prefix: Optional[Sequence[Any]] = None,
                     limit: Optional[int] = None
    ) -> Trietor:
        """
        Traverse trie, yielding all subsequences of `prefix`.

        Parameters
        ==========

        prefix: [Sequence] - default None
            The prefix to precede the returned subsequences

        limit: [int] - default None
            Limit the number of returned subsequences
        """

        seq = [] # list to hold visited items
        count = 0 # number of subsequences found
        limit = limit if limit else 0 # count limit

        root = self._get_node_at_prefix(prefix) if prefix else self._root

        # preprocessing function to add item to sequence
        def preproc(node):
            seq.append(node)

        # postprocessing function to remove item from sequence
        def postproc(node):
            seq.pop()

        # traverse nodes
        for node in root.traverse(preproc, postproc):

            # if terminating node reached, yield sequence
            if node.is_terminator():
                count += 1 # increment success count

                # yield data as Trietor instance
                yield Trietor([(node.key(), node.value(), node.data()) for node in seq[:-1]], seq[-1].data())

            # break if we've reached limit
            # TODO: Do we need this if we're doing this as a generator?
            if limit and count >= limit: break

    def substrings(self, prefix = None, limit = None):
        "Alias for subsequences()"

        return self.subsequences(prefix, limit)

    def subseqs(self, prefix = None, limit = None):
        "alias for subsequences()"

        return self.subsequences(prefix, limit)

    def match_strings(self, prefix: str, limit: Optional[int] = None):
        "Alias for match() but string-specific"
        return match(prefix, limit, return_items = 'k', as_str = True)

    def match(self,
              sequence: str|Sequence[Any],
              limit: Optional[int] = None,
    ) -> Trietor:
        "Get possible matches to sequence, max <limit>"

        if not self.has_prefix(sequence):
            yield Trietor()

        else:
            prefix = self.get(sequence, partial=True)

            for sub in self.subsequences(sequence, limit):
                yield prefix + sub

    def make(self,
             prefix: Sequence = [],
             weight: float|int = 1,
             lookahead: int = 0,
             *,
             max_len: int = 0, # maximum output length
             min_len: int = 0, # minimum output length
             strict: bool = True, # whether to be strict with endings
             fail_item: Any = '', # if set, prepend item instead of returning empty
             end_items: Sequence = '', # item(s) to interpret as an ending
             proc: Optional[Callable[[Triesonode], Any]] = None
    ) -> Trietor:
        """
        Make a random sequence.

        Uses node weights to weight the generator towards higher-frequency
        nodes. The `weight` parameter allows the degree of this weighing to
        be adjusted.

        Positional Parameters
        =====================

        prefix: [Sequence]
            Optional prefix sequence to use. Make will generate output starting
            after the prefix. No prefix will start from the trie root.

        weight: [float|int] (default 1)
            Adjust the weights. 1 is normal weighting. 0 is all weights equal.
            2 is double weighting. Etc.

        lookahead: [int] (default 0)
            Number of items to use when choosing next node.
            This essentially acts as a `prefix` designator for the algorithm.
            At each step in the process, the algorithm will use the last
            `lookahead` number of items in the generated word to select
            the next item. A `lookahead` of 0 will always use the whole
            set of generated items, effectively only generating sequences from
            the original set of inputs.

        Keyword Parameters
        ==================

        max_len: [int] (default 0)
            Maximum generated output length. A 0 here acts as no maximum.

        min_len: [int] (default 0)
            Minimum generated output length. A 0 here acts as no minimum.

        strict: [bool] (default True)
            Whether to be strict with sequence endings. If the generator reaches
            `max_len` without getting a terminating node, it will return an
            empty sequence if `strict` is `True`.

        fail_item: [Any] (default '')
            If provided, instead of failing with an empty sequence, the failing
            sequence will be returned with `fail_item` prepended.

        end_items: [Sequence]
            The algorithm will interpret the item(s) specified in the
            `end_items` parameter as terminating items, and will treat them
            identically to the standard sequence-terminating node. By default
            `end_items` is disabled.
        """

        # if no entries in trie, return empty result
        if not len(self._root): return Trietor()

        # max_len can't be less than min_len unless it's 0
        if max_len and max_len < min_len:
            max_len, min_len = min_len, max_len # swap them

        # if prefix doesn't exist in trie, return empty result
        if prefix and not has_prefix(prefix): return Trietor()

        # get prefix items
        prefix_items = self.get(prefix, partial=True) if prefix else Trietor()

        # generated items will be stored in Trietor instance
        generated_items = Trietor()

        # reserve identifier for a copy of items necessary in certain instances
        cached_items = None

        # log start of algorithm
        logging.debug(f'START: prefix {prefix_items.as_str()}')

        # modified lookahead to preserve original setting
        lookahead_mod = lookahead

        count = 0
        while count < 5:
            # (1) INITIALIZE

            # pre-calculate relevant sequence lengths
            prefix_length = len(prefix_items)
            generated_length = len(generated_items)
            total_length = prefix_length + generated_length

            # adjust lookahead - can't be more than word length
            if lookahead_mod and lookahead_mod > total_length:
                lookahead_mod = total_length

            # set prefix based on lookahead
            prefix = (prefix_items + generated_items).values()[-lookahead_mod:]

            # log prefix at start of loop
            logging.debug(f'> PREFIX: {prefix}')

            # (2) GET STARTING NODE AND VALIDATE

            # get node corresponding to last item of prefix
            node = self._get_node_at_prefix(prefix)

            # if invalid node, prefix does not exist in trie
            if not node:
                logging.debug(f'* no children for prefix {prefix} with lookahead {lookahead_mod}/{lookahead}')

                # if lookahead is >= word length, then can't get any more items
                if lookahead_mod >= total_length:
                    logging.debug(f'* > lookahead is at maximum - operation failed')

                    # if strict mode, then fail
                    if strict:

                        # if fail_item specified, return with fail_item prepended
                        if fail_item and cached_items: pass # return fail item + prefix item + cache item

                        # ...otherwise return empty result
                        return Trietor()

                    # ...otherwise return what we've got and call it a day
                    else:
                        pass

                    break

                # otherwise can try increasing lookahead to permit more choices
                else:
                    logging.debug(f'* > increasing effective lookahead from {lookahead_mod} to {lookahead_mod + 1}')

                    lookahead_mod += 1

                    continue

            # ... otherwise node is valid - reset lookahead for next cycle
            else:
                logging.debug(f'* resetting lookahead from {lookahead_mod} to {lookahead}')
                lookahead_mod = lookahead

            # (4) GET NEXT NODE AND VALIDATE

            logging.debug(f'> getting next node for prefix {prefix} and tried items <NOT IMPLEMENTED>')
            node = node.get(weight=weight, exclude = None)

            # if nothing returned then can't get any additional items from this
            # prefix - have to try another option
            if not node:
                # remove item in hopes that previous item will have more options
                pass
                # continue

            # (5) CHECK FOR STOP CONDITION

            # debug
            count += 1

        """
        while True:
            # 0. word list needs at least one character otherwise no way to
            #    generate a complete word
            if not word:
                logging.debug(f'no further options for generation with min_len {min_len} and max_len {max_len}')

                if strict:
                    if fail_item and cache: return fail_item + prefix + cache
                    return ''
                else:
                    return prefix + cache

            # 1. set lookahead - can't be more than word length
            if lookahead[1] and len(plist) + len(word) + 1 < lookahead[1]:
                lookahead[1] = len(plist) + len(word) + 1

            # 2a. update prefix to find next letter
            prefix = join_word((plist + word))[-lookahead[1]:]

            # 2b. get node corresponding to last char of prefix
            node = self._get_node_at_prefix(prefix)

            if not node:
                # prefix does not exist in trie
                # increase lookahead to see if we can get a hit
                # needed in event we have i.e. one string in trie, proc
                # combos.none, and lookahead less than string length

                logging.debug(f'* no children for prefix {join_word(word)} with lookahead {lookahead}')

                if lookahead[1] >= len(word) - 1 + len(plist):
                    # can't get any more characters from the trie
                    if strict:
                        if fail_item and cache: return fail_item + prefix + cache
                        return ''
                    else:
                        return prefix + cache

                    break

                else:
                    # increase lookahead
                    logging.debug(f'\tincreasing effective lookahead from {lookahead[1]} to {lookahead[1] + 1}')
                    lookahead[1] += 1

                    continue
            else:
                # reset lookahead
                lookahead[1] = lookahead[0]

            # 2c. get next node
            logging.debug(f'getting next char with prefix "{prefix}" and tried characters {word[-1]["tried"] if word else set()}')

            node = node.get(weight = weight, exclude_chars = word[-1]["tried"] if word else set())

            # 2d. check if node exists
            if node and not node.is_terminator():
                # exists so add character to word
                if word: word[-1]["tried"].add(node._value)
                word.append(char(node._value))
                logging.debug(f'> added {node._value} for prefix {prefix}')
            elif not node:
                # node not existing means we've exhausted all options
                # so remove character in hopes that previous character will
                # have more options
                word.pop()
                continue

            # store current word length
            wlen = len(word) - 1 + len(plist)

            # if we've reached max length end if possible else cache word
            # TODO: wrap this into stop condition check
            if max_len and wlen == max_len:
                cache = join_word(word)
                logging.debug(f'\t> cached "{cache}"')

            # 3. check for stop condition
            if max_len and wlen == max_len and node.has_terminator():
                # reached maximum length and have a full word - we can end here
                return join_word(plist + word)

            elif node.is_terminator() or (end_items and node._value in end_items):
                # at terminating node - check if we can end here
                logging.debug(f'reached terminating node at prefix {prefix}')

                # 3a. check if word is too small
                if min_len and wlen < min_len:
                    logging.debug(f'* word "{"".join([c["char"] for c in word])}" is too short')

                    # add to cache if larger than previous cached word
                    if len(cache) < wlen:
                        cache = join_word(word)
                        logging.debug(f'\t> cached "{cache}"')

                    # remove character from word to try another
                    word.pop()
                    continue

                # 3b. check if word is too big
                if max_len and wlen > max_len:
                    logging.debug(f'* word "{"".join([c["char"] for c in word])}" is too long')

                    # add to cache if smaller than previous cached word
                    if not cache or wlen < len(cache):
                        cache = join_word(word)
                        logging.debug(f'\t> cached "{cache}"')

                    # shorten word to 1 less than max length to try another character
                    word = word[:max_len - len(plist)]
                    continue

                logging.debug(f'made word "{join_word(plist + word)}"')
                return join_word(plist + word)
        """

    def depth(self):
        "Get trie depth"

        return self._depth

    # MAGIC ------------------------------------------------------------------

    def __contains__(self, seq):
        "Check if sequence in Trie"

        return self.has(seq)

    def __getitem__(self, seq):
        "Alias for get(seq)"

        return self.get(seq)

    def __setitem__(self, string, data):
        "Add item to Trie and associate with data"

        self.add(string, data)

    def __len__(self):
        "Get number of full sequences in Trie"

        return len(self.dict)

    def __iter__(self):
        "Iterate through all sequences in Trie"

        for s in self.substrings():
            yield s

    def __bool__(self):
        "Considered True if has entries, False otherwise"

        return bool(len(self))

    # STRING -----------------------------------------------------------------

    def __repr__(self):
        "String representation"
        return f'Trieson()'

    def __str__(self):
        "Pretty string representation"
        return f'Trieson - depth {self.depth()}'
