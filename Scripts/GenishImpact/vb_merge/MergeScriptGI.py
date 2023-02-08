from MergeStructureGI import *


def get_header_info(vb_file_name, max_element_number):

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
                # 加入之前修正format和bytewidth
                element_tmp.revise()
                # element_tmp加入list
                element_list.append(element_tmp)
                # 单个处理完毕
                elements_single_process_over = True

            if element_tmp.element_number == max_element_number and elements_single_process_over:
                header_info.elementlist = element_list
                elements_all_process_over = True
                break

    # 读取完header部分后，关闭文件
    vb_file.close()
    return header_info


def read_vertex_data_chunk_list_gracefully(file_index, read_element_list):
    # 根据接收到的index，获取vb文件列表
    vb_filenames = sorted(glob.glob(file_index + '-vb*txt'))

    header_info = get_header_info(vb_filenames[0], b"9")
    vertex_count = header_info.vertex_count

    # TODO 需要一个方法，接收一个索引，读取这个index对应的vb文件中参数指定的semantic name 列表的vertex-data
    # vertex data 列表 ,这里要注意，如果使用[VertexData()] * int(str(vertex_count.decode())) 则创建出的列表所有元素都是同一个元素
    vertex_data_chunk_list = [[] for i in range(int(str(vertex_count.decode())))]

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
    vertex_data_chunk_list = new_vertex_data_chunk_list

    # 根据传进来的要读取element_list,保留部分内容
    # TODO 优化，先统计可以输出的元素的索引，再遍历，把对应索引放到新的列表不就行了，节省很多资源
    revised_vertex_data_chunk_list = []
    for index in range(len(vertex_data_chunk_list)):
        vertex_data_chunk = vertex_data_chunk_list[index]
        new_vertex_data_chunk = []
        for vertex_data in vertex_data_chunk:
            if vertex_data.element_name in read_element_list:
                new_vertex_data_chunk.append(vertex_data)
        revised_vertex_data_chunk_list.append(new_vertex_data_chunk)


    return revised_vertex_data_chunk_list



def output_model_txt(vb_file_info):
    header_info = vb_file_info.header_info
    vertex_data_chunk_list = vb_file_info.vertex_data_chunk_list
    output_filename = vb_file_info.output_filename

    print("开始写出文件: " + output_filename)
    # 首先解决VertexData部分缺失，但是Element部分存在，导致合成的结果无法正常导入Blender的问题。
    # 抽取第一个vertex_data，判断它哪些属性存在
    vertex_data_chunk_test = vertex_data_chunk_list[0]
    vertex_data_chunk_has_element_list = []
    # 默认都没有，检测到一个算一个
    # TODO 这里为什么输出的时候不对？为什么这里的vertex_data类型是list？？？
    for vertex_data in vertex_data_chunk_test:
        vertex_data_chunk_has_element_list.append(vertex_data.element_name)

    # 获取可以输出的元素列表
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
        vertex_data = vertex_data_chunk_list[index]

        for vertex_data in vertex_data:
            if header_info_has_element_list.__contains__(vertex_data.element_name):
                output_file.write(vertex_data.__str__())

        # 如果是最后一行，就不追加换行符
        if index != len(vertex_data_chunk_list) - 1:
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


