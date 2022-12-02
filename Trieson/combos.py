""" combos.py
-------------
helper module with functions for extracting combinations from input sequences
"""

def seq_all(seq, min=2):
    slen = len(seq)
    return (seq[i:j] for i in range(slen) for j in range(i + 1, slen + 1) if (j - i) >= min)

def seq_to_end(seq, min=2):
    slen = len(seq)
    return (seq[i:] for i in range(slen) if (slen - i) >= 2)

def none(seq):
    return [seq]
