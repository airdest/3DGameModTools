import glob
import os
import re
import shutil
from VertexStructure import *

"""
This merge script is designed for NarakaBladepoint.

For easier to read and understand, I have add a lot of comments in this script,
and I split this script into several part, to be more elegent.
but it's still very hard to understand if you are first time read this kind of vertex merge script.

So before you want to figure out how this script is work, you need a lot of basic knowledge,
which can be found at BasicTutorial folder, especially for Element class, VertexData class and VertexModel class,
if you don't know the basic concept behind it, you almost impossible to understand this script.

Author: airde
Date: 1/28/2023
"""

# Magic Values, for easily read and understand.
# BH3
BH3_ELEMENT_NUMBER = b"7"  # from 0 to 7.
BH3_ROOT_VS = "653c63ba4a73ca8b"  # BH3's root hash.
BH3_INPUT_VB = ""  # the ib or vb hash you want to merge.

# NarakaBladepoint
NARAKA_ELEMENT_NUMBER = b"13"  # from 0 to 13.
Naraka_ROOT_VS = "e8425f64cfb887cd"  # NarakaBladepoint's root hash.
Naraka_INPUT_VB = "9f655a36"  # the ib or vb hash you want to merge.


# global variables
Naraka_related_vb_indexlist = []
# The related file number indices from your input vb or ib hash.
# looks like:000001,000002,000003, use this to confirm which file should be moved to output folder.

