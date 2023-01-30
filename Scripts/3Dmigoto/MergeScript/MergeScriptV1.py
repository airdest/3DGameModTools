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
GLOBAL_INPUT_VB = None  # the ib or vb hash you want to merge.


class HeaderInfo:
    """
    A universal data structure for every game, just for easier to read and understand.
    """
    file_index = None
    stride = None
    first_vertex = None
    vertex_count = None
    topology = None

    # Header have many semantic element,like POSITION,NORMAL,COLOR etc.
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
    header_info = HeaderInfo()
    vertex_data_list = [VertexData()]
    output_filename = None


def set_element_format_and_bytewidth(elementlist):
    """
    这里参考了原神脚本merge后的结果。
    # TODO 搞懂这些format的含义，还有每种element名称对应的format格式
    :param elementlist:
    :return:
    """
    new_element_list = []
    for element in elementlist:
        if element.semantic_name == b"POSITION":
            element.byte_width = 12
            element.format = b"R32G32B32_FLOAT"
        if element.semantic_name == b"NORMAL":
            element.byte_width = 12
            element.format = b"R32G32B32_FLOAT"
        if element.semantic_name == b"TANGENT":
            element.byte_width = 16
            element.format = b"R32G32B32A32_FLOAT"
        if element.semantic_name == b"COLOR":
            element.byte_width = 16
            element.format = b"R8G8B8A8_UNORM"
        if element.semantic_name == b"TEXCOORD":
            if element.semantic_index == b"0":
                element.byte_width = 8
                element.format = b"R32G32_FLOAT"
            else:
                element.byte_width = 16
                element.format = b"R32G32B32A32_FLOAT"
        if element.semantic_name == b"BLENDWEIGHTS":
            element.byte_width = 16
            element.format = b"R32G32B32A32_FLOAT"
        if element.semantic_name == b"BLENDINDICES":
            element.byte_width = 16
            element.format = b"R32G32B32A32_SINT"

        new_element_list.append(element)
    return new_element_list


def get_header_info(vb_file_name):
    """
    :param vb_file_name: the filename you want to extract header info.
    :return: return a HeaderInfo which has the vb file header info.
    """
    vb_file = open(vb_file_name, 'rb')

    header_info = HeaderInfo()

    # 用于控制标题部分读取
    header_process_over = False
    # 用于控制Elements部分读取
    elements_all_process_over = False
    elements_single_process_over = False
    # 用来装element列表
    element_list = []
    # 用来临时装一个Element
    element_tmp = Element()

    while vb_file.tell() < os.path.getsize(vb_file.name):
        # 读取一行
        line = vb_file.readline()
        # 处理header
        if not header_process_over:
            # TODO 这里不够兼容，因为不能处理first vertex在各个vb文件中不同的情况，具体后续再测试吧
            # 设置first_vertex,因为所有文件的first_vertex都是相同的，都是0，所以这里会取最后一次的first_vertex
            if line.startswith(b"first vertex: "):
                first_vertex = line[line.find(b"first vertex: ") + b"first vertex: ".__len__():line.find(b"\r\n")]
                header_info.first_vertex = first_vertex
            # 设置vertex_count,因为所有文件的vertex_count都是相同的，所以这里会取最后一次的vertex_count
            if line.startswith(b"vertex count: "):
                vertex_count = line[line.find(b"vertex count: ") + b"vertex count: ".__len__():line.find(b"\r\n")]
                header_info.vertex_count = vertex_count
            # 设置topology,因为所有文件的topology都是相同的，所以这里会取最后一次的topology
            if line.startswith(b"topology: "):
                topology = line[line.find(b"topology: ") + b"topology: ".__len__():line.find(b"\r\n")]
                header_info.topology = topology

            if header_info.topology is not None:
                header_process_over = True

        # 处理Element部分,同理，所有vb0,1,2这样文件的element部分都是完全相同的，所以默认赋值的最后一个也是正确的
        if not elements_all_process_over:

            if line.startswith(b"element["):
                # 检测到element[  说明开始了新的element处理
                elements_single_process_over = False
                # 初始化ElementTmp
                element_tmp = Element()
                element_number = line[line.find(b"element[") + b"element[".__len__():line.find(b"]:\r\n")]
                element_tmp.element_number = element_number
            if line.startswith(b"  SemanticName: "):
                semantic_name = line[line.find(b"  SemanticName: ") + b"  SemanticName: ".__len__():line.find(b"\r\n")]
                element_tmp.semantic_name = semantic_name
            if line.startswith(b"  SemanticIndex: "):
                semantic_index = line[
                                 line.find(b"  SemanticIndex: ") + b"  SemanticIndex: ".__len__():line.find(b"\r\n")]
                element_tmp.semantic_index = semantic_index
            if line.startswith(b"  Format: "):
                format = line[line.find(b"  Format: ") + b"  Format: ".__len__():line.find(b"\r\n")]
                element_tmp.format = format
            if line.startswith(b"  InputSlot: "):
                input_slot = line[line.find(b"  InputSlot: ") + b"  InputSlot: ".__len__():line.find(b"\r\n")]
                element_tmp.input_slot = input_slot
                # 因为最终都在一个文件里面，所以所有的input_slot都设置为0
                element_tmp.input_slot = b"0"
            if line.startswith(b"  AlignedByteOffset: "):
                aligned_byte_offset = line[line.find(
                    b"  AlignedByteOffset: ") + b"  AlignedByteOffset: ".__len__():line.find(b"\r\n")]
                element_tmp.aligned_byte_offset = aligned_byte_offset
            if line.startswith(b"  InputSlotClass: "):
                input_slot_class = line[line.find(b"  InputSlotClass: ") + b"  InputSlotClass: ".__len__():line.find(
                    b"\r\n")]
                element_tmp.input_slot_class = input_slot_class
            if line.startswith(b"  InstanceDataStepRate: "):
                instance_data_step_rate = line[line.find(
                    b"  InstanceDataStepRate: ") + b"  InstanceDataStepRate: ".__len__():line.find(b"\r\n")]
                element_tmp.instance_data_step_rate = instance_data_step_rate

                # element_tmp加入list
                element_list.append(element_tmp)
                # 单个处理完毕
                elements_single_process_over = True

            if element_tmp.element_number == GLOBAL_ELEMENT_NUMBER and elements_single_process_over:
                header_info.elementlist = element_list
                elements_all_process_over = True
                break

    # 读取完header部分后，关闭文件
    vb_file.close()

    # 设置bytewidth和format
    header_info.elementlist = set_element_format_and_bytewidth(header_info.elementlist)

    return header_info


