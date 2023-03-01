import re
import glob
import os
import shutil


def get_topology_vertexcount(filename):
    ib_file = open(filename, "rb")
    ib_file_size = os.path.getsize(filename)
    get_topology = None
    get_vertex_count = None
    count = 0
    while ib_file.tell() <= ib_file_size:
        line = ib_file.readline()
        # Because topology only appear in the first 5 line,so if count > 5 ,we can stop looking for it.
        count = count + 1
        if count > 5:
            break
        if line.startswith(b"vertex count: "):
            get_vertex_count = line[line.find(b"vertex count: ") + b"vertex count: ".__len__():line.find(b"\r\n")]

        if line.startswith(b"topology: "):
            topology = line[line.find(b"topology: ") + b"topology: ".__len__():line.find(b"\r\n")]
            if topology == b"pointlist":
                get_topology = b"pointlist"
                break
            if topology == b"trianglelist":
                get_topology = b"trianglelist"
                break

    # Safely close the file.
    ib_file.close()

    return get_topology, get_vertex_count


def get_pointlit_and_trianglelist_indices(input_ib_hash, root_vs="", use_root_vs=True):
    # The index number at the front of every file's filename.
    indices = sorted([re.findall('^\d+', x)[0] for x in glob.glob('*-vb0*txt')])

    pointlist_indices_dict = {}
    trianglelist_indices_dict = {}
    trianglelist_vertex_count = None
    # 1.First, grab all vb0 file's indices.
    for index in range(len(indices)):
        ib_filename = glob.glob(indices[index] + '-ib*txt')[0]

        # 优化，仅处理相关ib，其余不处理
        if input_ib_hash not in ib_filename:
            continue

        vb0_filename = glob.glob(indices[index] + '-vb0*txt')[0]
        topology, vertex_count = get_topology_vertexcount(vb0_filename)
        if topology == b"pointlist":
            if use_root_vs:
                # Filter, vb0 filename must have ROOT VS.
                if root_vs in vb0_filename:
                    pointlist_indices_dict[indices[index]] = vertex_count
            else:
                pointlist_indices_dict[indices[index]] = vertex_count


        topology, vertex_count = get_topology_vertexcount(ib_filename)
        if topology == b"trianglelist":
            # Filter,ib filename must include input_ib_hash.
            topology, vertex_count = get_topology_vertexcount(vb0_filename)
            trianglelist_indices_dict[(indices[index])] = vertex_count
            trianglelist_vertex_count = vertex_count

    # Based on vertex count, remove the duplicated pointlist indices.
    pointlist_indices = []
    trianglelist_indices = []
    for pointlist_index in pointlist_indices_dict:
        if pointlist_indices_dict.get(pointlist_index) == trianglelist_vertex_count:
            pointlist_indices.append(pointlist_index)

    for trianglelist_index in trianglelist_indices_dict:
        trianglelist_indices.append(trianglelist_index)

    print("----------------------------------------------------------")
    print("Pointlist vb indices: " + str(pointlist_indices))
    if len(pointlist_indices) == 0:
        print("This game don't use pointlist tech.")
    print("Trianglelist vb indices: " + str(trianglelist_indices))

    return pointlist_indices, trianglelist_indices


def get_unique_ib_bytes_by_indices(indices):
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


def print_all_first_index(input_ib_hash):
    """
    List all ib file's first index for an input ib hash.
    So you can test which part of a single index buffer could be removed correctly.
    Especially for the games that put a large number of object in a single index buffer.

    :return:
    """
    pointlist_indices, trianglelist_indices = get_pointlit_and_trianglelist_indices(input_ib_hash, use_root_vs=False)
    unique_ib_bytes = get_unique_ib_bytes_by_indices(trianglelist_indices)
    count = 0
    for ib_bytes in unique_ib_bytes:
        header = ib_bytes[0:100]
        first_index = header[header.find(b"first index: ") + 13:header.find(b"\r\nindex count:")]
        print("[TextureOverride_test_" + str(count) + "]")
        print("hash = " + input_ib_hash)
        print("match_first_index = " + first_index.decode())
        print("handling = skip")
        print("")

        count = count + 1


def move_ibfiles_by_indices(trianglelist_indices):
    for index in trianglelist_indices:
        ib_filename = glob.glob(index + '-ib*txt')[0]
        shutil.copy2(ib_filename, 'output/' + ib_filename)
        print("Moving: " + ib_filename)


