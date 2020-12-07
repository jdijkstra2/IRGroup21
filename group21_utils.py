import os
import argparse
from tqdm import tqdm
import json
import numpy as np
from operator import attrgetter
import sys

from pyserini import search
from pyserini import index
from pyserini import analysis

from bglinking.general_utils import utils
from bglinking.database_utils import db_utils
from bglinking.graph.graph import Graph
from bglinking.graph.graph_comparators.GMCSComparator import GMCSComparator

def my_test():
   print("This is from group 21")