def get_vertex_data_list(vb_filenames, vertex_count):
    # TODO 这里要使用pointlist技术中的姿态
    # vertex data 列表 ,这里要注意，如果使用[VertexData()] * int(str(vertex_count.decode())) 则创建出的列表所有元素都是同一个元素
    vertex_data_list = [VertexData() for i in range(int(str(vertex_count.decode())))]

    for filename in vb_filenames:
        # 首先获取当前是vb几
        vb_number = filename[filename.find("-vb"):filename.find("=")][1:].encode()

        # 打开vb文件
        vb_file = open(filename, 'rb')

        # 临时装载vertexdata
        vertex_data_tmp = VertexData()

        # 用于临时记录上一行
        line_before_tmp = b"\r\n"

        vb_file_size = os.path.getsize(vb_file.name)

        while vb_file.tell() <= vb_file_size:
            # 读取一行
            line = vb_file.readline()

            # vertexdata处理
            if line.startswith(vb_number):
                # 赋值上一行为有vb_number的行
                line_before_tmp = line

                # 获取属于第几个vertex group
                vertex_group_number = line[line.find(vb_number):line.find(b" ")]
                vertex_group_number = vertex_group_number[vertex_group_number.find(b"[") + 1:vertex_group_number.find(b"]")]
                index = int(str(vertex_group_number.decode()))
                # print("index: " + str(index) + " / all: " + str(vertex_count))

                if line.__contains__(b"POSITION:"):
                    vertex_data_tmp.POSITION = line
                if line.__contains__(b"NORMAL:"):
                    vertex_data_tmp.NORMAL = line
                if line.__contains__(b"TANGENT:"):
                    vertex_data_tmp.TANGENT = line
                if line.__contains__(b"COLOR:"):
                    vertex_data_tmp.COLOR = line
                if line.__contains__(b"TEXCOORD:"):
                    vertex_data_tmp.TEXCOORD = line
                if line.__contains__(b"TEXCOORD1:"):
                    vertex_data_tmp.TEXCOORD1 = line
                if line.__contains__(b"TEXCOORD2:"):
                    vertex_data_tmp.TEXCOORD2 = line
                if line.__contains__(b"TEXCOORD3:"):
                    vertex_data_tmp.TEXCOORD3 = line
                if line.__contains__(b"TEXCOORD4:"):
                    vertex_data_tmp.TEXCOORD4 = line
                if line.__contains__(b"TEXCOORD5:"):
                    vertex_data_tmp.TEXCOORD5 = line
                if line.__contains__(b"TEXCOORD6:"):
                    vertex_data_tmp.TEXCOORD6 = line
                if line.__contains__(b"TEXCOORD7:"):
                    vertex_data_tmp.TEXCOORD7 = line
                if line.__contains__(b"BLENDWEIGHTS:"):
                    vertex_data_tmp.BLENDWEIGHTS = line
                if line.__contains__(b"BLENDINDICES:"):
                    vertex_data_tmp.BLENDINDICES = line

            # 遇到换行符处理
            if (line.startswith(b"\r\n") or vb_file.tell() == vb_file_size) and line_before_tmp.startswith(vb_number):
                # 赋值上一行为\r\n的行
                line_before_tmp = b"\r\n"

                # 取出来，进行vb0替换
                vertex_data = vertex_data_list[index]

                if vertex_data_tmp.POSITION is not None:
                    vertex_data.POSITION = getVb0Bytes(vertex_data_tmp.POSITION, vb_number)
                if vertex_data_tmp.NORMAL is not None:
                    vertex_data.NORMAL = getVb0Bytes(vertex_data_tmp.NORMAL, vb_number)
                if vertex_data_tmp.TANGENT is not None:
                    vertex_data.TANGENT = getVb0Bytes(vertex_data_tmp.TANGENT, vb_number)
                if vertex_data_tmp.COLOR is not None:
                    vertex_data.COLOR = getVb0Bytes(vertex_data_tmp.COLOR, vb_number)
                if vertex_data_tmp.TEXCOORD is not None:
                    vertex_data.TEXCOORD = getVb0Bytes(vertex_data_tmp.TEXCOORD, vb_number)
                if vertex_data_tmp.TEXCOORD1 is not None:
                    vertex_data.TEXCOORD1 = getVb0Bytes(vertex_data_tmp.TEXCOORD1, vb_number)
                if vertex_data_tmp.TEXCOORD2 is not None:
                    vertex_data.TEXCOORD2 = getVb0Bytes(vertex_data_tmp.TEXCOORD2, vb_number)
                if vertex_data_tmp.TEXCOORD3 is not None:
                    vertex_data.TEXCOORD3 = getVb0Bytes(vertex_data_tmp.TEXCOORD3, vb_number)
                if vertex_data_tmp.TEXCOORD4 is not None:
                    vertex_data.TEXCOORD4 = getVb0Bytes(vertex_data_tmp.TEXCOORD4, vb_number)
                if vertex_data_tmp.TEXCOORD5 is not None:
                    vertex_data.TEXCOORD5 = getVb0Bytes(vertex_data_tmp.TEXCOORD5, vb_number)
                if vertex_data_tmp.TEXCOORD6 is not None:
                    vertex_data.TEXCOORD6 = getVb0Bytes(vertex_data_tmp.TEXCOORD6, vb_number)
                if vertex_data_tmp.TEXCOORD7 is not None:
                    vertex_data.TEXCOORD7 = getVb0Bytes(vertex_data_tmp.TEXCOORD7, vb_number)
                if vertex_data_tmp.BLENDWEIGHTS is not None:
                    vertex_data.BLENDWEIGHTS = getVb0Bytes(vertex_data_tmp.BLENDWEIGHTS, vb_number)
                if vertex_data_tmp.BLENDINDICES is not None:
                    vertex_data.BLENDINDICES = getVb0Bytes(vertex_data_tmp.BLENDINDICES, vb_number)

                # 替换完再塞回去
                vertex_data_list[index] = vertex_data
                # 重置临时VertexData
                vertex_data_tmp = VertexData()

            if vb_file.tell() == vb_file_size:
                break
        vb_file.close()
    return vertex_data_list