def move_related_files(move_dds=True, move_vscb=True,move_pscb=True):
    # 创建output目录，用于存放输出后的脚本
    if not os.path.exists('output'):
        os.mkdir('output')

    if move_dds:
        print("----------------------------------------------------------------")
        print("开始移动.dds贴图文件")
        # 移动dds贴图文件
        filenames = glob.glob('*.dds')
        for filename in filenames:
            if os.path.exists(filename):
                for index in RELATED_VB_INDEX_LIST:
                    if filename.__contains__(index):
                        # print("正在处理： " + filename + " ....")
                        shutil.copy2(filename, 'output/' + filename)

    if move_vscb:
        print("----------------------------------------------------------------")
        print("开始移动vs-cb骨骼txt文件")
        # 移动vs-cb骨骼文件
        filenames = glob.glob('*vs-cb*')
        for filename in filenames:
            if os.path.exists(filename):
                # 必须包含指定vb的索引才能移动
                for index in RELATED_VB_INDEX_LIST:
                    if filename.__contains__(index):
                        # print("正在移动： " + filename + " ....")
                        shutil.copy2(filename, 'output/' + filename)

    if move_pscb:
        print("----------------------------------------------------------------")
        print("开始移动ps-cb骨骼txt文件")
        # 移动ps-cb骨骼文件
        filenames = glob.glob('*ps-cb*')
        for filename in filenames:
            if os.path.exists(filename):
                # 必须包含指定vb的索引才能移动
                for index in RELATED_VB_INDEX_LIST:
                    if filename.__contains__(index):
                        # print("正在移动： " + filename + " ....")
                        shutil.copy2(filename, 'output/' + filename)


