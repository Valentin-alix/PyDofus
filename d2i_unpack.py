import json
import os
from pathlib import Path

from const import DOFUS_PATH
from pydofus.d2i import D2I

# python d2i_unpack.py file.d2i
# file output: file.json

path_input = os.path.join(DOFUS_PATH, "data", "i18n", "i18n_fr.d2i")
path_output = os.path.join(Path(__file__).parent, "output", "d2i.json")


d2i_input = open(path_input, "rb")
json_output = open(path_output, "w", encoding="utf-8")

d2i = D2I(d2i_input)
data = d2i.read()

json.dump(data, json_output, indent=2, ensure_ascii=False)

d2i_input.close()
json_output.close()