def getVb0Bytes(bytes, vb_number):
    return str(bytes.decode()).replace(vb_number.decode(), "vb0").encode()


def output_model_txt(header_info, vertex_data_list, output_filename):
    print("开始写出文件: " + output_filename)
    # 首先解决VertexData部分缺失，但是Element部分存在，导致合成的结果无法正常导入Blender的问题。
    # 抽取第一个vertex_data，判断它哪些属性存在
    vertex_data_test = vertex_data_list[0]
    vertex_data_has_element_list = []
    # 默认都没有，检测到一个算一个
    if vertex_data_test.POSITION is not None:
        vertex_data_has_element_list.append(b"POSITION")
    if vertex_data_test.NORMAL is not None:
        vertex_data_has_element_list.append(b"NORMAL")
    if vertex_data_test.TANGENT is not None:
        vertex_data_has_element_list.append(b"TANGENT")
    if vertex_data_test.COLOR is not None:
        vertex_data_has_element_list.append(b"COLOR")
    if vertex_data_test.TEXCOORD is not None:
        vertex_data_has_element_list.append(b"TEXCOORD")
    if vertex_data_test.TEXCOORD1 is not None:
        vertex_data_has_element_list.append(b"TEXCOORD1")
    if vertex_data_test.TEXCOORD2 is not None:
        vertex_data_has_element_list.append(b"TEXCOORD2")
    if vertex_data_test.TEXCOORD3 is not None:
        vertex_data_has_element_list.append(b"TEXCOORD3")
    if vertex_data_test.TEXCOORD4 is not None:
        vertex_data_has_element_list.append(b"TEXCOORD4")
    if vertex_data_test.TEXCOORD5 is not None:
        vertex_data_has_element_list.append(b"TEXCOORD5")
    if vertex_data_test.TEXCOORD6 is not None:
        vertex_data_has_element_list.append(b"TEXCOORD6")
    if vertex_data_test.TEXCOORD7 is not None:
        vertex_data_has_element_list.append(b"TEXCOORD7")
    if vertex_data_test.BLENDWEIGHTS is not None:
        vertex_data_has_element_list.append(b"BLENDWEIGHTS")
    if vertex_data_test.BLENDINDICES is not None:
        vertex_data_has_element_list.append(b"BLENDINDICES")

    header_info_has_element_list = []
    for element in header_info.elementlist:
        name = element.semantic_name
        if element.semantic_name == b"TEXCOORD" and element.semantic_index != b"0":
                name = element.semantic_name + element.semantic_index
        header_info_has_element_list.append(name)

    # 输出到最终文件
    output_file = open(output_filename, "wb+")

    # (1) 首先输出header
    output_file.write(b"stride: " + header_info.stride + b"\r\n")
    output_file.write(b"first vertex: " + header_info.first_vertex + b"\r\n")
    output_file.write(b"vertex count: " + header_info.vertex_count + b"\r\n")
    output_file.write(b"topology: " + header_info.topology + b"\r\n")

    # (2) 遍历Elementlist,根据是否存在element来写入对应内容
    element_list = header_info.elementlist
    for element in element_list:
        element_name = element.semantic_name
        semantic_index = element.semantic_index
        if element_name == b"TEXCOORD":
            if semantic_index != b'0':
                element_name = element_name + semantic_index

        if vertex_data_has_element_list.__contains__(element_name):
            # print("检测到："+str(element_name))
            # 输出对应的Element
            output_file.write(b"element[" + element.element_number + b"]:" + b"\r\n")
            output_file.write(b"  SemanticName: " + element.semantic_name + b"\r\n")
            output_file.write(b"  SemanticIndex: " + element.semantic_index + b"\r\n")
            output_file.write(b"  Format: " + element.format + b"\r\n")
            output_file.write(b"  InputSlot: " + element.input_slot + b"\r\n")
            output_file.write(b"  AlignedByteOffset: " + element.aligned_byte_offset + b"\r\n")
            output_file.write(b"  InputSlotClass: " + element.input_slot_class + b"\r\n")
            output_file.write(b"  InstanceDataStepRate: " + element.instance_data_step_rate + b"\r\n")
    # (3) 拼接写入Vertex-data部分
    output_file.write(b"\r\n")
    output_file.write(b"vertex-data:\r\n")
    output_file.write(b"\r\n")

    # 遍历vertex_data_list，如果vertexdata和element都存在此元素，才能进行输出
    # TODO，问题是element_has_list是从vertexdata读取的，那百分百是存在的，这里需要修改
    for index in range(len(vertex_data_list)):
        vertex_data = vertex_data_list[index]
        # print(index)
        if vertex_data.POSITION is not None and header_info_has_element_list.__contains__(b"POSITION"):
            output_file.write(vertex_data.POSITION)
        if vertex_data.NORMAL is not None and header_info_has_element_list.__contains__(b"NORMAL"):
            output_file.write(vertex_data.NORMAL)
        if vertex_data.TANGENT is not None and header_info_has_element_list.__contains__(b"TANGENT"):
            output_file.write(vertex_data.TANGENT)
        if vertex_data.COLOR is not None and header_info_has_element_list.__contains__(b"COLOR"):
            output_file.write(vertex_data.COLOR)
        if vertex_data.TEXCOORD is not None and header_info_has_element_list.__contains__(b"TEXCOORD"):
            output_file.write(vertex_data.TEXCOORD)
        if vertex_data.TEXCOORD1 is not None and header_info_has_element_list.__contains__(b"TEXCOORD1"):
           output_file.write(vertex_data.TEXCOORD1)
        if vertex_data.TEXCOORD2 is not None and header_info_has_element_list.__contains__(b"TEXCOORD2"):
            output_file.write(vertex_data.TEXCOORD2)
        if vertex_data.TEXCOORD3 is not None and header_info_has_element_list.__contains__(b"TEXCOORD3"):
            output_file.write(vertex_data.TEXCOORD3)
        if vertex_data.TEXCOORD4 is not None and header_info_has_element_list.__contains__(b"TEXCOORD4"):
           output_file.write(vertex_data.TEXCOORD4)
        if vertex_data.TEXCOORD5 is not None and header_info_has_element_list.__contains__(b"TEXCOORD5"):
            output_file.write(vertex_data.TEXCOORD5)
        if vertex_data.TEXCOORD6 is not None and header_info_has_element_list.__contains__(b"TEXCOORD6"):
            output_file.write(vertex_data.TEXCOORD6)
        if vertex_data.TEXCOORD7 is not None and header_info_has_element_list.__contains__(b"TEXCOORD7"):
            output_file.write(vertex_data.TEXCOORD7)
        if vertex_data.BLENDWEIGHTS is not None and header_info_has_element_list.__contains__(b"BLENDWEIGHTS"):
            output_file.write(vertex_data.BLENDWEIGHTS)
        if vertex_data.BLENDINDICES is not None and header_info_has_element_list.__contains__(b"BLENDINDICES"):
            output_file.write(vertex_data.BLENDINDICES)

        # 如果是最后一行，就不追加换行符
        if index != len(vertex_data_list) - 1:
            output_file.write(b"\r\n")

    output_file.close()


