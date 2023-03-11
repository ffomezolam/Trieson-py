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

## Methods

### Trieson([proc]) (constructor)

The `proc` parameter is for an optional preprocessing function that will be
applied to any string added to the trie. By default it will create a list of
all combinations of sequential letters in the string to the end of the string.
For example: 'apple' will become ['apple', 'pple', 'ple', 'le']

### add(string, [data], [proc])

Adds the string `string` to the trie, applying `proc` to the string before
adding. The `data` parameter supplies any data to attach to the final character
in the string and a true value specifies that this character ends a string.

### `has_prefix(prefix)`

Check for any sequential sequence of characters in the trie. For example, if
'apple' was added to the trie (with no preprocessing), has_prefix('ap') and
has_prefix('app') would return True, but has_prefix('apo') would return False.

### `has(string)`

Check if the full string `string` is in trie. This will only return True if the
final character in `string` has a True-equivalent `data` value in the trie.

### `get(string)`

Gets the `data` value associated with the final character in `string`.

### `substrings([prefix], [limit])`

Gets `limit` or all substrings starting after final character of `prefix` to
a terminating character (one that has a True-equivalent `data` value).

### `match(string, [limit])`

Gets `limit` or all possible word matches for prefix `string`. For example, if
'apple', 'apiary', and 'aptitude' were added to the trie, match('ap') would
return all three items, and match('app'), would return 'apple'.

### `make([prefix], [weight], [limit])`

The fun part. Makes a random word starting at end of `prefix` weighting the
character choices by the number of times they appeared after the previous
letter when "training" the trie. Can limit size of generated word with the
`limit` parameter.

Internally, each character in the trie keeps track of the number of times it
has been added to it's parent. For example, adding 'apple' and 'apiary' would
have a 2 count for the first and second characters, 'a' and 'p', and a 1 count
for the third character, 'p' in 'apple' and 'i' in 'apiary'. If I then added
'acorn', and the randomizer picked an 'a' as the first letter (there's no other
option), picking a 'p' as the second character would be twice as likely as
a 'c', since second-character 'p' has a 2-count and second-character 'c' has
a 1-count.

### `depth()`

Returns the depth of the tree, i.e. the longest sequence of characters.

## License

MIT Public License. See `license.txt` for details.
