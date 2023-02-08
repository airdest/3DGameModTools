import re
import glob
import os
import shutil

# List of global variables
RELATED_VB_INDEX_LIST = []  # The related file number indices from your input vb or ib hash. looks like:000001,
# 000002,000003, use this to confirm which file should be moved to output folder.


class HeaderInfo:
    file_index = None
    stride = None
    first_vertex = None
    vertex_count = None
    topology = None

    # Header have many semantic element,like POSITION,NORMAL,COLOR etc.
    elementlist = None


class Element:
    semantic_name = None
    semantic_index = None
    format = None
    input_slot = None
    aligned_byte_offset = None
    input_slot_class = None
    instance_data_step_rate = None

    # the order of the element,start from 0.
    element_number = None

    # the byte length of this Element's data.
    byte_width = None



class VertexData:
    vb_file_number = b"vb0"  # vb0
    index = None
    aligned_byte_offset = None
    element_name = None
    data = None

    def __init__(self, line_bytes=b""):
        if line_bytes != b"":
            line_str = str(line_bytes.decode())
            # vb_file_number = line_str.split("[")[0]
            # because we vb_merge into one file, so it always be vb0
            vb_file_number = "vb0"
            self.vb_file_number = vb_file_number.encode()

            tmp_left_index = line_str.find("[")
            tmp_right_index = line_str.find("]")
            index = line_str[tmp_left_index + 1:tmp_right_index]
            self.index = index.encode()

            tmp_left_index = line_str.find("]+")
            aligned_byte_offset = line_str[tmp_left_index + 2:tmp_left_index + 2 + 3]
            self.aligned_byte_offset = aligned_byte_offset.encode()

            tmp_right_index = line_str.find(": ")
            element_name = line_str[tmp_left_index + 2 + 3 + 1:tmp_right_index]
            self.element_name = element_name.encode()

            tmp_left_index = line_str.find(": ")
            tmp_right_index = line_str.find("\r\n")
            data = line_str[tmp_left_index + 2:tmp_right_index]
            self.data = data.encode()

    def __str__(self):
        return self.vb_file_number + b"[" + self.index + b"]+" + self.aligned_byte_offset.decode().zfill(3).encode() + b" " + self.element_name + b": " + self.data + b"\r\n"


class VbFileInfo:
    header_info = HeaderInfo()
    vertex_data_chunk_list = [[VertexData()]]
    output_filename = None