def get_header_infos(vb_file_name):
    """
    :param vb_file_name: the filename you want to extract header info.
    :return: return a VertexModel which has the vb file header info.
    """
    vb_file = open(vb_file_name, 'rb')
    # print("开始读取vbModel")
    # ★初始化信息装载
    naraka_vb_model = VertexModel()

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
            # stride只打印出来看看，因为之前已经设置过了
            # if line.startswith(b"stride: "):
            #     stride = line[line.find(b"stride: ") + b"stride: ".__len__():line.find(b"\r\n")]
            #     # print("stride: " + str(stride))

            # 设置first_vertex,因为所有文件的first_vertex都是相同的，都是0，所以这里会取最后一次的first_vertex
            if line.startswith(b"first vertex: "):
                first_vertex = line[line.find(b"first vertex: ") + b"first vertex: ".__len__():line.find(b"\r\n")]
                naraka_vb_model.first_vertex = first_vertex
                # print("first_vertex: " + str(first_vertex))
            # 设置vertex_count,因为所有文件的vertex_count都是相同的，所以这里会取最后一次的vertex_count
            if line.startswith(b"vertex count: "):
                vertex_count = line[line.find(b"vertex count: ") + b"vertex count: ".__len__():line.find(b"\r\n")]
                naraka_vb_model.vertex_count = vertex_count
                # print("first_vertex: " + str(vertex_count))
            # 设置topology,因为所有文件的topology都是相同的，所以这里会取最后一次的topology
            if line.startswith(b"topology: "):
                topology = line[line.find(b"topology: ") + b"topology: ".__len__():line.find(b"\r\n")]
                naraka_vb_model.topology = topology
                # print("topology: " + str(naraka_vb_model.topology))

            if naraka_vb_model.topology is not None:
                # print("标题基础信息部分处理完成")
                # print("----------------------------------------------------------------")
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
                # print("element_number: " + str(element_tmp.element_number))

            if line.startswith(b"  SemanticName: "):
                semantic_name = line[line.find(b"  SemanticName: ") + b"  SemanticName: ".__len__():line.find(b"\r\n")]
                element_tmp.semantic_name = semantic_name
                # print("semantic_name: " + str(element_tmp.semantic_name))

            if line.startswith(b"  SemanticIndex: "):
                semantic_index = line[
                                 line.find(b"  SemanticIndex: ") + b"  SemanticIndex: ".__len__():line.find(b"\r\n")]
                element_tmp.semantic_index = semantic_index
                # print("semantic_index: " + str(element_tmp.semantic_index))

            if line.startswith(b"  Format: "):
                format = line[line.find(b"  Format: ") + b"  Format: ".__len__():line.find(b"\r\n")]
                element_tmp.format = format
                # print("format: " + str(element_tmp.format))

            if line.startswith(b"  InputSlot: "):
                input_slot = line[line.find(b"  InputSlot: ") + b"  InputSlot: ".__len__():line.find(b"\r\n")]
                element_tmp.input_slot = input_slot
                # 因为最终都在一个文件里面，所以所有的input_slot都设置为0
                element_tmp.input_slot = b"0"
                # print("input_slot: " + str(element_tmp.input_slot))

            if line.startswith(b"  AlignedByteOffset: "):
                aligned_byte_offset = line[line.find(
                    b"  AlignedByteOffset: ") + b"  AlignedByteOffset: ".__len__():line.find(b"\r\n")]
                element_tmp.aligned_byte_offset = aligned_byte_offset
                # print("aligned_byte_offset: " + str(element_tmp.aligned_byte_offset))

            if line.startswith(b"  InputSlotClass: "):
                input_slot_class = line[line.find(b"  InputSlotClass: ") + b"  InputSlotClass: ".__len__():line.find(
                    b"\r\n")]
                element_tmp.input_slot_class = input_slot_class
                # print("input_slot_class: " + str(element_tmp.input_slot_class))

            if line.startswith(b"  InstanceDataStepRate: "):
                instance_data_step_rate = line[line.find(
                    b"  InstanceDataStepRate: ") + b"  InstanceDataStepRate: ".__len__():line.find(b"\r\n")]
                element_tmp.instance_data_step_rate = instance_data_step_rate
                # print("instance_data_step_rate: " + str(element_tmp.instance_data_step_rate))
                # print("----------------------------------------------------------------")
                # element_tmp加入list
                element_list.append(element_tmp)
                # 单个处理完毕
                elements_single_process_over = True

            if element_tmp.element_number == NARAKA_ELEMENT_NUMBER and elements_single_process_over:
                # print("所有Element处理完毕")
                # print(element_list)
                naraka_vb_model.elementlist = element_list
                # print("----------------------------------------------------------------")
                elements_all_process_over = True
                break

    # 读取完header部分后，关闭文件
    vb_file.close()
    # print("vb文件header部分读取完成！")
    # print("----------------------------------------------------------------")
    # print(naraka_vb_model.elementlist)
    # TODO 返回前设置正确的AlignedByteOffset
    # TODO 设置正确的AlignedByteOffset后，把它们的bytewidth相加得到最终的stride从

    # 设置正确的bytewidth和AlignedByteOffset,这里注意数字是手动计算出来的
    rectified_element_list = []
    for element in naraka_vb_model.elementlist:
        if element.semantic_name == b"POSITION":
            element.byte_width = 12
            element.aligned_byte_offset = get_offset_by_name(b"POSITION")
        if element.semantic_name == b"NORMAL":
            element.byte_width = 12
            element.aligned_byte_offset = get_offset_by_name(b"NORMAL")
        if element.semantic_name == b"TANGENT":
            element.byte_width = 16
            element.aligned_byte_offset = get_offset_by_name(b"TANGENT")
        if element.semantic_name == b"COLOR":
            element.byte_width = 16
            element.aligned_byte_offset = get_offset_by_name(b"COLOR")
        if element.semantic_name == b"TEXCOORD":
            element.byte_width = 16
            element.aligned_byte_offset = get_offset_by_name(b"TEXCOORD",element.semantic_index)
        if element.semantic_name == b"BLENDWEIGHTS":
            element.byte_width = 16
            element.aligned_byte_offset = get_offset_by_name(b"BLENDWEIGHTS")
        if element.semantic_name == b"BLENDINDICES":
            element.byte_width = 16
            element.aligned_byte_offset = get_offset_by_name(b"BLENDINDICES")
        rectified_element_list.append(element)

    naraka_vb_model.elementlist = rectified_element_list
    # 设置最终正确的步长
    naraka_vb_model.stride = b"208"
    return naraka_vb_model