def is_pointlist_file(filename):
    ib_file = open(filename, "rb")
    ib_file_size = os.path.getsize(filename)
    pointlist_flag = False
    count = 0
    while ib_file.tell() <= ib_file_size:
        line = ib_file.readline()
        # 因为topology固定在第四行出现，所以如果读取到了第五行，说明没发现pointlist，就可以停止了
        count = count + 1
        if count > 5:
            break
        if line.startswith(b"topology: "):
            topology = line[line.find(b"topology: ") + b"topology: ".__len__():line.find(b"\r\n")]
            if topology == b"pointlist":
                pointlist_flag = True
                break
    # 最后肯定要关闭文件
    ib_file.close()
    return pointlist_flag


def move_related_files():
    # 设置当前目录
    os.chdir(WORK_DIR)

    # 创建output目录，用于存放输出后的脚本
    if not os.path.exists('output'):
        os.mkdir('output')

    print("----------------------------------------------------------------")
    print("开始移动.dds贴图文件")
    # 移动dds贴图文件
    filenames = glob.glob('*.dds')
    for filename in filenames:
        if os.path.exists(filename):
            for index in RELATED_VB_INDEX_LIST:
                if filename.__contains__(index):
                    print("正在处理： " + filename + " ....")
                    shutil.copy2(filename, 'output/' + filename)

    print("----------------------------------------------------------------")
    print("开始移动vs-cb骨骼txt文件")
    # 移动vs-cb骨骼文件
    filenames = glob.glob('*vs-cb*')
    for filename in filenames:
        if os.path.exists(filename):
            # 必须包含指定vb的索引才能移动
            for index in RELATED_VB_INDEX_LIST:
                if filename.__contains__(index):
                    print("正在移动： " + filename + " ....")
                    shutil.copy2(filename, 'output/' + filename)

    print("----------------------------------------------------------------")
    print("开始移动ps-cb骨骼txt文件")
    # 移动ps-cb骨骼文件
    filenames = glob.glob('*ps-cb*')
    for filename in filenames:
        if os.path.exists(filename):
            # 必须包含指定vb的索引才能移动
            for index in RELATED_VB_INDEX_LIST:
                if filename.__contains__(index):
                    print("正在移动： " + filename + " ....")
                    shutil.copy2(filename, 'output/' + filename)


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

    # if element_name.endswith(b"TEXCOORD2"):
    #     aligned_byte_offset = OFFSET_TEXCOORD2
    # if element_name.endswith(b"TEXCOORD3"):
    #     aligned_byte_offset = OFFSET_TEXCOORD3
    # if element_name.endswith(b"TEXCOORD4"):
    #    aligned_byte_offset = OFFSET_TEXCOORD4
    # if element_name.endswith(b"TEXCOORD5"):
    #     aligned_byte_offset = OFFSET_TEXCOORD5
    # if element_name.endswith(b"TEXCOORD6"):
    #     aligned_byte_offset = OFFSET_TEXCOORD6
    # if element_name.endswith(b"TEXCOORD7"):
    #     aligned_byte_offset = OFFSET_TEXCOORD7

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
        # if semantic_index == b"2":
        #     OFFSET_TEXCOORD2 = aligned_byte_offset
        # if semantic_index == b"3":
        #     OFFSET_TEXCOORD3 = aligned_byte_offset
        # if semantic_index == b"4":
        #    OFFSET_TEXCOORD4 = aligned_byte_offset
        # if semantic_index == b"5":
        #     OFFSET_TEXCOORD5 = aligned_byte_offset
        # if semantic_index == b"6":
        #     OFFSET_TEXCOORD6 = aligned_byte_offset
        # if semantic_index == b"7":
        #     OFFSET_TEXCOORD7 = aligned_byte_offset

    if element_name == b"BLENDWEIGHTS":
        global OFFSET_BLENDWEIGHTS
        OFFSET_BLENDWEIGHTS = aligned_byte_offset

    if element_name == b"BLENDINDICES":
        global OFFSET_BLENDINDICES
        OFFSET_BLENDINDICES = aligned_byte_offset


