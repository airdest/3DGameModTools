# Vertex buffer split script - for use with Blender exports to 3dmigoto raw buffers (ib/vb/fmt files),
# this script will split the combined vertex buffer into individual buffers for games that use separate
# buffers for each vertex element.  Execute from the directory of the buffers and it will split any vb
# files it finds that has a corresponding fmt file.  It will also create a rudimentary ini file for use
# with 3dmigoto if one doesn't already exist.  Has only been tested with TOCS4.
# GitHub eArmada8/vbuffer_merge_split

import glob, os, re, json


if __name__ == "__main__":
    # Set current directory
    os.chdir("C:/Users/Administrator/Desktop/SplitTest/")

    # Make a list of all mesh groups in the current folder, both fmt and vb files are necessary for processing
    vb_name = "guqinghan"

    print('Processing vb ' + vb_name + '...\n')
    # Determine the offsets used in the combined buffer by parsing the FMT file
    offsets = []
    with open(vb_name + '.fmt', 'r') as f:
        for line in f:
            if line[0:6] == 'stride':
                combined_stride = int(line[8:-1])
            if line[0:8] == 'format: ':
                try:
                    ib_format = str.split(str.split(line[8:], sep='_FORMAT_')[1])[0]
                except IndexError:
                    ib_format = 'UNKNOWN'
                continue
            if line[2:19] == 'AlignedByteOffset':
                offsets.append(int(line[21:-1]))
    print(offsets)

    # Determine the strides to be used in the individual buffers
    if os.path.exists(vb_name + '.splitdata'):
        # Use custom data if available
        with open(vb_name + '.splitdata', 'r') as f:
            strides = json.loads(f.read())
        combined_stride = sum(strides)
        offsets = [0]
        for i in range(1, len(strides)):
            offsets.append(offsets[i - 1] + strides[i - 1])
    else:
        strides = []
        for i in range(len(offsets)):
            if i == len(offsets) - 1:
                strides.append(combined_stride - offsets[i])
            else:
                strides.append(offsets[i + 1] - offsets[i])

    print(strides)

    # Read in the entire combined buffer
    with open(vb_name + '.vb', 'rb') as f:
        vb_read_buffer = f.read()

    # print(vb_read_buffer)

    # Count the total number of vertices
    vertex_count = int(len(vb_read_buffer) / combined_stride)
    print(combined_stride)
    print(vertex_count)  # 原始只有6071，这里为什么6085  差了14

    # Write each individual vertex buffer file, one for each element
    for index in range(len(strides)):
        # 这里的vertex_group其实就是index
        write_data = b''
        for i in range(vertex_count):
            start_index = i * combined_stride + offsets[index]
            write_data = write_data + vb_read_buffer[start_index:start_index + strides[index]]
        with open(vb_name + '.vb' + str(index), 'wb') as f:
            f.write(write_data)


    # Create the beginnings of an ini file
    ini_text = []
    # ini file - VB Resources
    for index in range(len(strides)):
        ini_text.append('[Resource_Model_' + vb_name + '_VB' + str(index) + ']\n')
        ini_text.append('type = Buffer\n')
        ini_text.append('stride = ' + str(strides[index]) + '\n')
        ini_text.append('filename = ' + vb_name + '.vb' + str(index) + '\n')
        ini_text.append('\n')

    # ini file - IB Resource
    ini_text.append('[Resource_Model_' + vb_name + '_IB]\n')
    ini_text.append('type = Buffer\n')
    ini_text.append('format = ' + ib_format + '\n')
    ini_text.append('filename = ' + vb_name + '.ib\n')
    ini_text.append('\n')

    # ini file - Texture Override
    ini_text.append(';[TextureOverride_' + vb_name + ']\n')
    ini_text.append('; *** Texture hash needs to be filled in below\n')
    ini_text.append(';hash = _________\n')
    for index in range(len(strides)):
        ini_text.append(
            ';vb' + str(index) + ' = Resource_Model_' + vb_name + '_VB' + str(index) + '\n')
    ini_text.append(';ib = Resource_Model_' + vb_name + '_IB\n')
    ini_text.append(';handling = skip\n')
    ini_text.append(';drawindexed = auto\n')
    ini_text.append('\n')

    # ini file - Shader Override
    ini_text.append(';[ShaderOverride_' + vb_name + ']\n')
    ini_text.append('; *** Pixel shader hash needs to be filled in below.\n')
    ini_text.append(
        '; *** Duplicate this section as needed if the texture is called by more than one pixel shader.\n')
    ini_text.append('; ***     (If duplicating, keep in mind each section needs its own unique name.)\n')
    ini_text.append(';hash = _________\n')
    ini_text.append('; *** Uncomment the lines below or insert run statement, depending on your 3dmigoto setup\n')
    for index in range(len(strides)):
        ini_text.append(';checktextureoverride = vb' + str(index) + '\n')
    ini_text.append(';checktextureoverride = ib\n')
    ini_text.append(';allow_duplicate_hash=true\n')

    # Write ini file
    if not os.path.exists(vb_name + '.ini'):
        with open(vb_name + '.ini', 'w') as f:
            f.write("".join(ini_text))
