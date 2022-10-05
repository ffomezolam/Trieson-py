""" TriesonHistory.py
------------------
Exports a class that manages Trie character fetch history
"""

class TriesonHistory():
    def __init__(self, max_entries=1):
        self._max = max_entries
        self._history = []
        self._len = 0

    def new(self):
        if self._len >= self._max:
            self._history.pop(0)
            self._len -= 1

        self._history.append('')
        self._len += 1
        return self

    def add(self, char):
        self._history[-1] += char
        return self

    def get(self, n=None):
        if n == None: n = self._len - 1
        return self._history[-1]

    def clear(self):
        self._history = []
        self._len = 0
        return self
