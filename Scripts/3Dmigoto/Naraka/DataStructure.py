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

Naraka_related_vb_indexlist = []
# The related file number indices from your input vb or ib hash.
# looks like:000001,000002,000003, use this to confirm which file should be moved to output folder.

# 便于设置工作目录
work_dir = "C:/Users/Administrator/Desktop/FrameAnalysis-2023-01-29-130542/"

# Magic Values, for easily read and understand.
# NarakaBladepoint
GLOBAL_ELEMENT_NUMBER = b"13"  # from 0 to 13.
GLOBAL_ROOT_VS = "e8425f64cfb887cd"  # NarakaBladepoint's root hash.
GLOBAL_INPUT_VB = "9f655a36"  # the ib or vb hash you want to merge.


class VbFile:
    """
    A universal data structure for every game, just for easier to read and understand.
    """
    file_index = None
    stride = None
    first_vertex = None
    vertex_count = None
    topology = None

    # A vertexmodel have many semantic element,like POSITION,NORMAL,COLOR etc.
    elementlist = None


class Element:
    """
    The structure is nearly same for every game, but may have different number of Element.
    """
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
    """
    Note: This structure is different between games, depends on your game's Frame analyse dump.
    """
    POSITION = None
    NORMAL = None
    TANGENT = None
    COLOR = None
    TEXCOORD = None
    TEXCOORD1 = None
    TEXCOORD2 = None
    TEXCOORD3 = None
    TEXCOORD4 = None
    TEXCOORD5 = None
    TEXCOORD6 = None
    TEXCOORD7 = None
    BLENDWEIGHTS = None
    BLENDINDICES = None


class VbFileInfo:
    """
    A universal data structure for every game, just for easier to construct this merge script.
    """
    vertex_model = VbFile()
    vertex_data = VertexData()
    output_filename = None