def get_rectified_vertex(vertex):
    # TODO 这里的每一行vertex_data，都应该是一个单独的数据结构，最后再拼接出来，拼接的过程在类中实现而不是代码中
    vertex_str = vertex.decode()
    original_index = vertex_str[vertex_str.find("]+"):vertex_str.find("]+") + 2 + 3]
    original_name = vertex_str[vertex_str.find("]+")+6: vertex_str.find(": ")]
    new_index = "]+" + get_offset_by_name(original_name.encode()).decode().zfill(3)
    vertex_str = vertex_str.replace(original_index, new_index)
    return vertex_str.encode()


def revise_trianglelist_by_pointlist(triangle_vb_list, pointlist_vb_list):
    # 根据pointlist，修正trianglelist中的vertex_data信息
    rectified_triangle_list = []
    for triangle_vb in triangle_vb_list:
        triangle_header_info = triangle_vb.header_info
        vertex_count = triangle_header_info.vertex_count

        # 寻找对应vertex_count长度的pointlist
        right_pointlist_vb = None
        count = 0
        for pointlist_vb in pointlist_vb_list:
            if vertex_count == pointlist_vb.header_info.vertex_count:
                right_pointlist_vb = pointlist_vb
                count = count + 1

        if right_pointlist_vb is None:
            print("未找到对应的pointlist")
            print("vertexcount"+str(vertex_count))
        elif count == 1:
            print("找到了对应的pointlist，进行替换")
            # TODO 这里目前还不确定是全部替换比较好，还是只替换部分比较好,先运行试试，有可能存在element数量不一致情况
            triangle_vb.vertex_data_list = right_pointlist_vb.vertex_data_list

            print(right_pointlist_vb.output_filename)
        else:
            # 这里触发找到了多个对应pointlist的原因是trianglelist那里我们没有对输入的vb做限制
            print("找到了多个对应的pointlist？？？")
            exit(1)
        # 加入到修正后的列表中
        rectified_triangle_list.append(triangle_vb)
    return rectified_triangle_list


