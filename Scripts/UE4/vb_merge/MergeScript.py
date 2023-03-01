"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import re
import glob
import os
import shutil

# List of global variables
RELATED_VB_INDEX_LIST = []  # TODO The related file number indices from your input vb or ib hash. looks like:000001,
# 000002,000003, use this to confirm which file should be moved to output folder.


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


def get_header_info(vb_file_name, max_element_number):

    vb_file = open(vb_file_name, 'rb')

    header_info = HeaderInfo()

    # Use to control the header process.
    header_process_over = False
    # Use to control the element process.
    elements_all_process_over = False
    elements_single_process_over = False

    element_list = []

    element_tmp = Element()

    while vb_file.tell() < os.path.getsize(vb_file.name):
        # Read a line.
        line = vb_file.readline()
        # Process header part.
        if not header_process_over:
            # Set the fitst vertex,because this value in every vb file is totally same,so we get the final file's first vertex is safe.
            if line.startswith(b"first vertex: "):
                first_vertex = line[line.find(b"first vertex: ") + b"first vertex: ".__len__():line.find(b"\r\n")]
                header_info.first_vertex = first_vertex
            # Set vertex count, similarly it's safe to get the final vb file's vertex count.
            if line.startswith(b"vertex count: "):
                vertex_count = line[line.find(b"vertex count: ") + b"vertex count: ".__len__():line.find(b"\r\n")]
                header_info.vertex_count = vertex_count
            # Set topology, similarly it's safe to get the final vb file's vertex count.
            if line.startswith(b"topology: "):
                topology = line[line.find(b"topology: ") + b"topology: ".__len__():line.find(b"\r\n")]
                header_info.topology = topology

            if header_info.topology is not None:
                header_process_over = True

        # Process element list.
        if not elements_all_process_over:

            if line.startswith(b"element["):
                # If detected "element[" ,that means we start to process a new element.
                elements_single_process_over = False
                # Initialize ElementTmp
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
                # Because we finally get only one vb file,so every input_slot should be set to 0.
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

                # Put element_tmp into element_list.
                element_list.append(element_tmp)
                # Process single element over.
                elements_single_process_over = True

            if element_tmp.element_number == max_element_number and elements_single_process_over:
                header_info.elementlist = element_list
                elements_all_process_over = True
                break

    # Safely close the file.
    vb_file.close()
    return header_info


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



def output_model_txt(vb_file_info):
    header_info = vb_file_info.header_info
    vertex_data_chunk_list = vb_file_info.vertex_data_chunk_list
    output_filename = vb_file_info.output_filename

    print("Starting output to file: " + output_filename)
    # Grab the first vertex_data, and judge which element exists.
    vertex_data_chunk_test = vertex_data_chunk_list[0]
    vertex_data_chunk_has_element_list = []
    # Default we think all element does not exist,unless we detected it.
    for vertex_data in vertex_data_chunk_test:
        vertex_data_chunk_has_element_list.append(vertex_data.element_name)

    # Get the element list which can be output.
    header_info_has_element_list = []
    for element in header_info.elementlist:
        name = element.semantic_name
        if element.semantic_name == b"TEXCOORD" and element.semantic_index != b"0":
                name = element.semantic_name + element.semantic_index
        header_info_has_element_list.append(name)

    # Output to the final file.
    output_file = open(output_filename, "wb+")

    # (1) First output header.
    output_file.write(b"stride: " + header_info.stride + b"\r\n")
    output_file.write(b"first vertex: " + header_info.first_vertex + b"\r\n")
    output_file.write(b"vertex count: " + header_info.vertex_count + b"\r\n")
    output_file.write(b"topology: " + header_info.topology + b"\r\n")

    # (2) Traversal Elementlist,if element exists then output it.
    element_list = header_info.elementlist
    for element in element_list:
        element_name = element.semantic_name
        semantic_index = element.semantic_index
        if element_name == b"TEXCOORD":
            if semantic_index != b'0':
                element_name = element_name + semantic_index

        if vertex_data_chunk_has_element_list.__contains__(element_name):
            # print("Detected："+str(element_name))
            # Output the corroesponding element.
            output_file.write(b"element[" + element.element_number + b"]:" + b"\r\n")
            output_file.write(b"  SemanticName: " + element.semantic_name + b"\r\n")
            output_file.write(b"  SemanticIndex: " + element.semantic_index + b"\r\n")
            output_file.write(b"  Format: " + element.format + b"\r\n")
            output_file.write(b"  InputSlot: " + element.input_slot + b"\r\n")
            output_file.write(b"  AlignedByteOffset: " + element.aligned_byte_offset + b"\r\n")
            output_file.write(b"  InputSlotClass: " + element.input_slot_class + b"\r\n")
            output_file.write(b"  InstanceDataStepRate: " + element.instance_data_step_rate + b"\r\n")

    # (3) Write the vertex-data part.
    output_file.write(b"\r\n")
    output_file.write(b"vertex-data:\r\n")
    output_file.write(b"\r\n")

    # It's element_name must appear in header_info_has_element_list,otherwise it can't be output.
    for index in range(len(vertex_data_chunk_list)):
        vertex_data = vertex_data_chunk_list[index]

        for vertex_data in vertex_data:
            if header_info_has_element_list.__contains__(vertex_data.element_name):
                output_file.write(vertex_data.__str__())

        # If it is the final line ,we don't append \r\n.
        if index != len(vertex_data_chunk_list) - 1:
            output_file.write(b"\r\n")

    output_file.close()