def read_vertex_data_chunk_list_gracefully(file_index, read_element_list, only_vb1=False, sanity_check=False):
    """
    :param file_index:  the file index numbers you want to process.
    :param read_element_list:  the element name list you need to read.
    :param only_vb1:  weather read only from vb slot 1 file.
    :param sanity_check: weather check the first line to remove duplicated content.
    :return:
    """
    # Get vb filenames by the read_element_list.
    if only_vb1:
        vb_filenames = sorted(glob.glob(file_index + '-vb1*txt'))
    else:
        vb_filenames = sorted(glob.glob(file_index + '-vb*txt'))

    header_info = get_header_info(vb_filenames[0], b"9")
    vertex_count = header_info.vertex_count

    vertex_data_chunk_list = [[] for i in range(int(str(vertex_count.decode())))]

    # temp vertex_data_chunk
    vertex_data_chunk = []

    chunk_index = 0

    for filename in vb_filenames:
        # Get the vb file's slot number.
        vb_number = filename[filename.find("-vb"):filename.find("=")][1:].encode()
        # Open the vb file.
        vb_file = open(filename, 'rb')
        # For temporarily record the last line.
        line_before_tmp = b"\r\n"

        vb_file_size = os.path.getsize(vb_file.name)
        while vb_file.tell() <= vb_file_size:
            # Read a line
            line = vb_file.readline()

            # Process vertexdata
            if line.startswith(vb_number):

                line_before_tmp = line

                vertex_data = VertexData(line)
                vertex_data_chunk.append(vertex_data)
                chunk_index = int(vertex_data.index.decode())

            # Process when meet the \r\n.
            if (line.startswith(b"\r\n") or vb_file.tell() == vb_file_size) and line_before_tmp.startswith(vb_number):

                line_before_tmp = b"\r\n"

                # If we got \r\n,it means this vertex_data_chunk as ended,so put it into the final vertex_data_chunk_list.
                vertex_data_chunk_list[chunk_index].append(vertex_data_chunk)

                # Reset temp VertexData
                vertex_data_chunk = []

            if vb_file.tell() == vb_file_size:
                break
        vb_file.close()

    # Combine every chunk split part by corresponding index.
    new_vertex_data_chunk_list = []
    for vertex_data_chunk in vertex_data_chunk_list:
        new_vertex_data_chunk = []
        for vertex_data_chunk_split in vertex_data_chunk:
            for vertex_data in vertex_data_chunk_split:
                new_vertex_data_chunk.append(vertex_data)
        new_vertex_data_chunk_list.append(new_vertex_data_chunk)
    vertex_data_chunk_list = new_vertex_data_chunk_list

    # Check TEXCOORD and remove duplicated content.
    if sanity_check:
        vertex_data_chunk_check = vertex_data_chunk_list[0]
        # Count every time the different kind of data appears.
        repeat_value_time = {}
        for vertex_data in vertex_data_chunk_check:
            if repeat_value_time.get(vertex_data.data) is None:
                repeat_value_time[vertex_data.data] = 1
            else:
                repeat_value_time[vertex_data.data] = repeat_value_time[vertex_data.data] + 1
        # Decide the unique element_name by the data appears time.
        unique_element_names = []
        for vertex_data in vertex_data_chunk_check:
            if repeat_value_time.get(vertex_data.data) == 1:
                unique_element_names.append(vertex_data.element_name)
        # Retain vertex_data based on the unique element name.
        new_vertex_data_chunk_list = []
        for vertex_data_chunk in vertex_data_chunk_list:
            new_vertex_data_chunk = []
            for vertex_data in vertex_data_chunk:
                if vertex_data.element_name in unique_element_names:
                    new_vertex_data_chunk.append(vertex_data)
            new_vertex_data_chunk_list.append(new_vertex_data_chunk)
        vertex_data_chunk_list = new_vertex_data_chunk_list

    # Retain some content based on the input element_list.
    revised_vertex_data_chunk_list = []
    for index in range(len(vertex_data_chunk_list)):
        vertex_data_chunk = vertex_data_chunk_list[index]
        new_vertex_data_chunk = []
        for vertex_data in vertex_data_chunk:
            if vertex_data.element_name in read_element_list:
                new_vertex_data_chunk.append(vertex_data)
        revised_vertex_data_chunk_list.append(new_vertex_data_chunk)

    return revised_vertex_data_chunk_list

