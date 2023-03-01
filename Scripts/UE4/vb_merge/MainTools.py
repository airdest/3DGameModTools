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
from UE4Functions import *


if __name__ == "__main__":
    # Set work dir, here is your FrameAnalysis dump dir.
    FrameAnalyseFolder = "FrameAnalysis-2023-02-12-212207"
    os.chdir("C:/Program Files (x86)/Steam/steamapps/common/BrightMemoryInfinite/BrightMemoryInfinite/Binaries/Win64/" + FrameAnalyseFolder + "/")
    if not os.path.exists('output'):
        os.mkdir('output')

    # Here is the ib you want to import into blender.
    ib_hashs = {"805c4688":"body"}
    for input_ib_hash in ib_hashs:
        # print_all_first_index(input_ib_hash)

        # 获取ib相关的trianglelist列表
        pointlist_indices, trianglelist_indices = get_pointlit_and_trianglelist_indices(input_ib_hash,use_root_vs=False)

        # 对于每个trianglelist_indices，都将它的vb0,vb1,vb2组装起来

        # First ,move these trianglelist indices ib file to the output folder.
        move_ibfiles_by_indices(trianglelist_indices)

        # Then get the vb file's name,and put info into vb0
        for index in trianglelist_indices:
            vb_filenames = sorted(glob.glob(index + '-vb*txt'))

        # 设置各个vb中要读取的element的名称
        # 这里以光明记忆无限为例子
        element_name_dict = {"vb0":["ATTRIBUTE"], "vb1":["ATTRIBUTE1", "ATTRIBUTE2"]}

        # 转化ATTRIBUTE的真实名称，属性，长度
        # TODO 搞清楚各个数据类型可能的名称和长度
        element_convert = {"ATTRIBUTE": ["POSITION", "R32G32B32_FLOAT", 12],
                             "ATTRIBUTE1": ["BLENDWEIGHTS"],
                             "ATTRIBUTE2": ["BLENDINDICES"],
                             }

    print("----------------------------------------------------------\r\nAll process done！")