def move_related_files(move_dds=True, move_vscb=True,move_pscb=True):
    # Create output folder in case it doesn't exists.
    if not os.path.exists('output'):
        os.mkdir('output')

    if move_dds:
        print("----------------------------------------------------------------")
        print("Start to move .dds files.")
        # Start to move .dds files.
        filenames = glob.glob('*.dds')
        for filename in filenames:
            if os.path.exists(filename):
                for index in RELATED_VB_INDEX_LIST:
                    if filename.__contains__(index):
                        # print("Moving ： " + filename + " ....")
                        shutil.copy2(filename, 'output/' + filename)

    if move_vscb:
        print("----------------------------------------------------------------")
        print("Start to move VS-CB files.")
        # Start to move VS-CB files.
        filenames = glob.glob('*vs-cb*')
        for filename in filenames:
            if os.path.exists(filename):
                # Must have the vb index you sepcified.
                for index in RELATED_VB_INDEX_LIST:
                    if filename.__contains__(index):
                        # print("Moving ： " + filename + " ....")
                        shutil.copy2(filename, 'output/' + filename)

    if move_pscb:
        print("----------------------------------------------------------------")
        print("Start to move PS-CB files.")
        # Start to move PS-CB files.
        filenames = glob.glob('*ps-cb*')
        for filename in filenames:
            if os.path.exists(filename):
                # Must have the vb index you sepcified.
                for index in RELATED_VB_INDEX_LIST:
                    if filename.__contains__(index):
                        # print("Moving ： " + filename + " ....")
                        shutil.copy2(filename, 'output/' + filename)

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


def get_pointlit_and_trianglelist_indices(input_ib_hash, root_vs):
    # The index number at the front of every file's filename.
    indices = sorted([re.findall('^\d+', x)[0] for x in glob.glob('*-vb0*txt')])

    pointlist_indices_dict = {}
    trianglelist_indices_dict = {}
    trianglelist_vertex_count = None
    # 1.First, grab all vb0 file's indices.
    for index in range(len(indices)):
        vb0_filename = glob.glob(indices[index] + '-vb0*txt')[0]
        topology, vertex_count = get_topology_vertexcount(vb0_filename)
        if topology == b"pointlist":
            # Filter, vb0 filename must have ROOT VS.
            if root_vs in vb0_filename:
                pointlist_indices_dict[indices[index]] = vertex_count

        ib_filename = glob.glob(indices[index] + '-ib*txt')[0]
        topology, vertex_count = get_topology_vertexcount(ib_filename)
        if topology == b"trianglelist":
            # Filter,ib filename must include input_ib_hash.
            if input_ib_hash in ib_filename:
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
    print("Trianglelist vb indices: " + str(trianglelist_indices))

    return pointlist_indices, trianglelist_indices


