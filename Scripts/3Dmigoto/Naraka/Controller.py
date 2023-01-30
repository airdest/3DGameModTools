from Methods import *


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

# 便于设置工作目录
work_dir = "C:/Users/Administrator/Desktop/FrameAnalysis-2023-01-29-130542/"

def move_dds_file():
    # 设置当前目录
    os.chdir(work_dir)

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
    os.chdir(work_dir)
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

def get_format_by_name(element_name, semantic_index):
    # TODO 这里的format都是照着原神导出的文件抄过来的，但是根本不明白含义，需要搞懂
    format = None

    if element_name == b"POSITION":
        format = b"R32G32B32_FLOAT"

    if element_name == b"NORMAL":
        format =  b"R32G32B32_FLOAT"

    if element_name == b"TANGENT":
        format =  b"R32G32B32A32_FLOAT"

    if element_name == b"COLOR":
        format =  b"R8G8B8A8_UNORM"

    if element_name.endswith(b"TEXCOORD"):
        if semantic_index == b"0":
            format =  b"R32G32_FLOAT"
        else:
            format = b"R32G32B32A32_FLOAT"

    if element_name == b"BLENDWEIGHTS":
        format =  b"R32G32B32A32_FLOAT"

    if element_name == b"BLENDINDICES":
        format = b"R32G32B32A32_SINT"

    return format

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
    vertex_decode = vertex.decode()
    original_index = vertex_decode[vertex_decode.find("]+"):vertex_decode.find("]+") + 2 + 3]
    original_name = vertex_decode[vertex_decode.find("]+")+6: vertex_decode.find(": ")]
    # print(original_name)
    new_index = get_offset_by_name(original_name.encode()).decode()
    new_index = "]+" + new_index.zfill(3)
    vertex_decode = vertex_decode.replace(original_index, new_index)
    rectified_vertexstr = vertex_decode.encode()
    return rectified_vertexstr


def revise_trianglelist_by_pointlist(triangle_vb_list, pointlist_vb_list):
    # 根据pointlist，修正trianglelist中的信息
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
    return rectified_triangle_list


def revise_model_by_output_control(rectified_triangle_list):
    # 传入OutputController，根据是否输出对应element元素，来决定每个元素的alignedbyteoffset和总的stride

    # 第一步: 删除不想输出的element，反过来说就是只保留你想要的element
    # 这里naraka删除TEXCOORD1到TEXCOORD7
    new_list = []
    for vbmodel in rectified_triangle_list:
        element_list = vbmodel.vertex_model.elementlist
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

            # if element.semantic_name == b"TEXCOORD" and element.semantic_index == b"1":
            #     new_element_lsit.append(element)
        vbmodel.vertex_model.elementlist = new_element_lsit
        new_list.append(vbmodel)

    rectified_triangle_list = new_list
    # 第二步: 重新计算各元素的aligned_byte_offset和总stride 还有elementnumber
    # TODO 修正所有Element的Format
    new_list = []
    for vbmodel in rectified_triangle_list:
        element_list = vbmodel.vertex_model.elementlist
        new_element_lsit = []
        aligned_byte_offset = 0
        element_number = 0
        for element in element_list:
            # 修正Format
            format = get_format_by_name(element.semantic_name,element.semantic_index)
            # print("------------------")
            # print(element.semantic_name)
            # print(format)
            # print("------------------")
            if format is not None:
                element.format = format

            # 修正aligned_byte_offset
            element.aligned_byte_offset = str(aligned_byte_offset).encode()
            # 修正element_number
            element.element_number = str(element_number).encode()
            set_offset_by_name(element.semantic_name, str(aligned_byte_offset).encode(),element.semantic_index)
            element_number = element_number + 1
            aligned_byte_offset = aligned_byte_offset + element.byte_width
            new_element_lsit.append(element)
        vbmodel.vertex_model.elementlist = new_element_lsit
        vbmodel.vertex_model.stride = str(aligned_byte_offset).encode()
        new_list.append(vbmodel)
    rectified_triangle_list = new_list


    # 第三步：vertex_data部分的element对应的索引+xxx重新赋予正确的值
    newlist = []
    for rectfied_vb in rectified_triangle_list:
        new_vertex_data_list = []
        vertex_data_list = rectfied_vb.vertex_data
        for vertex_data in vertex_data_list:
            vertex_data.POSITION = get_rectified_vertex(vertex_data.POSITION)
            # print(vertex_data.POSITION)
            # print(get_rectified_vertex(vertex_data.POSITION))
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

        rectfied_vb.vertex_data = new_vertex_data_list
        newlist.append(rectfied_vb)
    return newlist


