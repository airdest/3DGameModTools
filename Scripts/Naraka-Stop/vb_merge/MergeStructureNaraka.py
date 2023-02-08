import re
import glob
import os
import shutil

# List of global variables

# Offsets calculated
OFFSET_POSITION = None
OFFSET_NORMAL = None
OFFSET_TANGENT = None
OFFSET_COLOR = None
OFFSET_TEXCOORD = None
OFFSET_TEXCOORD1 = None
OFFSET_TEXCOORD2 = None
OFFSET_TEXCOORD3 = None
OFFSET_TEXCOORD4 = None
OFFSET_TEXCOORD5 = None
OFFSET_TEXCOORD6 = None
OFFSET_TEXCOORD7 = None
OFFSET_BLENDWEIGHTS = None
OFFSET_BLENDINDICES = None

RELATED_VB_INDEX_LIST = []  # The related file number indices from your input vb or ib hash. looks like:000001,
# 000002,000003, use this to confirm which file should be moved to output folder.

WORK_DIR = None  # for setting work dir
GLOBAL_ELEMENT_NUMBER = None  # The number of element a dump vb txt file contains, start from 0, format: b"number".
GLOBAL_ROOT_VS = None  # the vertex shader which contains character's animation information.
GLOBAL_INPUT_IB = None  # the ib file hash you want to vb_merge.
GLOBAL_INPUT_VB = None  # the vb file hash you want to vb_merge,which contains the real TEXCOORD info.


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

    def revise(self):
        if self.semantic_name == b"POSITION":
            self.byte_width = 12
            self.format = b"R32G32B32_FLOAT"
        if self.semantic_name == b"NORMAL":
            self.byte_width = 12
            self.format = b"R32G32B32_FLOAT"
        if self.semantic_name == b"TANGENT":
            self.byte_width = 16
            self.format = b"R32G32B32A32_FLOAT"
        if self.semantic_name == b"COLOR":
            self.byte_width = 4
            self.format = b"R8G8B8A8_UNORM"
        if self.semantic_name == b"TEXCOORD":
            if self.semantic_index == b"0":
                self.byte_width = 8
                self.format = b"R32G32_FLOAT"
            else:
                self.byte_width = 16
                # TODO 测试它的原始R8G8B8A8_UNORM 是否能正确导入
                # element.format = b"R32G32B32A32_FLOAT"
                self.format = b"R8G8B8A8_UNORM"
        if self.semantic_name == b"BLENDWEIGHTS":
            self.byte_width = 16
            self.format = b"R32G32B32A32_FLOAT"
        if self.semantic_name == b"BLENDINDICES":
            self.byte_width = 16
            self.format = b"R32G32B32A32_SINT"


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


def get_offset_by_name(element_name):
    aligned_byte_offset = None

    if element_name == b"POSITION":
        aligned_byte_offset = OFFSET_POSITION

    if element_name == b"NORMAL":
        aligned_byte_offset = OFFSET_NORMAL

    if element_name == b"TANGENT":
        aligned_byte_offset = OFFSET_TANGENT

    if element_name == b"COLOR":
        aligned_byte_offset = OFFSET_COLOR

    if element_name.endswith(b"TEXCOORD"):
        aligned_byte_offset = OFFSET_TEXCOORD

    if element_name.endswith(b"TEXCOORD1"):
        aligned_byte_offset = OFFSET_TEXCOORD1

    if element_name.endswith(b"TEXCOORD2"):
        aligned_byte_offset = OFFSET_TEXCOORD2
    if element_name.endswith(b"TEXCOORD3"):
        aligned_byte_offset = OFFSET_TEXCOORD3
    if element_name.endswith(b"TEXCOORD4"):
       aligned_byte_offset = OFFSET_TEXCOORD4
    if element_name.endswith(b"TEXCOORD5"):
        aligned_byte_offset = OFFSET_TEXCOORD5
    if element_name.endswith(b"TEXCOORD6"):
        aligned_byte_offset = OFFSET_TEXCOORD6
    if element_name.endswith(b"TEXCOORD7"):
        aligned_byte_offset = OFFSET_TEXCOORD7

    if element_name == b"BLENDWEIGHTS":
        aligned_byte_offset = OFFSET_BLENDWEIGHTS

    if element_name == b"BLENDINDICES":
        aligned_byte_offset = OFFSET_BLENDINDICES

    return aligned_byte_offset


def set_offset_by_name(element_name, aligned_byte_offset, semantic_index):
    if element_name == b"POSITION":
        global OFFSET_POSITION
        OFFSET_POSITION = aligned_byte_offset

    if element_name == b"NORMAL":
        global OFFSET_NORMAL
        OFFSET_NORMAL = aligned_byte_offset

    if element_name == b"TANGENT":
        global OFFSET_TANGENT
        OFFSET_TANGENT = aligned_byte_offset

    if element_name == b"COLOR":
        global OFFSET_COLOR
        OFFSET_COLOR = aligned_byte_offset

    if element_name.endswith(b"TEXCOORD"):
        global OFFSET_TEXCOORD
        global OFFSET_TEXCOORD1
        global OFFSET_TEXCOORD2
        global OFFSET_TEXCOORD3
        global OFFSET_TEXCOORD4
        global OFFSET_TEXCOORD5
        global OFFSET_TEXCOORD6
        global OFFSET_TEXCOORD7
        if semantic_index == b"0":
            OFFSET_TEXCOORD = aligned_byte_offset
        if semantic_index == b"1":
            OFFSET_TEXCOORD1 = aligned_byte_offset
        if semantic_index == b"2":
            OFFSET_TEXCOORD2 = aligned_byte_offset
        if semantic_index == b"3":
            OFFSET_TEXCOORD3 = aligned_byte_offset
        if semantic_index == b"4":
           OFFSET_TEXCOORD4 = aligned_byte_offset
        if semantic_index == b"5":
            OFFSET_TEXCOORD5 = aligned_byte_offset
        if semantic_index == b"6":
            OFFSET_TEXCOORD6 = aligned_byte_offset
        if semantic_index == b"7":
            OFFSET_TEXCOORD7 = aligned_byte_offset

    if element_name == b"BLENDWEIGHTS":
        global OFFSET_BLENDWEIGHTS
        OFFSET_BLENDWEIGHTS = aligned_byte_offset

    if element_name == b"BLENDINDICES":
        global OFFSET_BLENDINDICES
        OFFSET_BLENDINDICES = aligned_byte_offset
