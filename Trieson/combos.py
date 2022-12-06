""" combos.py
-------------
helper module with functions for extracting combinations from input sequences
"""

def seq_all(seq, min=2):
    """
    Return all sequential combinations of minimum [min] length as generator.
    Example (min 2): abcd -> [ab, abc, abcd, bc, bcd, cd]
    """
    slen = len(seq)
    return (seq[i:j] for i in range(slen) for j in range(i + 1, slen + 1) if (j - i) >= min)

def seq_to_end(seq, min=2):
    """
    Return sequential combinations of minimum [min] length to end of sequence as generator.
    Example (min 2): abcd -> [abcd, bcd, cd]
    """
    slen = len(seq)
    return (seq[i:] for i in range(slen) if (slen - i) >= 2)

def none(seq):
    "Return entire sequence as generator."
    return (seq for i in [0])

#--- SELF-TEST --------------------------------------------------------------
if __name__ == '__main__':
    seq = 'abcd'
    funcs = [seq_all, seq_to_end, none]

    for func in funcs:
        for n in range(2, 4):
            print(f'{func.__name__} ({n}): {list(func(seq))}')