def revise_model_by_output_control(revised_triangle_list):
    # 第一步: 删除不想输出的element，反过来说就是只保留你想要的element
    new_list = []
    for vb_file_info in revised_triangle_list:
        element_list = vb_file_info.header_info.elementlist
        new_element_lsit = []
        for element in element_list:
            if element.semantic_name == b"POSITION":
                new_element_lsit.append(element)
            if element.semantic_name == b"NORMAL":
                new_element_lsit.append(element)
            if element.semantic_name == b"TANGENT":
                new_element_lsit.append(element)
            if element.semantic_name == b"BLENDWEIGHTS":
                new_element_lsit.append(element)
            if element.semantic_name == b"BLENDINDICES":
                new_element_lsit.append(element)
            if element.semantic_name == b"COLOR":
                new_element_lsit.append(element)
            if element.semantic_name == b"TEXCOORD":
                if element.semantic_index == b"0":
                    new_element_lsit.append(element)
                if element.semantic_index == b"1":
                    new_element_lsit.append(element)

        vb_file_info.header_info.elementlist = new_element_lsit
        new_list.append(vb_file_info)

    revised_triangle_list = new_list
    # 第二步: 重新计算各元素的aligned_byte_offset和总stride 还有elementnumber
    # TODO，这个重新计算是不是应该放到类里面的方法？

    new_list = []
    for vb_file_info in revised_triangle_list:
        new_element_lsit ,stride = get_element_byte_aligned_offset_and_stride(vb_file_info.header_info.elementlist)
        vb_file_info.header_info.elementlist = new_element_lsit
        vb_file_info.header_info.stride = stride
        new_list.append(vb_file_info)
    revised_triangle_list = new_list


    # 第三步：vertex_data部分的element对应的索引+xxx重新赋予正确的值
    newlist = []
    for vb_file_info in revised_triangle_list:
        new_vertex_data_list = []
        vertex_data_list = vb_file_info.vertex_data_list
        for vertex_data in vertex_data_list:
            vertex_data.POSITION = get_rectified_vertex(vertex_data.POSITION)
            vertex_data.NORMAL = get_rectified_vertex(vertex_data.NORMAL)
            vertex_data.TANGENT = get_rectified_vertex(vertex_data.TANGENT)
            vertex_data.COLOR = get_rectified_vertex(vertex_data.COLOR)

            vertex_data.TEXCOORD = get_rectified_vertex(vertex_data.TEXCOORD)
            vertex_data.TEXCOORD1 = get_rectified_vertex(vertex_data.TEXCOORD1)
            # vertex_data.TEXCOORD2 = get_rectified_vertex(vertex_data.TEXCOORD2)
            # vertex_data.TEXCOORD3 = get_rectified_vertex(vertex_data.TEXCOORD3)
            # vertex_data.TEXCOORD4 = get_rectified_vertex(vertex_data.TEXCOORD4)
            # vertex_data.TEXCOORD5 = get_rectified_vertex(vertex_data.TEXCOORD5)
            # vertex_data.TEXCOORD6 = get_rectified_vertex(vertex_data.TEXCOORD6)
            # vertex_data.TEXCOORD7 = get_rectified_vertex(vertex_data.TEXCOORD7)
            vertex_data.BLENDWEIGHTS = get_rectified_vertex(vertex_data.BLENDWEIGHTS)
            vertex_data.BLENDINDICES = get_rectified_vertex(vertex_data.BLENDINDICES)
            new_vertex_data_list.append(vertex_data)

        vb_file_info.vertex_data_list = new_vertex_data_list
        newlist.append(vb_file_info)
    return newlist