def get_offset_by_name(element_name, semantic_index = b"0"):
    """
    get aligned byte offset by name
    :param element_name:
    :return:
    """
    aligned_byte_offset = b"0"

    if element_name == b"POSITION":
        aligned_byte_offset = b"0"

    if element_name == b"NORMAL":
        aligned_byte_offset = b"12"

    if element_name == b"TANGENT":
        aligned_byte_offset = b"24"

    if element_name == b"COLOR":
        aligned_byte_offset = b"40"

    if element_name.startswith(b"TEXCOORD") and element_name.__len__() > 8:
        name = element_name.decode()
        tex_num = int(name[name.find("TEXCOORD")+8:name.find("TEXCOORD")+9])
        aligned_byte_offset = str(64 + ((tex_num - 1) * 16)).encode()

    if element_name.endswith(b"TEXCOORD"):
        tex_num = int(semantic_index.decode())
        if tex_num == 0:
            aligned_byte_offset = b"56"
        else:
            aligned_byte_offset = str(64 + ((tex_num - 1) * 16)).encode()


    if element_name == b"BLENDWEIGHTS":
        aligned_byte_offset = str(64 + (16 * 7)).encode()

    if element_name == b"BLENDINDICES":
        aligned_byte_offset = str(64 + (16 * 8)).encode()

    return aligned_byte_offset


def get_vertex_data(vb_filenames, vertex_count):
    # warnings.warn("过时方法",DeprecationWarning)
    """
    这里拿到的是一个ib文件的vb文件列表，然后返回这个ib文件对应的vb0的vertex_data列表
    但是在新版本中，我们需要先获取所有使用到pointlist技术的ib文件，然后对每个ib文件都获取vertex_data列表，并组成一个数据结构放入到pointlist技术列表中
    然后我们遍历pointlist技术列表，用拿到的vertex_count去对比pointlist技术列表其中的vertexcount，
    如果vertexcount值相同，就用pointlist里的值替换我们当前列表的值
    :param vb_filenames:
    :param vertex_count:
    :return:
    """
    # TODO 这里要使用pointlist技术中的姿态
    # print("开始读取vertex data 列表")
    # print(int(str(vertex_count.decode())))  5573

    # vertex data 列表 ,这里要注意，如果使用[VertexData()] * int(str(vertex_count.decode())) 则创建出的列表所有元素都是同一个元素
    vertex_data_list = [VertexData() for i in range(int(str(vertex_count.decode())))]
    # print("初始化vertex_data_list完成")

    # print(len(vertex_data_list)) 5573

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