def output_ini_file(pointlist_indices, input_ib_hash, part_name):
    # TODO Now this function is testing, and finally will use it to generate the final .ini file.
    filenames = sorted(glob.glob(pointlist_indices[0] + '-vb*txt'))
    position_vb = filenames[0]
    position_vb = position_vb[position_vb.find("-vb0=") + 5:position_vb.find("-vs=")]

    texcoord_vb = filenames[1]
    texcoord_vb = texcoord_vb[texcoord_vb.find("-vb1=") + 5:texcoord_vb.find("-vs=")]

    blend_vb = filenames[2]
    blend_vb = blend_vb[blend_vb.find("-vb2=") + 5:blend_vb.find("-vs=")]

    # print("position_vb: " + position_vb)
    # print("texcoord_vb: " + texcoord_vb)
    # print("blend_vb: " + blend_vb)

    output_bytes = b""
    output_bytes = output_bytes + (b"[Resource_POSITION]\r\ntype = Buffer\r\nstride = 40\r\nfilename = " + part_name.encode() + b"_POSITION.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_BLEND]\r\ntype = Buffer\r\nstride = 32\r\nfilename = " + part_name.encode() + b"_BLEND.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_TEXCOORD]\r\ntype = Buffer\r\nstride = 8\r\nfilename = " + part_name.encode() + b"_TEXCOORD.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_IB_FILE]\r\ntype = Buffer\r\nformat = DXGI_FORMAT_R16_UINT\r\nfilename = " + part_name.encode() + b".ib\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_NUDE_BODY]\r\nfilename = body.png\r\n\r\n")

    output_bytes = output_bytes + (b"[TextureOverride_IB_SKIP]\r\nhash = "+input_ib_hash.encode()+b"\r\nhandling = skip\r\nib = Resource_IB_FILE\r\nps-t7 = Resource_NUDE_BODY\r\ndrawindexed = auto\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_POSITION]\r\nhash = "+position_vb.encode()+b"\r\nvb0 = Resource_POSITION\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_TEXCOORD]\r\nhash = "+texcoord_vb.encode()+b"\r\nvb1 = Resource_TEXCOORD\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_BLEND]\r\nhash = "+blend_vb.encode()+b"\r\nvb2 = Resource_BLEND\r\n\r\n")
    output_bytes = output_bytes + (b";[TextureOverride_VB_SKIP_1]\r\n;hash = \r\n;handling = skip\r\n\r\n")

    output_file = open("output/"+part_name+".ini", "wb+")
    output_file.write(output_bytes)
    output_file.close()







def start_merge_files(input_ib_hash, part_name , root_vs):
    pointlist_indices, trianglelist_indices = get_pointlit_and_trianglelist_indices(input_ib_hash,root_vs)

    output_ini_file(pointlist_indices, input_ib_hash, part_name)

    # The vertex data you want to read from pointlist vb file.
    read_pointlist_element_list = [b"POSITION", b"NORMAL", b"TANGENT", b"BLENDWEIGHTS", b"BLENDINDICES"]

    pointlist_vertex_data_chunk_list = read_vertex_data_chunk_list_gracefully(pointlist_indices[0], read_pointlist_element_list)

    # The vertex data you want to read from trianglelist vb file.
    read_trianglelist_element_list = [b"COLOR", b"TEXCOORD", b"TEXCOORD1"]

    final_trianglelist_vertex_data_chunk_list_list = []
    for trianglelist_index in trianglelist_indices:
        vertex_data_chunk_list_tmp = read_vertex_data_chunk_list_gracefully(trianglelist_index, read_trianglelist_element_list, only_vb1=True, sanity_check=True)
        final_trianglelist_vertex_data_chunk_list_list.append(vertex_data_chunk_list_tmp)

    repeat_vertex_data_chunk_list_list = []

    for final_trianglelist_vertex_data_chunk_list in final_trianglelist_vertex_data_chunk_list_list:
        first_vertex_data_chunk = final_trianglelist_vertex_data_chunk_list[0]
        # First,check if there have TEXCOORD, continue if not exists.
        element_name_list = []
        found_invalid_texcoord = False
        for vertex_data in first_vertex_data_chunk:
            element_name_list.append(vertex_data.element_name)
            datas = str(vertex_data.data.decode()).split(",")
            # Here > 2, because TEXCOORD's format must be R32G32_FLOAT.
            if vertex_data.element_name.startswith(b"TEXCOORD") and len(datas) > 2:
                found_invalid_texcoord = True
        if found_invalid_texcoord:
            continue

        if b"TEXCOORD" not in element_name_list:
            continue

        # for vertex_data in first_vertex_data_chunk:
        #     print(vertex_data.element_name)
        #     print(vertex_data.data)
        # print("-----------------------------------")
        repeat_vertex_data_chunk_list_list.append(final_trianglelist_vertex_data_chunk_list)

    # Remove duplicated contents.
    final_trianglelist_vertex_data_chunk_list_list = []
    repeat_check = []
    for final_trianglelist_vertex_data_chunk_list in repeat_vertex_data_chunk_list_list:
        # Grab the first one to check.
        first_vertex_data_chunk = final_trianglelist_vertex_data_chunk_list[0]
        first_vertex_data = first_vertex_data_chunk[0]

        # The length of final_trianglelist_vertex_data_chunk_list must equals pointlist_vertex_data_chunk_list's length.
        if len(final_trianglelist_vertex_data_chunk_list) == len(pointlist_vertex_data_chunk_list):
            if first_vertex_data.data not in repeat_check:
                repeat_check.append(first_vertex_data.data)
                final_trianglelist_vertex_data_chunk_list_list.append(final_trianglelist_vertex_data_chunk_list)

    if len(final_trianglelist_vertex_data_chunk_list_list) != 1:
        print("The length after duplicate removal should be 1!")
        exit(1)

    # After duplicate removal, there should only be one element in list,so we use index [0].
    final_trianglelist_vertex_data_chunk_list = final_trianglelist_vertex_data_chunk_list_list[0]

    # Based on output_element_list，generate a final header_info.
    output_element_list = [b"POSITION", b"NORMAL", b"TANGENT", b"BLENDWEIGHTS", b"BLENDINDICES", b"COLOR", b"TEXCOORD"]
    # TODO This output_element_list may should be generated by vertex-data chunk list's real exists element_name.

    header_info = get_header_info_by_elementnames(output_element_list)
    # Set vertex count
    header_info.vertex_count = str(len(final_trianglelist_vertex_data_chunk_list)).encode()

    # Generate a final vb file.
    if len(pointlist_vertex_data_chunk_list) != len(final_trianglelist_vertex_data_chunk_list):
        print("The length of the pointlist_vertex_data_chunk_list and the final_trianglelist_vertex_data_chunk_list should equal!")
        exit(1)

    final_vertex_data_chunk_list = [[] for i in range(int(str(header_info.vertex_count.decode())))]
    for index in range(len(pointlist_vertex_data_chunk_list)):
        final_vertex_data_chunk_list[index] = final_vertex_data_chunk_list[index] + pointlist_vertex_data_chunk_list[
            index]
        final_vertex_data_chunk_list[index] = final_vertex_data_chunk_list[index] + \
                                              final_trianglelist_vertex_data_chunk_list[index]

    # Solve TEXCOORD1 can't match the element's semantic name TEXCOORD problem.
    element_aligned_byte_offsets = {}
    new_element_list = []
    for element in header_info.elementlist:
        element_aligned_byte_offsets[element.semantic_name] = element.aligned_byte_offset
        if element.semantic_name.endswith(b"TEXCOORD1"):
            element.semantic_name = b"TEXCOORD"
        new_element_list.append(element)
    header_info.elementlist = new_element_list

    # Revise aligned byte offset
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

    ib_file_bytes = get_ib_bytes_by_indices(trianglelist_indices)

    # Output to file.
    for index in range(len(ib_file_bytes)):
        ib_file_byte = ib_file_bytes[index]
        output_vbname = "output/" + input_ib_hash + "-" + part_name + "-vb0.txt"
        output_ibname = "output/" + input_ib_hash + "-" + part_name + "-ib.txt"
        output_vb_fileinfo.output_filename = output_vbname

        # Write to ib file.
        output_ibfile = open(output_ibname, "wb+")
        output_ibfile.write(ib_file_byte)
        output_ibfile.close()

        # Write to vb file.
        output_model_txt(output_vb_fileinfo)


