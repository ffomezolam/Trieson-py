# taken from The Hitchhiker's Guide To Python

import os
import sys

# add Trieson package path to search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import used modules
from Trieson import Trieson
from Trieson.Trieson import format_return_item_spec, get_node_attr
from Trieson import Vein
from Trieson import Triesonode
from Trieson import comboster
from Trieson import vessels
from Trieson import traversers
import Trie