def get_element_byte_aligned_offset_and_stride(element_list):
    new_element_lsit = []
    aligned_byte_offset = 0
    element_number = 0
    for element in element_list:
        # 修正aligned_byte_offset
        element.aligned_byte_offset = str(aligned_byte_offset).encode()
        # 修正element_number
        element.element_number = str(element_number).encode()

        set_offset_by_name(element.semantic_name, str(aligned_byte_offset).encode(), element.semantic_index)

        element_number = element_number + 1
        aligned_byte_offset = aligned_byte_offset + element.byte_width
        new_element_lsit.append(element)
    return new_element_lsit, str(aligned_byte_offset).encode()


def read_pointlist_trianglelist():
    """
    read all dump files, and filter which topology is pointlist and which topology is trianglelist.
    :return:
    """
    # 文件开头的索引数字
    indices = sorted([re.findall('^\d+', x)[0] for x in glob.glob('*-vb0*txt')])

    # 分别装载pointlist技术和triangle技术
    pointlist_topology = []
    trianglelist_topology = []

    for index_number in range(len(indices)):
        # 获取IB文件列表，要么没有，要么只有一个
        ib_files = glob.glob(indices[index_number] + '-ib*txt')

        # 首先获取当前index的所有VB文件的列表
        vb_filenames = sorted(glob.glob(indices[index_number] + '-vb*txt'))

        # 如果不存在ib文件，则直接跳过此索引不进行处理
        if ib_files.__len__() == 0:
            print("This version of script can not process vb information without ib file.")
            continue

        # 获取ib文件名并输出
        ib_filename = str(glob.glob(indices[index_number] + '-ib*txt')[0])
        print("正在处理: " + ib_filename + "  ....")

        # 把这个ib的index对应的所有VB文件的内容融合到一个单独的VB文件中
        # 初始化并读取第一个vb文件的header部分信息，因为所有vb文件的header部分长得都一样，所以默认用vb0来读取
        first_vb_filename = vb_filenames[0]


        header_info = get_header_info(first_vb_filename)

        # 设置当前所属Index
        header_info.file_index = index_number

        # 遍历所有vb文件，读取VertexData部分数据
        vertex_data_list = get_vertex_data_list(vb_filenames, header_info.vertex_count)

        # 判断是pointlsit还是trianglist
        # 如果有IB文件，就把IB(index buffer)文件复制到output目录，直接复制不修改内容
        if os.path.exists(ib_filename):
            # 遇到pointlist自动跳过且不复制到output目录
            # 判断是否为topology
            pointlist_flag = is_pointlist_file(ib_filename)
            # 这里注意，pointlist文件只用来获取真实的骨骼信息，而不移动到output目录
            # 这里如果是pointlist文件，就加入专属列表，如果是tranglelist，就加入tranglist列表
            output_filename = 'output/' + first_vb_filename

            # 这里是pointlist的基础上，文件名中还必须包含根源VB，可能因为正确的blendwidth 和 blendindices是包含在根源VB里的
            if pointlist_flag and ib_filename.__contains__(GLOBAL_ROOT_VS):
                pointlist_vb = VbFileInfo()
                pointlist_vb.header_info = header_info
                pointlist_vb.vertex_data_list = vertex_data_list
                pointlist_vb.output_filename = output_filename
                pointlist_topology.append(pointlist_vb)
            # 这里ib的文件名还要包含我们指定的vb，限制范围，防止出现找到多个pointlist
            elif ib_filename.__contains__(GLOBAL_INPUT_VB):
                trianglelist_vb = VbFileInfo()
                trianglelist_vb.header_info = header_info
                trianglelist_vb.vertex_data_list = vertex_data_list
                trianglelist_vb.output_filename = output_filename
                trianglelist_topology.append(trianglelist_vb)
                # 复制ib文件到output目录
                shutil.copy2(ib_filename, 'output/' + ib_filename)

    return pointlist_topology, trianglelist_topology



