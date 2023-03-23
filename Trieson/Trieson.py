""" Trieson.py
--------------
Trie class
"""

from typing import Optional, Any

import os # for environment variable access
import logging

if os.getenv('DEBUG'): logging.getLogger(__name__).setLevel(logging.DEBUG)

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
             prefix: Optional[str] = None,
             weight: float|int = 1,
             lookahead: int = 0,
             *,
             max_len: int = 0, # maximum word length
             min_len: int = 0, # minimum word length
             strict: bool = True, # whether to be strict with endings
             fail_str: str = '!', # string to prepend if strict and failed
             end_char: Optional[str] = '' # character to interpret as an ending
    ):
        "Make a random word"

        # max_len can't be less than min_len unless it's 0
        if max_len and max_len < min_len:
            max_len, min_len = min_len, max_len # swap them

        word = []
        ends = set()

        # get starting node
        node = self._get_node_at_prefix(prefix, lambda n: word.append(n._value))

        lookahead = [lookahead for _ in range(3)]

        while node:
            # 1. set lookahead - can't be more than word length
            lookahead[2] = lookahead[1] if (lookahead[1] and len(word) > lookahead[1]) else len(word)

            # 2a. update prefix to find next letter
            prefix = ''.join(word[-lookahead[2]:])

            # 2b. get node corresponding to last char of prefix
            node = self._get_node_at_prefix(prefix)

            if not node:
                # prefix doesn't have children
                # increase lookahead to see if we can get a hit

                if lookahead[2] >= len(word):
                    # can't get any more characters from the trie

                    if strict: word.insert(0, fail_str)

                    break

                else:
                    lookahead[1] += 1
                    continue

            lookahead[1] = lookahead[0]

            # 2c. get next node
            node = node.get(weight = weight, exclude_chars = ends)

            # 2d. check if node exists
            # if so, add character to word
            if node:
                # add character to word
                word.append(node._value)

            logging.debug(f'MAKE() added {node._value} (prefix {prefix}, word {"".join(word)}')

            # 3. check for stop condition

            # 3a. word equals or exceeds max-length
            if max_len and len(word) >= max_len:
                # if word equal max-length and we are at terminating node, end
                if len(word) == max_len and (node.is_terminator() or node.has_terminator()) or (end_char and node._value == end_char):
                    break

                if len(word) > max_len:
                    # word is longer than max-length and no terminating node
                    # force word to length and end
                    word.pop()

                    if strict:
                        word.insert(0, fail_str)

                    break

            # 3b. end_char or terminating node was reached
            if (end_char and word[-1] == end_char) or node.is_terminator():
                logging.debug(f'MAKE() stop condition reached: {end_char if word[-1] == end_char else node.data()}')

                # word length OK so can end
                if len(word) >= min_len:
                    break

                # word length needs to be longer
                # remove last letter and add to exclusion set
                ends.add(word.pop())

        return ''.join(word)

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