def output_model_txt(naraka_vb_model, vertex_data_list, output_filename):
    print("开始写出文件: " + output_filename)
    # 首先解决VertexData部分缺失，但是Element部分存在，导致合成的结果无法正常导入Blender的问题。
    # 抽取第一个vertex_data，判断它哪些属性存在
    vertex_data_test = vertex_data_list[0]
    element_has_list = []
    # 默认都没有，检测到一个算一个

    if vertex_data_test.POSITION is not None:
        element_has_list.append(b"POSITION")
    if vertex_data_test.NORMAL is not None:
        element_has_list.append(b"NORMAL")
    if vertex_data_test.TANGENT is not None:
        element_has_list.append(b"TANGENT")
    if vertex_data_test.COLOR is not None:
        element_has_list.append(b"COLOR")

    if vertex_data_test.TEXCOORD is not None:
        element_has_list.append(b"TEXCOORD")
    if vertex_data_test.TEXCOORD1 is not None:
        element_has_list.append(b"TEXCOORD1")

    if vertex_data_test.TEXCOORD2 is not None:
        element_has_list.append(b"TEXCOORD2")
    if vertex_data_test.TEXCOORD3 is not None:
        element_has_list.append(b"TEXCOORD3")
    if vertex_data_test.TEXCOORD4 is not None:
        element_has_list.append(b"TEXCOORD4")
    if vertex_data_test.TEXCOORD5 is not None:
        element_has_list.append(b"TEXCOORD5")
    if vertex_data_test.TEXCOORD6 is not None:
        element_has_list.append(b"TEXCOORD6")
    if vertex_data_test.TEXCOORD7 is not None:
        element_has_list.append(b"TEXCOORD7")


    if vertex_data_test.BLENDWEIGHTS is not None:
        element_has_list.append(b"BLENDWEIGHTS")
    if vertex_data_test.BLENDINDICES is not None:
        element_has_list.append(b"BLENDINDICES")

    # 输出到最终文件
    output_file = open(output_filename, "wb+")

    # (1) 首先输出header
    output_file.write(b"stride: " + naraka_vb_model.stride + b"\r\n")
    output_file.write(b"first vertex: " + naraka_vb_model.first_vertex + b"\r\n")
    output_file.write(b"vertex count: " + naraka_vb_model.vertex_count + b"\r\n")
    output_file.write(b"topology: " + naraka_vb_model.topology + b"\r\n")

    # (2) 遍历Elementlist,根据是否存在element来写入对应内容
    element_list = naraka_vb_model.elementlist
    for element in element_list:
        element_name = element.semantic_name
        semantic_index = element.semantic_index
        if element_name == b"TEXCOORD":
            if semantic_index != b'0':
                element_name = element_name + semantic_index

        if element_has_list.__contains__(element_name):
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

    # TODO 写出之前要替换掉正确的byteoffset

    # 遍历vertex_data_list
    # print(len(vertex_data_list))
    for index in range(len(vertex_data_list)):
        vertex_data = vertex_data_list[index]
        # print(index)
        if vertex_data.POSITION is not None:
            output_file.write(vertex_data.POSITION)
        if vertex_data.NORMAL is not None:
            output_file.write(vertex_data.NORMAL)
        if vertex_data.TANGENT is not None:
            output_file.write(vertex_data.TANGENT)
        if vertex_data.COLOR is not None:
            output_file.write(vertex_data.COLOR)
        if vertex_data.TEXCOORD is not None:
            output_file.write(vertex_data.TEXCOORD)
        if vertex_data.TEXCOORD1 is not None:
            output_file.write(vertex_data.TEXCOORD1)
        if vertex_data.TEXCOORD2 is not None:
            output_file.write(vertex_data.TEXCOORD2)
        if vertex_data.TEXCOORD3 is not None:
            output_file.write(vertex_data.TEXCOORD3)
        if vertex_data.TEXCOORD4 is not None:
            output_file.write(vertex_data.TEXCOORD4)
        if vertex_data.TEXCOORD5 is not None:
            output_file.write(vertex_data.TEXCOORD5)
        if vertex_data.TEXCOORD6 is not None:
            output_file.write(vertex_data.TEXCOORD6)
        if vertex_data.TEXCOORD7 is not None:
            output_file.write(vertex_data.TEXCOORD7)
        if vertex_data.BLENDWEIGHTS is not None:
            output_file.write(vertex_data.BLENDWEIGHTS)
        if vertex_data.BLENDINDICES is not None:
            output_file.write(vertex_data.BLENDINDICES)

        # 如果是最后一行，就不追加换行符
        if index != len(vertex_data_list) - 1:
            output_file.write(b"\r\n")

    output_file.close()


