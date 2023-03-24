""" Trieson.py
--------------
Trie class
"""

from typing import Optional, Any

import os # for environment variable access
import logging

from .Triesonode import Triesonode
from . import combos

#--- CLASS DEFINITION -------------------------------------------------------

class Trieson():
    """
    Trie Class

    Constructor Parameters
    ----------------------
    proc: callable
        Optional preprocessing function for added strings
    proc_args: list|tuple
        Arguments for preprocessing function
    proc_kwargs: dict
        Keyword arguments for preprocessing function
    """

    # CONSTRUCTOR ------------------------------------------------------------

    def __init__(self, proc = None, proc_args: list|tuple = [], proc_kwargs: dict = {}):
        self._root = Triesonode()
        self._depth = 0
        self.dict = set()
        self._proc = {
            "proc": proc or combos.seq_to_end,
            "args": proc_args,
            "kwargs": proc_kwargs
        }

    # GET/SET/QUERY METHODS --------------------------------------------------

    def add(self,
            string: str|list,
            data: Any = True,
            proc = None,
            proc_args: list|tuple = [],
            proc_kwargs: dict = {}
    ):
        """
        Add string(s) to Trie, associate with data.

        Can pass a list of strings or a single string. `proc` argument
        will preprocess each string, and must return a string or list
        of strings to add.
        """

        # default proc if none
        proc = proc or self._proc['proc']
        proc_args = proc_args or self._proc['args']
        proc_kwargs = proc_kwargs or self._proc['kwargs']

        # convert to list input
        if type(string) == str: string = [string]

        # add to dict
        for s in string: self.dict.add(s)

        # apply proc function
        string = [ps for s in string for ps in proc(s, *proc_args, **proc_kwargs)]

        # add characters for each string
        for s in string:
            node = self._root

            depth = 0
            for c in s:
                node = node.add(c)
                depth += 1

            node.terminate(data)

            if depth > self._depth: self._depth = depth

        return self

    def _get_node_at_prefix(self, prefix: str, proc = None):
        "Get node corresponding to final charachter of prefix"

        if not prefix: return self._root

        # start at root node
        node = self._root

        # traverse trie
        for char in prefix:
            node = node[char]
            if not node: return None
            if proc: proc(node)

        return node

    def has_prefix(self, prefix):
        "Check for any sequence of characters in Trie"

        return bool(self._get_node_at_prefix(prefix))

    def has(self, string):
        "See if string is in Trie"

        node = self._root
        for char in string:
            node = node[char]
            if not node:
                return False

        return node.has_terminator()

    def get(self, string=None):
        "Get data associated with string"

        if not string: return self.make()

        # get node at conclusion of string
        node = self._get_node_at_prefix(string)

        if not node: return None

        # only return full strings
        if not node.has_terminator(): return None

        return node.get_terminator().data()

    def substrings(self, prefix = None, limit = None):
        "Collect and return all substrings"
        string = ''
        collection = []
        count = 0
        limit = limit if limit else 0
        root = self._get_node_at_prefix(prefix) if prefix else self._root

        # preprocessing function to add letter to string and check for word
        def preproc(node):
            nonlocal string, collection, count

            # add character to string (terminating character is '')
            string += node._value

            if node.is_terminator():
                # if we've reached a terminating node, add string to collection
                collection.append(string)
                count += 1

        # postprocessing function to remove letter from string
        def postproc(node):
            # only process if we're not at a terminating node
            if not node.is_terminator():
                nonlocal string
                string = string[:-1]

        for _ in root.traverse(preproc, postproc):
            if limit and count >= limit: break

        return collection

    def match(self, string, limit=None):
        "Get possible matches to string, max <limit>"

        if not self.has_prefix(string): return [string]

        return [string + sub for sub in self.substrings(string, limit)]

    def make(self,
             prefix: str = '',
             weight: float|int = 1,
             lookahead: int = 0,
             *,
             max_len: int = 0, # maximum word length
             min_len: int = 0, # minimum word length
             strict: bool = True, # whether to be strict with endings
             fail_str: str = '', # if set, prepend string instead of returning empty
             end_char: str = '' # character to interpret as an ending
    ):
        """
        Make a random word.

        Uses node weights to weight the generator towards higher-frequency
        nodes. The `weight` parameter allows the degree of this weighing to
        be adjusted.

        Positional Parameters
        =====================

        prefix: [str]
            Optional prefix string to use. Make will generate text starting
            after the prefix. No prefix will start from the trie root.

        weight: [float|int] (default 1)
            Adjust the weights. 1 is normal weighting. 0 is all weights equal.
            2 is double weighting. Etc.

        lookahead: [int] (default 0)
            Number of characters to use when choosing next node.
            This essentially acts as a `prefix` designator for the algorithm.
            At each step in the process, the algorithm will use the last
            `lookahead` number of characters in the generated word to select
            the next character. A `lookahead` of 0 will always use the whole
            set of generated characters, effectively only generating words from
            the original set of inputs.

        Keyword Parameters
        ==================

        max_len: [int] (default 0)
            Maximum generated word length. A 0 here acts as no maximum.

        min_len: [int] (default 0)
            Minimum generated word length. A 0 here acts as no minimum.

        strict: [bool] (default True)
            Whether to be strict with word endings. If the generator reaches
            `max_len` without getting a terminating node, it will return an
            empty string if `strict` is `True`.

        fail_str: [str] (default '')
            If provided, instead of failing with an empty string, the failing
            string will be returned with `fail_str` prepended.

        end_char: [str]
            The algorithm will interpret the character specified in the
            `end_char` parameter as a terminating character, and will treat it
            identically to the standard word-terminating node. By default
            `end_char` is disabled.
        """

        # max_len can't be less than min_len unless it's 0
        if max_len and max_len < min_len:
            max_len, min_len = min_len, max_len # swap them

        # characters will be stores as dict in form:
        # { "char": <the character>, "tried": <children accessed from this character> }

        # helper function to generate word entries
        def char(char):
            return { "char": char, "tried": set() }

        # helper function to join characters
        def join_word(word_list):
            return ''.join([w['char'] for w in word_list])

        backtrack_count = 0
        plist = [] # stores prefix characters
        word = [char('')] # stores generated characters - starts with a dummy character
        cache = '' # stores a copy of word in case of length failure

        # get starting node
        node = self._get_node_at_prefix(prefix, lambda n: plist.append(char(n._value)))

        # return if prefix doesn't exist in trie
        if not node: return ''

        logging.debug(f'START: prefix {join_word(plist)}')

        lookahead = [lookahead for _ in range(2)]

        while True:
            # 1. set lookahead - can't be more than word length
            if lookahead[1] and len(plist) + len(word) + 1 < lookahead[1]:
                lookahead[1] = len(plist) + len(word) + 1

            # 2a. update prefix to find next letter
            prefix = join_word((plist + word)[-lookahead[1]:])

            # 2b. get node corresponding to last char of prefix
            node = self._get_node_at_prefix(prefix)

            if not node:
                # prefix does not exist in trie
                # increase lookahead to see if we can get a hit
                # needed in event we have i.e. one string in trie, proc
                # combos.none, and lookahead less than string length

                logging.debug(f'* no children for prefix {"".join(word)} with lookahead {lookahead}')

                if lookahead[1] >= len(word):
                    # can't get any more characters from the trie
                    if strict: return ''

                    break

                else:
                    # increase lookahead
                    lookahead[1] += 1

                    continue
            else:
                # reset lookahead
                lookahead[1] = lookahead[0]

            # 2c. get next node
            logging.debug(f'getting next char with prefix "{prefix}" and tried characters {word[-1]["tried"] if word else set()}')

            node = node.get(weight = weight, exclude_chars = word[-1]["tried"])

            # 2d. check if node exists
            if node and not node.is_terminator():
                # exists so add character to word
                if word: word[-1]["tried"].add(node._value)
                word.append(char(node._value))
                logging.debug(f'added {node._value} for prefix {prefix}')
            elif not node:
                # node not existing means we've exhausted all options
                # so remove character in hopes that previous character will
                # have more options
                word.pop()
                continue

            # 3. check for stop condition
            if node.is_terminator() or (end_char and node._value == end_char):
                # at terminating node - check if we can end here
                logging.debug(f'reached terminating node at prefix {prefix}')

                # 3a. check if word is too small
                if min_len and (len(word) - 1 + len(plist)) < min_len:
                    logging.debug(f'* word "{"".join([c["char"] for c in word])}" is too short')

                    # add to cache if larger than previous cached word
                    if len(cache) < len(word) - 1:
                        cache = join_word(word)
                        logging.debug(f'\t> cached "{cache}"')

                    # remove character from word to try another
                    word.pop()
                    continue

                # 3b. check if word is too big
                if max_len and (len(word) - 1 + len(plist)) > max_len:
                    logging.debug(f'* word "{"".join([c["char"] for c in word])}" is too long')

                    # add to cache if smaller than previous cached word
                    if len(cache) > len(word) - 1:
                        cache = join_word(word)
                        logging.debug(f'\t> cached "{cache}"')

                    # shorten word to 1 less than max length to try another character
                    word = word[:max_len - len(plist) - 1]
                    continue

                # return word
                return join_word(word)

    def depth(self):
        return self._depth

    # MAGIC ------------------------------------------------------------------

    def __contains__(self, string):
        "Check if string in Trie"
        return self.has(string)

    def __getitem__(self, string):
        "Get data associated with string. Alias for get(string)"
        return self.get(string)

    def __setitem__(self, string, data):
        "Add item to Trie and associate with data"
        self.add(string, data)

    def __len__(self):
        "Get number of full strings in Trie"
        return len(self.dict)

    def __iter__(self):
        "Iterate through all strings in Trie"
        for s in self.substrings():
            yield s

    # STRING -----------------------------------------------------------------

    def __repr__(self):
        "String representation"
        return f'Trieson()'

    def __str__(self):
        "Pretty string representation"
        return f'Trieson - depth {self.depth()}'
