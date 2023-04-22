# taken from The Hitchhiker's Guide To Python

import os
import sys

# add Trieson package path to search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import used modules
from Trieson import Trieson
from Trieson import Triesonode
from Trieson.Triechery import Triechery
from Trieson.Triecherynode import Triecherynode, is_primitive, as_key
from Trieson import combos
import Trie