if __name__ == "__main__":
    # TODO 这里是用全局变量来传递，后续改成用参数传递
    GLOBAL_ROOT_VS = "e8425f64cfb887cd"  # Naraka root vs
    GLOBAL_INPUT_VB = "794d8782"  # 胡桃黑丝衣服
    GLOBAL_ELEMENT_NUMBER = b"13"  # Naraka element number
    # setting work dir
    WORK_DIR = "C:/Users/Administrator/Desktop/FrameAnalysis-2023-01-29-130542/"

    # 设置当前工作目录
    os.chdir(WORK_DIR)
    print("当前工作目录：" + str(WORK_DIR))

    # 创建output目录，用于存放输出后的脚本
    if not os.path.exists('output'):
        os.mkdir('output')

    pointlist_vb_list, triangle_vb_list = read_pointlist_trianglelist()

    # 根据pointlist，修正trianglelist中的信息
    # TODO 测试不修正会怎样
    revised_triangle_list = revise_trianglelist_by_pointlist(triangle_vb_list, pointlist_vb_list)

    # 根据是否输出对应element元素，来决定每个元素的alignedbyteoffset和总的stride
    revised_triangle_list = revise_model_by_output_control(revised_triangle_list)

    # (3)遍历修正后的列表并拼接vertex_data部分,然后输出
    for rectfied_vb in revised_triangle_list:
        # 将这些vb文件的开头索引加入到列表，方便后续移动dds文件和vs-cb文件
        outputindex = str(rectfied_vb.output_filename)
        outputindex = outputindex[outputindex.find("/000") + 1:outputindex.find("/000") + 7]
        print(outputindex)

        RELATED_VB_INDEX_LIST.append(outputindex)
        # 输出到文件
        output_model_txt(rectfied_vb.header_info, rectfied_vb.vertex_data_list, rectfied_vb.output_filename)


    # 移动相关联的文件
    move_related_files()

    print("全部转换完成！")
    # TODO 目前COLOR和TEXCOOORD1的值完全相通，但是格式不同，而去掉TEXCOORD1后，游戏中是一片白光
    # TODO 如果保留TEXCOORD1，则游戏中是横躺下来的模型，且没有动作