def main():
    # 设置当前目录
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    print("当前工作目录：" + str(os.path.abspath(os.path.dirname(__file__))))
    print("----------------------------------------------------------------")

    # 创建output目录，用于存放输出后的脚本
    if not os.path.exists('output'):
        os.mkdir('output')

    # Make a list of all vertex buffer indices in the current folder
    # NOTE: Will *not* include index buffers without vertex data! (i.e. ib files without corresponding vb files)
    indices = sorted([re.findall('^\d+', x)[0] for x in glob.glob('*-vb0*txt')])


    # TODO 创建一个用来装pointlist的vb信息的列表
    pointlist_vb_list = []
    triangle_vb_list = []


    for file_index in range(len(indices)):
        # 获取IB文件列表，要么没有，要么只有一个
        ib_files = glob.glob(indices[file_index] + '-ib*txt')
        # 首先获取当前index的所有VB文件的列表
        vb_filenames = sorted(glob.glob(indices[file_index] + '-vb*txt'))

        # 如果不存在ib文件，则直接跳过此索引不进行处理
        if ib_files.__len__() == 0:
            print("由于blender暂不支持无ib文件类型，所以跳过不处理")
            continue

            # # 此段代码未来有可能会启用，暂时保留，目前不处理此类型
            # # 长度为0说明没有IB文件，此时直接读取第一个vb文件判断是否为pointlist
            # vb_filename = vb_filenames[0]
            # print("正在处理特殊类型--无IB文件,只有VB文件: " + vb_filename + "  ....")
            #
            # # 校验第一个vb文件是否为pointlist类型
            # if os.path.exists(vb_filename):
            #     pointlist_flag = is_pointlist_file(vb_filename)
            #     if pointlist_flag:
            #         print("blender暂不支持导入pointlist文件，跳过...")
            #         continue


        ib_filename = str(glob.glob(indices[file_index] + '-ib*txt')[0])
        print("正在处理: " + ib_filename + "  ....")



        # 读取当前ib文件判断topology是否为Pointlist

        # 第二步：处理VB文件
        # 把这个IndexBuffer里的所有VB文件的内容融合到一个单独的VB文件中

        # (1)读取一个vb文件的Header部分数据,因为header部分长得都一样，所以默认用vb0来读取
        # ★初始化并读取header部分信息
        first_vb_filename = vb_filenames[0]

        vertex_model = get_header_infos(first_vb_filename)

        # ★设置当前所属Index
        vertex_model.file_index = file_index

        # ★遍历所有vb文件，读取VertexData部分数据
        vertex_data = get_vertex_data(vb_filenames, vertex_model.vertex_count)


        # (2) 判断是pointlsit还是trianglist
        # 如果有IB文件，就把IB(index buffer)文件复制到output目录，直接复制不修改内容
        if os.path.exists(ib_filename):
            # 遇到pointlist自动跳过且不复制到output目录
            # 判断是否为topology
            pointlist_flag = is_pointlist_file(ib_filename)
            # TODO 这里注意，pointlist文件只用来获取真实的骨骼信息，而不移动到output目录
            # 这里如果是pointlist文件，就加入专属列表，如果是tranglelist，就加入tranglist列表
            output_filename = 'output/' + first_vb_filename

            # TODO 这里是pointlist的基础上，文件名中还必须包含根源VB，可能因为正确的blendwidth 和 blendindices是包含在根源VB里的
            # TODO 这里ib的文件名还要包含我们指定的vb，限制范围，防止出现找到多个pointlist
            if pointlist_flag and ib_filename.__contains__(Naraka_ROOT_VS):
                pointlist_vb = VbFileInfo()
                pointlist_vb.vertex_model = vertex_model
                pointlist_vb.vertex_data = vertex_data
                pointlist_vb.output_filename = output_filename
                pointlist_vb_list.append(pointlist_vb)
            elif ib_filename.__contains__(Naraka_INPUT_VB):
                trianglelist_vb = VbFileInfo()
                trianglelist_vb.vertex_model = vertex_model
                trianglelist_vb.vertex_data = vertex_data
                trianglelist_vb.output_filename = output_filename
                triangle_vb_list.append(trianglelist_vb)
                # 复制ib文件到output目录
                shutil.copy2(ib_filename, 'output/' + ib_filename)




    # TODO 实际上，在拼接之前，就应该能从vertex_data_list中找出pointlist类型的
    # 修正trianglelist中的骨骼和blend信息
    rectified_triangle_list = []
    for triangle_vb in triangle_vb_list:
        triangle_vertex_model =  triangle_vb.vertex_model
        vertex_count = triangle_vertex_model.vertex_count

        right_pointlist_vb = None
        count = 0
        for pointlist_vb in pointlist_vb_list:
            if vertex_count == pointlist_vb.vertex_model.vertex_count:
                right_pointlist_vb = pointlist_vb
                count = count + 1

        if right_pointlist_vb is None:
            print("未找到对应的pointlist")
            print("vertexcount"+str(vertex_count))
        elif count == 1:
            print("找到了对应的pointlist，进行替换")
            # TODO 这里目前还不确定是全部替换比较好，还是只替换部分比较好,先运行试试，有可能存在element数量不一致情况
            triangle_vb.vertex_data = right_pointlist_vb.vertex_data
            # TODO 这里的步长也要替换成pointlist的步长才对
            triangle_vb.vertex_model.stride = right_pointlist_vb.vertex_model.stride
            print(right_pointlist_vb.output_filename)
        else:
            # 这里触发找到了多个对应pointlist的原因是trianglelist那里我们没有对输入的vb做限制
            print("找到了多个对应的pointlist？？？")
            exit(1)
        # 加入到修正后的列表中
        rectified_triangle_list.append(triangle_vb)

    # ★这里需要注意，因为永劫无间格式很完整不需要修复，所以这里注释掉不用了
    # 遍历修正后的列表，修复vertex_data中含有blendindices，但是语义部分没有，而导致最后导入的数据可能有问题的情况
    # new_rectified_triangle_list = []
    # for rectified_vb in rectified_triangle_list:
    #     element_list = rectified_vb.vertex_model.elementlist
    #     if len(element_list) == 8:
    #         # 如果长度为8，说明只有8个元素，缺少了blend indices元素，同时也要判断vertex_data里是否有blendindices元素
    #         if rectified_vb.vertex_data[0].BLENDINDICES is not None:
    #             print("------------------------------------------")
    #             print("找到了需要补齐的元素")
    #
    #             # 补齐element列表
    #             element = Element()
    #             # 这里的number为8是因为BH3是从0开始到7，我们在最后追加所以7+1=8
    #             element.element_number = b"8"
    #             element.semantic_name = b"BLENDINDICES"
    #             element.semantic_index = b"0"
    #             element.format = b"R32G32B32A32_UINT"
    #             element.input_slot = b"0"
    #             element.aligned_byte_offset = b'16'
    #             element.input_slot_class = b"per-vertex"
    #             element.instance_data_step_rate = b"0"
    #             rectified_vb.vertex_model.elementlist.append(element)
    #
    #     new_rectified_triangle_list.append(rectified_vb)

    # TODO 3.vertex_data部分的索引+xxx要重新赋予正确的值
    # TODO 为什么不在读取的时候替换而是写出的时候替换？都是一样的，最终写出的时候替换才是最终结果
    newlist = []
    for rectfied_vb in rectified_triangle_list:
        new_vertex_data_list = []
        vertex_data_list = rectfied_vb.vertex_data
        for vertex_data in vertex_data_list:
            vertex_data.POSITION = get_rectified_vertex(vertex_data.POSITION)
            print(vertex_data.POSITION)
            print(get_rectified_vertex(vertex_data.POSITION))
            vertex_data.NORMAL = get_rectified_vertex(vertex_data.NORMAL)
            vertex_data.TANGENT = get_rectified_vertex(vertex_data.TANGENT)
            vertex_data.COLOR = get_rectified_vertex(vertex_data.COLOR)
            vertex_data.TEXCOORD = get_rectified_vertex(vertex_data.TEXCOORD)
            vertex_data.TEXCOORD1 = get_rectified_vertex(vertex_data.TEXCOORD1)
            vertex_data.TEXCOORD2 = get_rectified_vertex(vertex_data.TEXCOORD2)
            vertex_data.TEXCOORD3 = get_rectified_vertex(vertex_data.TEXCOORD3)
            vertex_data.TEXCOORD4 = get_rectified_vertex(vertex_data.TEXCOORD4)
            vertex_data.TEXCOORD5 = get_rectified_vertex(vertex_data.TEXCOORD5)
            vertex_data.TEXCOORD6 = get_rectified_vertex(vertex_data.TEXCOORD6)
            vertex_data.TEXCOORD7 = get_rectified_vertex(vertex_data.TEXCOORD7)
            vertex_data.BLENDWEIGHTS = get_rectified_vertex(vertex_data.BLENDWEIGHTS)
            vertex_data.BLENDINDICES = get_rectified_vertex(vertex_data.BLENDINDICES)
            new_vertex_data_list.append(vertex_data)

        rectfied_vb.vertex_data = new_vertex_data_list
        newlist.append(rectfied_vb)
    rectified_triangle_list = newlist

    # (3)遍历修正后的列表并拼接vertex_data部分,然后输出
    for rectfied_vb in rectified_triangle_list:
        # 将这些vb文件的开头索引加入到列表，方便后续移动dds文件和vs-cb文件
        outputindex = str(rectfied_vb.output_filename)
        outputindex = outputindex[outputindex.find("/000")+ 1:outputindex.find("/000") + 7]
        print(outputindex)

        Naraka_related_vb_indexlist.append(outputindex)
        # 输出到文件
        output_model_txt(rectfied_vb.vertex_model, rectfied_vb.vertex_data, rectfied_vb.output_filename)


