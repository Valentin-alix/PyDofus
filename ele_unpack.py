import json
import os
from pathlib import Path

from const import DOFUS_PATH
from pydofus.ele import ELE

# python ele_unpack.py file.ele
# file output: file.json

PATH_MAP = os.path.join(DOFUS_PATH, "content", "maps", "elements.ele")
PATH_MAP_OUTPUT = os.path.join(Path(__file__).parent, "output", "elements.json")

ele_input = open(PATH_MAP, "rb")
json_output = open(PATH_MAP_OUTPUT, "w")

ele = ELE(ele_input)
data = ele.read()

json.dump(data, json_output, indent=2)

ele_input.close()
json_output.close()