def start_merge(input_ib_hash, root_vs="653c63ba4a73ca8b"):
    # 文件开头的索引数字
    indices = sorted([re.findall('^\d+', x)[0] for x in glob.glob('*-vb0*txt')])

    # 分别装载pointlist技术和triangle技术
    pointlist_topology = []
    trianglelist_topology = []

    for index_number in range(len(indices)):
        # 获取IB文件列表，要么没有，要么只有一个,如果不存在ib文件，则直接跳过此索引不进行处理
        ib_files = glob.glob(indices[index_number] + '-ib*txt')
        has_ib_file = True
        if ib_files.__len__() == 0:
            has_ib_file = False

        # 获取VB文件列表，如果没有则直接跳过此索引不处理
        vb_files = glob.glob(indices[index_number] + '-vb*txt')
        has_vb_file = True
        if vb_files.__len__() == 0:
            has_vb_file = False

        # 默认不是pointlist，后续条件判断决定最终结果
        pointlist_flag = False

        # 如果ib和vb都没有，那就可以跳过了
        if not has_ib_file and not has_vb_file:
            continue

        if not has_ib_file and has_vb_file:
            pointlist_flag = True

        # 首先获取当前index的所有VB文件的列表
        vb_filenames = sorted(glob.glob(indices[index_number] + '-vb*txt'))

        # 获取ib文件名并输出
        ib_filename = ""
        if glob.glob(indices[index_number] + '-ib*txt').__len__() != 0:
            ib_filename = str(glob.glob(indices[index_number] + '-ib*txt')[0])
        else:
            print("特殊情况，无ib文件")
        print("正在处理: " + indices[index_number] + "  ....")

        # 把这个ib的index对应的所有VB文件的内容融合到一个单独的VB文件中
        # 初始化并读取第一个vb文件的header部分信息，因为所有vb文件的header部分长得都一样，所以默认用vb0来读取
        first_vb_filename = vb_filenames[0]

        # 判断是pointlsit还是trianglist
        if has_ib_file:
            pointlist_flag = is_pointlist_file(ib_filename)

        # 这里要区别开进行处理，pointlist是9,trianglelist是7
        if pointlist_flag:
            header_info = get_header_info(first_vb_filename, b"9")
        else:
            header_info = get_header_info(first_vb_filename, b"7")


        # 设置当前所属Index
        header_info.file_index = indices[index_number]

        # 这里如果是pointlist文件，就加入专属列表，如果是tranglelist，就加入tranglist列表
        # 这里是pointlist的基础上，文件名中还必须包含根源VB，可能因为正确的blendwidth 和 blendindices是包含在根源VB里的
        if pointlist_flag and (ib_filename.__contains__(root_vs) or first_vb_filename.__contains__(root_vs)):
            pointlist_vb = VbFileInfo()
            pointlist_vb.header_info = header_info
            pointlist_topology.append(pointlist_vb)
        # 这里ib的文件名还要包含我们指定的ib，限制范围，防止出现找到多个pointlist
        elif not pointlist_flag and ib_filename.__contains__(input_ib_hash):
            trianglelist_vb = VbFileInfo()
            trianglelist_vb.header_info = header_info
            trianglelist_topology.append(trianglelist_vb)
            # 复制ib文件到output目录
            # shutil.copy2(ib_filename, 'output/' + ib_filename)
        else:
            # print("此ib文件与设定的IB输入不同，不做处理")
            pass

    # 选举机制，首先获取所有可能的pointlist的索引
    print("------------------------------------------------")
    print("选举pointlist技术的最终索引列表")

    pointlist_indices = []
    trianglelist_indices = []

    for triangle_vb in trianglelist_topology:
        vertex_count = triangle_vb.header_info.vertex_count

        # 寻找对应vertex_count长度的pointlist
        right_pointlist_vb = None
        count = 0
        for pointlist_vb in pointlist_topology:
            if vertex_count == pointlist_vb.header_info.vertex_count:
                right_pointlist_vb = pointlist_vb
                count = count + 1

        print("--------------------------------------------------------")
        print("当前正在处理：" + str(triangle_vb.header_info.file_index))

        if right_pointlist_vb is None:
            # 这里未找到对应pointlist也要加入，因为这个vb中可能包含正确的TEXCOORD信息。
            trianglelist_indices.append(triangle_vb.header_info.file_index)
        elif count == 1:
            pointlist_indices.append(right_pointlist_vb.header_info.file_index)
            trianglelist_indices.append(triangle_vb.header_info.file_index)
        else:
            # 这里触发找到了多个对应pointlist的原因是trianglelist那里我们没有对输入的vb做限制
            print("找到了多个对应的pointlist？？？")
            exit(1)

    # TODO 这里找到的pointlist可能是重复的，需要去重
    new_pointlist_indices = []
    for pointlist_index in pointlist_indices:
        if pointlist_index not in new_pointlist_indices:
            new_pointlist_indices.append(pointlist_index)
    pointlist_indices = new_pointlist_indices

    print(new_pointlist_indices)
    print(trianglelist_indices)
    # TODO 这里要注意，上面的代码效率很低，现在暂时不优化，后面再搞优化

    # 要从pointlist中读取的element,这里只读一个文件
    read_pointlist_element_list = [b"POSITION", b"NORMAL", b"TANGENT", b"BLENDWEIGHT", b"BLENDINDICES"]
    pointlist_vertex_data_chunk_list = read_vertex_data_chunk_list_gracefully(pointlist_indices[0], read_pointlist_element_list)

    # 要从trianglelist中读取的element，这里要读很多文件
    read_trianglelist_element_list = [b"COLOR", b"TEXCOORD", b"TEXCOORD1"]
    final_trianglelist_vertex_data_chunk_list_list = []
    for trianglelist_index in trianglelist_indices:
        vertex_data_chunk_list_tmp = read_vertex_data_chunk_list_gracefully(trianglelist_index, read_trianglelist_element_list)
        final_trianglelist_vertex_data_chunk_list_list.append(vertex_data_chunk_list_tmp)
    print(len(final_trianglelist_vertex_data_chunk_list_list))

    # TODO 读取完trianglelist的vertex-data后，进行格式检查，从而找出最终的element正确的vertex-data
    repeat_vertex_data_chunk_list_list = []
    for final_trianglelist_vertex_data_chunk_list in final_trianglelist_vertex_data_chunk_list_list:
        first_vertex_data_chunk = final_trianglelist_vertex_data_chunk_list[0]
        length = len(first_vertex_data_chunk)

        unique_data_list = []
        new_vertex_data_chunk = []
        for vertex_data in first_vertex_data_chunk:
            if vertex_data.data not in unique_data_list:
                unique_data_list.append(vertex_data.data)
                new_vertex_data_chunk.append(vertex_data)

        right_texcoord = False
        right_texcoord1 = False
        if len(unique_data_list) == length:
            for vertex_data in new_vertex_data_chunk:
                if len(str(vertex_data.data.decode()).split(",")) == 2 and str(vertex_data.element_name.decode()).endswith("TEXCOORD"):
                    right_texcoord = True

                if len(str(vertex_data.data.decode()).split(",")) == 2 and str(vertex_data.element_name.decode()).endswith("TEXCOORD1"):
                    right_texcoord1 = True

        if right_texcoord and right_texcoord1:
            repeat_vertex_data_chunk_list_list.append(final_trianglelist_vertex_data_chunk_list)
        else:
            continue

    # 找出之后进行去重
    final_trianglelist_vertex_data_chunk_list_list = []
    repeat_check = []
    for final_trianglelist_vertex_data_chunk_list in repeat_vertex_data_chunk_list_list:
        # 抽取第一个进行校验，如果抽取的第一个出现过就啥都不干，没出现过就加入，很简单
        first_vertex_data_chunk = final_trianglelist_vertex_data_chunk_list[0]
        first_vertex_data = first_vertex_data_chunk[0]

        if first_vertex_data.data not in repeat_check:
            repeat_check.append(first_vertex_data.data)
            final_trianglelist_vertex_data_chunk_list_list.append(final_trianglelist_vertex_data_chunk_list)

    print("去重后的长度：")
    print(len(final_trianglelist_vertex_data_chunk_list_list))
    # 去重之后只有一个，所以取0
    final_trianglelist_vertex_data_chunk_list = final_trianglelist_vertex_data_chunk_list_list[0]

    # 根据output_element_list，拼接出一个最终的header_info
    output_element_list = [b"POSITION", b"NORMAL", b"TANGENT", b"BLENDWEIGHT", b"BLENDINDICES", b"COLOR", b"TEXCOORD", b"TEXCOORD1"]
    header_info = get_header_info_by_elementnames(output_element_list)
    # 设置vertex count
    header_info.vertex_count = str(len(final_trianglelist_vertex_data_chunk_list)).encode()

    # 根据前面几步  拼接最终的只有一个的vb0文件
    if len(pointlist_vertex_data_chunk_list) != len(final_trianglelist_vertex_data_chunk_list):
        print("pointlist的trunk和trianglelist的trunk列表长度需相同")
        exit(1)

    final_vertex_data_chunk_list = [[] for i in range(int(str(header_info.vertex_count.decode())))]
    for index in range(len(pointlist_vertex_data_chunk_list)):
        final_vertex_data_chunk_list[index] = final_vertex_data_chunk_list[index] + pointlist_vertex_data_chunk_list[index]
        final_vertex_data_chunk_list[index] = final_vertex_data_chunk_list[index] + final_trianglelist_vertex_data_chunk_list[index]

    # TODO 拼接出来之后，要设置每个VertexData的alignedbyte为正确值。
    # TODO 顺便修复element_list中出现TEXCOORD1的问题
    element_aligned_byte_offsets = {}
    new_element_list = []
    for element in header_info.elementlist:
        element_aligned_byte_offsets[element.semantic_name] = element.aligned_byte_offset
        if element.semantic_name.endswith(b"TEXCOORD1"):
            element.semantic_name = b"TEXCOORD"
        new_element_list.append(element)
    header_info.elementlist = new_element_list

    # 遍历vertex data chunk list，修正aligned byte offset
    new_final_vertex_data_chunk_list = []
    for vertex_data_chunk in final_vertex_data_chunk_list:
        new_vertex_data_chunk = []
        for vertex_data in vertex_data_chunk:
            vertex_data.aligned_byte_offset = element_aligned_byte_offsets[vertex_data.element_name]
            new_vertex_data_chunk.append(vertex_data)
        new_final_vertex_data_chunk_list.append(new_vertex_data_chunk)
    final_vertex_data_chunk_list = new_final_vertex_data_chunk_list





    output_vb_fileinfo = VbFileInfo()
    output_vb_fileinfo.header_info = header_info
    output_vb_fileinfo.vertex_data_chunk_list = final_vertex_data_chunk_list
    # 暂不设置输出到的文件名，在后面设置

    # 获取不重复的ib文件内容，准备输出ib、vb0这样的组合，vb0只有一种情况，在前面已确定好。
    ib_file_bytes = get_ib_bytes_by_indices(trianglelist_indices)

    # 输出到最终文件
    for index in range(len(ib_file_bytes)):
        ib_file_byte = ib_file_bytes[index]
        output_vbname = "output/output-" + str(index) + "-vb0.txt"
        output_ibname = "output/output-" + str(index) + "-ib.txt"
        output_vb_fileinfo.output_filename = output_vbname

        # 先写出ib文件，再写出vb文件
        output_ibfile = open(output_ibname, "wb+")
        output_ibfile.write(ib_file_byte)
        output_ibfile.close()

        output_model_txt(output_vb_fileinfo)