def get_ib_bytes_by_indices(indices):
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
    # 1.Generate element_list.
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
        elif element_name.endswith(b"BLENDWEIGHTS"):
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
    # 2.Add aligned_byte_offset and element_number.
    new_element_list = []
    aligned_byte_offset = 0
    for index in range(len(element_list)):
        element = element_list[index]
        element.element_number = str(index).encode()
        element.aligned_byte_offset = str(aligned_byte_offset).encode()
        aligned_byte_offset = aligned_byte_offset + element.byte_width
        new_element_list.append(element)

    # 3.Set element_list and stride.
    header_info.first_vertex = b"0"
    header_info.topology = b"trianglelist"
    header_info.stride = str(aligned_byte_offset).encode()
    header_info.elementlist = new_element_list

    return header_info


if __name__ == "__main__":
    # Set work dir, here is your FrameAnalysis dump dir.
    FrameAnalyseFolder = "FrameAnalysis-2023-02-12-170352"
    os.chdir("C:/Program Files (x86)/Steam/steamapps/common/BrightMemoryInfinite/BrightMemoryInfinite/Binaries/Win64/" + FrameAnalyseFolder + "/")
    if not os.path.exists('output'):
        os.mkdir('output')

    # Here is the ib you want to import into blender.
    ib_hashs = {"031b8d4e":"body"}
    for input_ib_hash in ib_hashs:
        # Naraka use e8425f64cfb887cd as it's ROOT VS, and this value is different between games which use pointlist topology.
        start_merge_files(input_ib_hash, ib_hashs.get(input_ib_hash), root_vs="e8425f64cfb887cd")

    print("----------------------------------------------------------\r\nAll process done！")

    