def main():
    # 设置当前目录
    # now_path = os.path.abspath(os.path.dirname(__file__))

    os.chdir(work_dir)
    print("当前工作目录：" + str(work_dir))
    print("----------------------------------------------------------------")

    # 创建output目录，用于存放输出后的脚本
    if not os.path.exists('output'):
        os.mkdir('output')

    # 文件开头的索引数字
    indices = sorted([re.findall('^\d+', x)[0] for x in glob.glob('*-vb0*txt')])

    # 分别装载pointlist技术和triangle技术
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

        # 获取ib文件名并输出
        ib_filename = str(glob.glob(indices[file_index] + '-ib*txt')[0])
        print("正在处理: " + ib_filename + "  ....")

        # 把这个ib的index对应的所有VB文件的内容融合到一个单独的VB文件中
        # 初始化并读取第一个vb文件的header部分信息，因为所有vb文件的header部分长得都一样，所以默认用vb0来读取
        first_vb_filename = vb_filenames[0]
        vertex_model = get_header_infos(first_vb_filename)

        # 设置当前所属Index
        vertex_model.file_index = file_index

        # 遍历所有vb文件，读取VertexData部分数据
        vertex_data = get_vertex_data(vb_filenames, vertex_model.vertex_count)

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
            if pointlist_flag and ib_filename.__contains__(NARAKA_ROOT_VS):
                pointlist_vb = VbFileInfo()
                pointlist_vb.vertex_model = vertex_model
                pointlist_vb.vertex_data = vertex_data
                pointlist_vb.output_filename = output_filename
                pointlist_vb_list.append(pointlist_vb)
            # 这里ib的文件名还要包含我们指定的vb，限制范围，防止出现找到多个pointlist
            elif ib_filename.__contains__(NARAKA_INPUT_VB):
                trianglelist_vb = VbFileInfo()
                trianglelist_vb.vertex_model = vertex_model
                trianglelist_vb.vertex_data = vertex_data
                trianglelist_vb.output_filename = output_filename
                triangle_vb_list.append(trianglelist_vb)
                # 复制ib文件到output目录
                shutil.copy2(ib_filename, 'output/' + ib_filename)

    # 根据pointlist，修正trianglelist中的信息
    rectified_triangle_list = revise_trianglelist_by_pointlist(triangle_vb_list, pointlist_vb_list)

    # 传入OutputController，根据是否输出对应element元素，来决定每个元素的alignedbyteoffset和总的stride
    rectified_triangle_list = revise_model_by_output_control(rectified_triangle_list)

    # (3)遍历修正后的列表并拼接vertex_data部分,然后输出
    for rectfied_vb in rectified_triangle_list:
        # 将这些vb文件的开头索引加入到列表，方便后续移动dds文件和vs-cb文件
        outputindex = str(rectfied_vb.output_filename)
        outputindex = outputindex[outputindex.find("/000")+ 1:outputindex.find("/000") + 7]
        print(outputindex)

        Naraka_related_vb_indexlist.append(outputindex)
        # 输出到文件
        output_model_txt(rectfied_vb.vertex_model, rectfied_vb.vertex_data, rectfied_vb.output_filename)


if __name__ == "__main__":
    # 殷紫萍衣服
    # Naraka_INPUT_VB = "9f655a36"

    # 胡桃黑丝衣服
    NARAKA_INPUT_VB = "794d8782"

    main()
    move_dds_file()
    move_cb_file()

    # 默认不移动buf文件，因为对不上
    # move_buf_file()

    print("全部转换完成！")
    os.system("pause")

    # TODO 目前COLOR和TEXCOOORD1的值完全相通，但是格式不同，而去掉TEXCOORD1后，游戏中是一片白光
    # TODO 如果保留TEXCOORD1，则游戏中是横躺下来的模型，且没有动作
