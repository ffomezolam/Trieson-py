# taken from The Hitchhiker's Guide To Python

import os
import sys

# add Trieson package path to search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import used modules
from Trieson.Trieson import *
from Trieson.Trietor import *
from Trieson import Trieson
from Trieson import Triesonode
from Trieson import combos
import Trie
