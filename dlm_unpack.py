import json
import os
from pathlib import Path

from pydofus.dlm import DLM

# python dlm_unpack.py file.dlm
# file output: file.json

PATH_INPUT = os.path.join(Path(__file__).parent, "output", "d2p_maps\\")
FOLDER_OUPUT = os.path.join(Path(__file__).parent, "output", "dlm\\")


def main():
    for root, dirs, files in os.walk(PATH_INPUT):
        for file in files:
            path_file = os.path.join(root, file)
            path_output = os.path.join(FOLDER_OUPUT, file.replace("dlm", "json"))

            with open(path_file, "rb") as dlm_input:
                dlm = DLM(dlm_input, "649ae451ca33ec53bbcbcc33becf15f4")
                data = dlm.read()

            with open(path_output, "w") as dlm_output:
                json.dump(data, dlm_output, indent=2)


if __name__ == "__main__":
    main()
