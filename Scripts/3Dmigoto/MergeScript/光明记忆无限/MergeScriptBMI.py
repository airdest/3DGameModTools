from DataStructureBMI import *


def get_header_info(vb_file_name):
    with open(vb_file_name, 'rb') as vb_file:
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
                    semantic_name = line[
                                    line.find(b"  SemanticName: ") + b"  SemanticName: ".__len__():line.find(b"\r\n")]
                    element_tmp.semantic_name = semantic_name
                if line.startswith(b"  SemanticIndex: "):
                    semantic_index = line[
                                     line.find(b"  SemanticIndex: ") + b"  SemanticIndex: ".__len__():line.find(
                                         b"\r\n")]
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
                    input_slot_class = line[
                                       line.find(b"  InputSlotClass: ") + b"  InputSlotClass: ".__len__():line.find(
                                           b"\r\n")]
                    element_tmp.input_slot_class = input_slot_class
                if line.startswith(b"  InstanceDataStepRate: "):
                    instance_data_step_rate = line[line.find(
                        b"  InstanceDataStepRate: ") + b"  InstanceDataStepRate: ".__len__():line.find(b"\r\n")]
                    element_tmp.instance_data_step_rate = instance_data_step_rate
                    # 加入之前修正format和bytewidth
                    element_tmp.revise()
                    # element_tmp加入list
                    element_list.append(element_tmp)
                    # 单个处理完毕
                    elements_single_process_over = True

                if elements_single_process_over:
                    if line.startswith(b"\r\n"):
                        header_info.elementlist = element_list
                        elements_all_process_over = True
                        break

        return header_info


def get_vertex_data_chunk_list(vb_filenames, vertex_count):
    # vertex data 列表 ,这里要注意，如果使用[VertexData()] * int(str(vertex_count.decode())) 则创建出的列表所有元素都是同一个元素
    vertex_data_chunk_list = [[] for i in range(int(str(vertex_count.decode())))]

    print(len(vertex_data_chunk_list))

    # 最终的vertex_data_chunk
    vertex_data_chunk = []

    chunk_index = 0

    for filename in vb_filenames:
        # 首先获取当前是vb几
        vb_number = filename[filename.find("-vb"):filename.find("=")][1:].encode()
        # 打开vb文件
        vb_file = open(filename, 'rb')
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

                vertex_data = VertexData(line)
                vertex_data_chunk.append(vertex_data)
                chunk_index = int(vertex_data.index.decode())

            # 遇到换行符处理
            if (line.startswith(b"\r\n") or vb_file.tell() == vb_file_size) and line_before_tmp.startswith(vb_number):
                # 赋值上一行为\r\n的行
                line_before_tmp = b"\r\n"

                # 遇到换行符说明这一个vertex_data_chunk已经完结了，放入总trunk列表
                vertex_data_chunk_list[chunk_index].append(vertex_data_chunk)

                # 重置临时VertexData
                vertex_data_chunk = []

            if vb_file.tell() == vb_file_size:
                break
        vb_file.close()

    # 合并每个对应index对应的chunk split分段
    new_vertex_data_chunk_list = []
    for vertex_data_chunk in vertex_data_chunk_list:
        new_vertex_data_chunk = []
        for vertex_data_chunk_split in vertex_data_chunk:
            for vertex_data in vertex_data_chunk_split:
                new_vertex_data_chunk.append(vertex_data)
        new_vertex_data_chunk_list.append(new_vertex_data_chunk)

    return new_vertex_data_chunk_list


