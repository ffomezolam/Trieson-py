# Trieson

A Trie class implemented in python, with added rebellious features (namely
weighted random traversal).

*Near stable release, but still under final testing and development.*

## Usage

Load the `Trieson` package:

`from Trieson import Trieson`

Instantiate:

`trie = Trieson() # by default will create additional strings - see combos.py`

Add strings:

`trie.add(['apple', 'apiary', 'apply', 'apricot'])`

Generate a random word:

`random_word = trie.make()`

Have lots of fun!

## License

MIT Public License. See `license.txt` for details.