def get_rectified_vertex(vertex):
    vertex_decode = vertex.decode()
    original_index = vertex_decode[vertex_decode.find("]+"):vertex_decode.find("]+") + 2 + 3]
    original_name = vertex_decode[vertex_decode.find("]+")+6: vertex_decode.find(": ")]
    new_index = get_offset_by_name(original_name.encode()).decode()
    new_index = "]+" + new_index.zfill(3)
    vertex_decode = vertex_decode.replace(original_index, new_index)
    rectified_vertexstr = vertex_decode.encode()
    return rectified_vertexstr



def move_dds_file():
    # 设置当前目录
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    print("----------------------------------------------------------------")
    print("开始移动.dds贴图文件")

    # 创建output目录，用于存放输出后的脚本
    if not os.path.exists('output'):
        os.mkdir('output')

    # 移动dds贴图文件
    filenames = glob.glob('*.dds')
    for filename in filenames:
        if os.path.exists(filename):
            for index in Naraka_related_vb_indexlist:
                if filename.__contains__(index):
                    print("正在处理： " + filename + " ....")
                    shutil.copy2(filename, 'output/' + filename)


def move_cb_file():
    # 设置当前目录
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    print("----------------------------------------------------------------")
    print("开始移动vs-cb骨骼txt文件")

    # 创建output目录，用于存放输出后的脚本
    if not os.path.exists('output'):
        os.mkdir('output')

    # 移动vs-cb骨骼文件
    filenames = glob.glob('*vs-cb*')
    for filename in filenames:
        if os.path.exists(filename):
            # TODO 必须包含指定vb的索引才能移动，不然不移动过去
            for index in Naraka_related_vb_indexlist:
                if filename.__contains__(index):
                    print("正在移动： " + filename + " ....")
                    shutil.copy2(filename, 'output/' + filename)

    # 移动ps-cb骨骼文件
    filenames = glob.glob('*ps-cb*')
    for filename in filenames:
        if os.path.exists(filename):
            # TODO 必须包含指定vb的索引才能移动，不然不移动过去
            for index in Naraka_related_vb_indexlist:
                if filename.__contains__(index):
                    print("正在移动： " + filename + " ....")
                    shutil.copy2(filename, 'output/' + filename)


def move_buf_file():
    # 设置当前目录
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    print("----------------------------------------------------------------")
    print("开始移动.buf文件")

    # 创建output目录，用于存放输出后的脚本
    if not os.path.exists('output'):
        os.mkdir('output')

    # 移动vs-cb2骨骼文件
    filenames = glob.glob('*.buf')
    for filename in filenames:
        if os.path.exists(filename):
            print("正在处理： " + filename + " ....")
            shutil.copy2(filename, 'output/' + filename)
    pass


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















