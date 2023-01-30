class VertexModel:
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
    The structure is nearly same between different games, but may have different number of Element.
    """
    element_number = None
    semantic_name = None
    semantic_index = None
    format = None
    input_slot = None
    aligned_byte_offset = None
    input_slot_class = None
    instance_data_step_rate = None

    # the byte length of this Element's data
    byte_width = None

    # a flag to control whether to output this Element to file.
    output_flag = True


class VertexData:
    """
    Note: This structure is different between games, depends on your game's Frame analyse dump.
    For Naraka's FrameAnalysis dump txt format, vertex-data structure is generally looks like this:

    vb0[1]+000 POSITION: 0.473946899, -0.0874404684, 1.06045353
    vb0[1]+012 NORMAL: -0.856731474, 0.416949213, -0.303586215
    vb0[1]+024 TANGENT: -0.436835259, -0.899537563, -0.00267134164, 1
    vb0[1]+000 COLOR: 0.168627456, 0.662745118, 0.949019611, 0.243137255
    vb0[1]+000 TEXCOORD: 1.98849225, 0.0440213978
    vb0[1]+000 TEXCOORD1: 0.168627456, 0.662745118, 0.949019611, 0.243137255
    vb0[1]+000 TEXCOORD2: 0.168627456, 0.662745118, 0.949019611, 0.243137255
    vb0[1]+000 TEXCOORD3: 0.168627456, 0.662745118, 0.949019611, 0.243137255
    vb0[1]+000 TEXCOORD4: 0.168627456, 0.662745118, 0.949019611, 0.243137255
    vb0[1]+000 TEXCOORD5: 0.168627456, 0.662745118, 0.949019611, 0.243137255
    vb0[1]+000 TEXCOORD6: 0.168627456, 0.662745118, 0.949019611, 0.243137255
    vb0[1]+000 TEXCOORD7: 0.168627456, 0.662745118, 0.949019611, 0.243137255
    vb0[1]+000 BLENDWEIGHTS: 0.911903203, 0.0880968124, 0, 0
    vb0[1]+016 BLENDINDICES: 0, 4, 0, 0
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
    vertex_model = VertexModel()
    vertex_data = VertexData()
    output_filename = None