def get_ib_bytes_by_indices(indices):
    """
    根据给出的index列表，返回去重之后的ib文件的bytes内容列表
    """
    ib_filenames = []
    for index in range(len(indices)):
        indexnumber = indices[index]
        ib_filename = sorted(glob.glob(str(indexnumber) + '-ib*txt'))[0]
        ib_filenames.append(ib_filename)

    ib_file_bytes = []
    for ib_filename in ib_filenames:
        with open(ib_filename, "rb") as ib_file:
            bytes = ib_file.read()
            if bytes not in ib_file_bytes:
                ib_file_bytes.append(bytes)

    return ib_file_bytes


def get_header_info_by_elementnames(output_element_list):
    header_info = HeaderInfo()
    # 1.遍历output_element_list，拼接elementlist列表
    element_list = []
    for element_name in output_element_list:
        element = Element()

        element.semantic_name = element_name
        element.input_slot = b"0"
        element.input_slot_class = b"per-vertex"
        element.instance_data_step_rate = b"0"

        if element_name.endswith(b"POSITION"):
            element.semantic_index = b"0"
            element.format = b"R32G32B32_FLOAT"
            element.byte_width = 12
        elif element_name.endswith(b"NORMAL"):
            element.semantic_index = b"0"
            element.format = b"R32G32B32_FLOAT"
            element.byte_width = 12
        elif element_name.endswith(b"TANGENT"):
            element.semantic_index = b"0"
            element.format = b"R32G32B32A32_FLOAT"
            element.byte_width = 16
        elif element_name.endswith(b"BLENDWEIGHT"):
            element.semantic_index = b"0"
            element.format = b"R32G32B32A32_FLOAT"
            element.byte_width = 16
        elif element_name.endswith(b"BLENDINDICES"):
            element.semantic_index = b"0"
            element.format = b"R32G32B32A32_SINT"
            element.byte_width = 16
        elif element_name.endswith(b"COLOR"):
            element.semantic_index = b"0"
            element.format = b"R8G8B8A8_UNORM"
            element.byte_width = 4
        elif element_name.endswith(b"TEXCOORD"):
            element.semantic_index = b"0"
            element.format = b"R32G32_FLOAT"
            element.byte_width = 8
        elif element_name.endswith(b"TEXCOORD1"):
            element.semantic_index = b"1"
            element.format = b"R32G32_FLOAT"
            element.byte_width = 8

        element_list.append(element)
    # 2.遍历并补充aligned_byte_offset和element_number
    new_element_list = []
    aligned_byte_offset = 0
    for index in range(len(element_list)):
        element = element_list[index]
        element.element_number = str(index).encode()
        element.aligned_byte_offset = str(aligned_byte_offset).encode()
        aligned_byte_offset = aligned_byte_offset + element.byte_width
        new_element_list.append(element)

    # 3.设置element_list和stride
    header_info.first_vertex = b"0"
    header_info.topology = b"trianglelist"
    header_info.stride = str(aligned_byte_offset).encode()
    header_info.elementlist = new_element_list

    return header_info


if __name__ == "__main__":
    # TODO genshin的脚本命令 python genshin_3dmigoto_collect.py -vb dfb54407 -n zhujue
    # setting work dir
    os.chdir("C:/Users/Administrator/Desktop/FrameAnalysis-2023-02-06-180919/")
    if not os.path.exists('output'):
        os.mkdir('output')

    input_ib_hash = "dfb54407"  # 基础角色
    start_merge(input_ib_hash)
    print("全部转换完成！")