def output_model_txt(vb_file_info):
    header_info = vb_file_info.header_info
    vertex_data_chunk_list = vb_file_info.vertex_data_chunk_list
    output_filename = vb_file_info.output_filename

    # 第一步：获取vertex-data中真实存在的Element元素有哪些
    # 抽取第一个vertex_data_chunk，判断它哪些Element元素存在
    vertex_data_chunk_test = vertex_data_chunk_list[0]
    vertex_data_chunk_has_element_list = []
    # 默认都没有，检测到一个算一个
    for vertex_data_chunk in vertex_data_chunk_test:
        vertex_data_chunk_has_element_list.append(vertex_data_chunk.element_name)

    # 第二步:根据可输出的元素列表，删除header元素列表中的元素
    new_list = []
    for element in header_info.elementlist:
        element_name = element.semantic_name + element.semantic_index
        if vertex_data_chunk_has_element_list.__contains__(element_name):
            new_list.append(element)
    header_info.elementlist = new_list

    # 第三步：获取header_info中真实存在的Element元素有哪些
    # TODO 总感觉这一步有一点冗余？？？
    header_info_has_element_list = []
    for element in header_info.elementlist:
        name = element.semantic_name
        if element.semantic_name == b"ATTRIBUTE" and element.semantic_index != b"0":
            name = element.semantic_name + element.semantic_index
        header_info_has_element_list.append(name)

    # 第四步：重新计算各元素的aligned_byte_offset
    new_element_lsit, stride = get_element_byte_aligned_offset(header_info.elementlist)
    header_info.elementlist = new_element_lsit
    header_info.stride = stride

    # 第五步：vertex_data部分的element对应的索引+xxx重新赋予正确的值
    new_vertex_data_chunk_list = []
    for vertex_data_chunk in vertex_data_chunk_list:
        new_vertex_data_chunk = []
        # print(vertex_data_chunk)
        for vertex_data in vertex_data_chunk:
            new_vertex_data = vertex_data
            new_vertex_data.aligned_byte_offset = get_offset_by_name(vertex_data.element_name)
            new_vertex_data_chunk.append(new_vertex_data)
        new_vertex_data_chunk_list.append(new_vertex_data_chunk)

    vb_file_info.header_info = header_info
    vb_file_info.vertex_data_chunk_list = new_vertex_data_chunk_list

    print("开始写出文件: " + output_filename)
    with open(output_filename, "wb+") as output_file:
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
            if element_name == b"ATTRIBUTE":
                if semantic_index != b'0':
                    element_name = element_name + semantic_index

            if vertex_data_chunk_has_element_list.__contains__(element_name):
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

        # 如果允许输出，才能输出
        for index in range(len(vertex_data_chunk_list)):
            vertex_data_chunk = vertex_data_chunk_list[index]

            for vertex_data in vertex_data_chunk:
                if header_info_has_element_list.__contains__(vertex_data.element_name):
                    output_file.write(vertex_data.__str__())

            # 如果是最后一行，就不追加换行符
            if index != len(vertex_data_chunk_list) - 1:
                output_file.write(b"\r\n")


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


def get_element_byte_aligned_offset(element_list):
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


def read_trianglelist():
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
        ib_filename = str(glob.glob(indices[index_number] + '-ib*txt')[0])
        if not ib_filename.__contains__(GLOBAL_INPUT_IB):
            continue

        # 获取IB文件列表，要么没有，要么只有一个
        ib_files = glob.glob(indices[index_number] + '-ib*txt')

        # 首先获取当前index的所有VB文件的列表
        vb_filenames = sorted(glob.glob(indices[index_number] + '-vb*txt'))

        # 如果不存在ib文件，则直接跳过此索引不进行处理
        if ib_files.__len__() == 0:
            print("This version of script can not process vb information without ib file.")
            continue


        print("正在处理: " + ib_filename + "  ....")
        # 把这个ib的index对应的所有VB文件的内容融合到一个单独的VB文件中
        # 初始化并读取第一个vb文件的header部分信息，因为所有vb文件的header部分长得都一样，所以默认用vb0来读取
        first_vb_filename = vb_filenames[0]

        header_info = get_header_info(first_vb_filename)

        # 设置当前所属Index
        header_info.file_index = index_number

        # 遍历所有vb文件，读取VertexData部分数据
        vertex_data_chunk_list = get_vertex_data_chunk_list(vb_filenames, header_info.vertex_count)

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
            if pointlist_flag:
                pointlist_vb = VbFileInfo()
                pointlist_vb.header_info = header_info
                pointlist_vb.vertex_data_chunk_list = vertex_data_chunk_list
                pointlist_vb.output_filename = output_filename
                pointlist_topology.append(pointlist_vb)
            # 这里ib的文件名还要包含我们指定的vb，限制范围，防止出现找到多个pointlist
            elif ib_filename.__contains__(GLOBAL_INPUT_IB):
                trianglelist_vb = VbFileInfo()
                trianglelist_vb.header_info = header_info
                trianglelist_vb.vertex_data_chunk_list = vertex_data_chunk_list
                trianglelist_vb.output_filename = output_filename
                trianglelist_topology.append(trianglelist_vb)
                # 复制ib文件到output目录
                shutil.copy2(ib_filename, 'output/' + ib_filename)

    return pointlist_topology, trianglelist_topology


if __name__ == "__main__":
    GLOBAL_INPUT_IB = "031b8d4e"  # 夏日派对衣服

    # setting work dir
    WORK_DIR = "C:/Users/Administrator/Desktop/FrameAnalysis-2023-01-31-165121/"
    # 设置当前工作目录
    os.chdir(WORK_DIR)
    print("当前工作目录：" + str(WORK_DIR))

    # 创建output目录，用于存放输出后的脚本
    if not os.path.exists('output'):
        os.mkdir('output')

    # 读取pointlist 和 trianglelist
    # TODO，因为没有pointlist技术，所以不会读取，所以要删除
    pointlist_vb_list, triangle_vb_list = read_trianglelist()
    # (3)遍历修正后的列表并拼接vertex_data部分,然后输出
    for triangle_vb_file_info in triangle_vb_list:
        # 将这些vb文件的开头索引加入到列表，方便后续移动dds文件和vs-cb文件
        RELATED_VB_INDEX_LIST.append(str(triangle_vb_file_info.header_info.file_index).zfill(6))
        # 输出到文件
        output_model_txt(triangle_vb_file_info)

    # 移动相关联的文件
    move_related_files()
    print("全部转换完成！")

