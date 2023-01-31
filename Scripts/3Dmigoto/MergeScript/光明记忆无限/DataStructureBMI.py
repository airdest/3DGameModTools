import re
import glob
import os
import shutil

# List of global variables

# Offsets calculated
OFFSET_ATTRIBUTE = None
OFFSET_ATTRIBUTE1 = None
OFFSET_ATTRIBUTE2 = None
OFFSET_ATTRIBUTE3 = None
OFFSET_ATTRIBUTE4 = None
OFFSET_ATTRIBUTE5 = None
OFFSET_ATTRIBUTE6 = None
OFFSET_ATTRIBUTE7 = None
OFFSET_ATTRIBUTE13 = None
OFFSET_ATTRIBUTE15 = None


RELATED_VB_INDEX_LIST = []  # The related file number indices from your input vb or ib hash. looks like:000001,
# 000002,000003, use this to confirm which file should be moved to output folder.

WORK_DIR = None  # for setting work dir
GLOBAL_INPUT_IB = None  # the ib file hash you want to merge.


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
        if self.semantic_name == b"ATTRIBUTE":
            if self.semantic_index == b"0":
                self.byte_width = 12
                self.format = b"R32G32B32_FLOAT"

            if self.semantic_index == b"1":
                self.byte_width = 16
                self.format = b"R8G8B8A8_SNORM"

            if self.semantic_index == b"2":
                self.byte_width = 16
                self.format = b"R8G8B8A8_SNORM"

            if self.semantic_index == b"3":
                self.byte_width = 16
                self.format = b"R8G8B8A8_SNORM"

            if self.semantic_index == b"4":
                self.byte_width = 16
                self.format = b"R16G16B16A16_FLOAT"

            if self.semantic_index == b"5":
                self.byte_width = 8
                self.format = b"R16G16_FLOAT"

            if self.semantic_index == b"6":
                self.byte_width = 8
                self.format = b"R16G16_FLOAT"

            if self.semantic_index == b"7":
                self.byte_width = 8
                self.format = b"R16G16_FLOAT"

            if self.semantic_index == b"13":
                self.byte_width = 4
                self.format = b"R32_UINT"

            if self.semantic_index == b"15":
                self.byte_width = 8
                self.format = b"R16G16_FLOAT"


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
            # because we merge into one file, so it always be vb0
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

    if element_name.endswith(b"ATTRIBUTE"):
        aligned_byte_offset = OFFSET_ATTRIBUTE
    if element_name.endswith(b"ATTRIBUTE1"):
        aligned_byte_offset = OFFSET_ATTRIBUTE1
    if element_name.endswith(b"ATTRIBUTE2"):
        aligned_byte_offset = OFFSET_ATTRIBUTE2
    if element_name.endswith(b"ATTRIBUTE3"):
        aligned_byte_offset = OFFSET_ATTRIBUTE3
    if element_name.endswith(b"ATTRIBUTE4"):
        aligned_byte_offset = OFFSET_ATTRIBUTE4
    if element_name.endswith(b"ATTRIBUTE5"):
        aligned_byte_offset = OFFSET_ATTRIBUTE5
    if element_name.endswith(b"ATTRIBUTE6"):
        aligned_byte_offset = OFFSET_ATTRIBUTE6
    if element_name.endswith(b"ATTRIBUTE7"):
        aligned_byte_offset = OFFSET_ATTRIBUTE7
    if element_name.endswith(b"ATTRIBUTE13"):
        aligned_byte_offset = OFFSET_ATTRIBUTE13
    if element_name.endswith(b"ATTRIBUTE15"):
        aligned_byte_offset = OFFSET_ATTRIBUTE15

    return aligned_byte_offset


def set_offset_by_name(element_name, aligned_byte_offset, semantic_index):
    if element_name == b"ATTRIBUTE":
        global OFFSET_ATTRIBUTE
        global OFFSET_ATTRIBUTE1
        global OFFSET_ATTRIBUTE2
        global OFFSET_ATTRIBUTE3
        global OFFSET_ATTRIBUTE4
        global OFFSET_ATTRIBUTE5
        global OFFSET_ATTRIBUTE6
        global OFFSET_ATTRIBUTE7
        global OFFSET_ATTRIBUTE13
        global OFFSET_ATTRIBUTE15

        if semantic_index == b"0":
            OFFSET_ATTRIBUTE = aligned_byte_offset
        if semantic_index == b"1":
            OFFSET_ATTRIBUTE1 = aligned_byte_offset
        if semantic_index == b"2":
            OFFSET_ATTRIBUTE2 = aligned_byte_offset
        if semantic_index == b"3":
            OFFSET_ATTRIBUTE3 = aligned_byte_offset
        if semantic_index == b"4":
           OFFSET_ATTRIBUTE4 = aligned_byte_offset
        if semantic_index == b"5":
            OFFSET_ATTRIBUTE5 = aligned_byte_offset
        if semantic_index == b"6":
            OFFSET_ATTRIBUTE6 = aligned_byte_offset
        if semantic_index == b"7":
            OFFSET_ATTRIBUTE7 = aligned_byte_offset
        if semantic_index == b"13":
            OFFSET_ATTRIBUTE13 = aligned_byte_offset
        if semantic_index == b"15":
            OFFSET_ATTRIBUTE15 = aligned_byte_offset
