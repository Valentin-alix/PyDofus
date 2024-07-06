import io
import json
import os
import struct
from pathlib import Path

from const import DOFUS_PATH
from pydofus.d2p import D2PReader, InvalidD2PFile
from pydofus.swl import SWLReader

# python d2p_pack.py (all files in input folder)
# folder output: ./output/{all files}.d2p


PATH_MAP = os.path.join(DOFUS_PATH, "content", "maps\\")
PATH_MAP_OUTPUT = os.path.join(Path(__file__).parent, "output", "d2p_maps\\")

PATH_GFX = os.path.join(DOFUS_PATH, "content", "gfx\\")
PATH_GFX_OUTPUT = os.path.join(Path(__file__).parent, "output", "gfx\\")

path_input = PATH_MAP
path_output = PATH_MAP_OUTPUT


def main():
    for root, subdirs, files in os.walk(path_input):
        for file in files:
            folder = os.path.relpath(root, path_input)
            if file.endswith(".d2p"):
                file_name = os.path.basename(file)
                d2p_file = open(os.path.join(root, file), "rb")

                output_folder = os.path.join(path_output, folder, file_name)
                os.makedirs(output_folder, exist_ok=True)

                # print("D2P Unpacker for " + file_name)

                try:
                    d2p_reader = D2PReader(d2p_file, False)
                    d2p_reader.load()
                    for name, specs in d2p_reader.files.items():
                        # print("extract file " + file_name + "/" + name)

                        file_path_output = os.path.join(
                            output_folder,
                            os.path.dirname(name),
                        )

                        file_output = os.path.join(output_folder, name)

                        os.makedirs(file_path_output, exist_ok=True)

                        if "swl" in name:
                            swl = io.BytesIO(specs["binary"])
                            swl_reader = SWLReader(swl)

                            swf_output = open(file_output.replace("swl", "swf"), "wb")
                            json_output = open(file_output.replace("swl", "json"), "w")

                            swf_output.write(swl_reader.SWF)
                            swl_data = {
                                "version": swl_reader.version,
                                "frame_rate": swl_reader.frame_rate,
                                "classes": swl_reader.classes,
                            }
                            json.dump(swl_data, json_output, indent=4)

                            swf_output.close()
                            json_output.close()
                        else:
                            _file_output = open(file_output, "wb")
                            _file_output.write(specs["binary"])
                            _file_output.close()
                        pass
                except (InvalidD2PFile, struct.error):
                    pass


if __name__ == "__main__":
    main()
