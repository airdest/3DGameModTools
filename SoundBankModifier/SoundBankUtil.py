import os
import random
import shutil
import subprocess
import warnings

class BNKFileInfo:
    BKHD_Section = None
    DIDX_Section = None
    DATA_Section = None
    REST_Section = None  # 除了BKHD，DIDX，DATA部分外，剩余的字节
    pass


class BKHDSection:
    bkhd_bytes = None  # BKHD部分所有字节

    bkhd_name = None
    bkhd_length = None
    bkhd_version = None
    bkhd_soundBankId = None
    bkhd_alwaysZero1 = None
    bkhd_alwaysZero2 = None
    '''
    The BKHD section (Bank Header) contains the version number and the SoundBank id.
    ● bkhd_name             42 4B 48 44 -- BKHD
    ● bkhd_length           uint32: length of section
    ● bkhd_version          uint32: version number of this SoundBank
    ● bkhd_soundBankId      uint32: id of this SoundBank
    ● bkhd_alwaysZero1      uint32: always zero
    ● bkhd_alwaysZero2      uint32: always zero
    '''


class DIDXSection:
    didx_bytes = None  # DIDX部分所有字节，注意如果发生了wem文件替换需要重新赋值

    didx_name = None
    didx_length = None
    WEMInfos = None

    '''
    The DIDX (Data Index) section contains the references to the .wem files embedded in the SoundBank. 
    Each sound file is described with 12 bytes, 
    so you can get the number of embedded files by dividing the section length by 12.
    ● didx_name         44 49 44 58 -- DIDX
    ● didx_length       uint32: length of section
    ● FOR EACH (embedded .wem file) {
      ○ uint32: .wem file id
      ○ uint32: offset from start of DATA section
      ○ uint32: length in bytes of .wem file
    ● } END FOR
    '''


class WEMInfo:
    wem_bytes = None
    id = None
    offset = None
    length = None


class DATASection:
    data_bytes = None
    data_name = None
    data_length = None
    '''
    The DATA section contains the .wem files, not encoded, and immediately following each other. 
    (踩坑提示：这里注意不是一个wem的bytes立刻跟着另一个wem的bytes，中间是有空隙的，空隙都是b'\x00'组成的！)
    It is not recommended to read this section by itself but instead to immediately jump to 
    the correct position based on the offset given in the DIDX or HIRC section.
    ● data_name         44 41 54 41 -- DATA
    ● data_length       uint32: length of section
    ● FOR EACH (embedded .wem file) {
        ○ byte[]: the .wem file with the length as given in the DIDX section, and starting with 52 49 46 46 -- RIFF.
    ● } END FOR
    '''


class RESTSection:
    rest_bytes = None

    '''
    ENVS section (The ENVS section (Environments?) section is yet to be analysed.)
    FXPR section (The FXPR section (Effects production?) section is yet to be analysed.)
    HIRC section 
    '''


def get_bnk_info(input_bnk_path):
    # 类定义好之后，开始读取所有信息到BNKFileInfo类
    input_file = open(input_bnk_path, "rb")
    input_bnk_size = os.path.getsize(input_bnk_path)

    bnkFileInfo = BNKFileInfo()
    BKHD = BKHDSection()
    DIDX = DIDXSection()
    DATA = DATASection()
    REST = RESTSection()

    # 1.读取BKHD部分
    bkhd_StartPosition = 0
    BKHD.bkhd_name = input_file.read(4)
    BKHD.bkhd_length = int.from_bytes(input_file.read(4), "little")
    # 读取BKHD bytes，读取后进入DIDX部分
    input_file.seek(bkhd_StartPosition)
    BKHD.bkhd_bytes = input_file.read(BKHD.bkhd_length + 4 + 4)

    # 2.读取DIDX部分
    didx_StartPosition = input_file.tell()
    DIDX.didx_name = input_file.read(4)
    DIDX.didx_length = int.from_bytes(input_file.read(4), "little")
    # 读取DIDX bytes，读取后进入DATA部分
    input_file.seek(didx_StartPosition)
    DIDX.didx_bytes = input_file.read(DIDX.didx_length + 4 + 4)

    # 3.读取DATA部分
    data_StartPosition = input_file.tell()
    DATA.data_name = input_file.read(4)
    DATA.data_length = int.from_bytes(input_file.read(4), "little")
    # 读取DATA bytes，读取后进入REST部分
    input_file.seek(data_StartPosition)
    DATA.data_bytes = input_file.read(DATA.data_length + 4 + 4)

    # 4.读取REST部分
    rest_length = input_bnk_size - input_file.tell()
    REST.rest_bytes = input_file.read(rest_length)

    # 5.读取WEMInfo列表
    didx_TruePosition = didx_StartPosition + 4 + 4
    data_TruePosition = data_StartPosition + 4 + 4

    # (1)跳转到DIDX存储WEM信息的部分
    input_file.seek(didx_TruePosition)

    # (2)循环遍历WEM部分
    wemInfoList = []
    for i in range(0, int(DIDX.didx_length // 12)):
        wemInfo = WEMInfo()

        # 跳转到对应的实际起始位置
        input_file.seek(didx_TruePosition + (i * 12))
        print("------------------------------------------")

        # 读取wem_id
        wemInfo.id = int.from_bytes(input_file.read(4), "little")
        print("wem_id:" + str(wemInfo.id))

        # 读取wem_offset 这里的wem_offset指的是相对于DATA部分的偏移量
        wemInfo.offset = int.from_bytes(input_file.read(4), "little")
        print("wem_offset:" + str(wemInfo.offset))

        # 读取wem_length
        wemInfo.length = int.from_bytes(input_file.read(4), "little")
        print("wem_bytes_length:" + str(wemInfo.length))

        # 首先跳转到DATA部分(DATA实际起始部分 + wem偏移量)
        input_file.seek(data_TruePosition + wemInfo.offset)

        # 读取wem数据
        wemInfo.wem_bytes = input_file.read(wemInfo.length)

        # 加入列表
        wemInfoList.append(wemInfo)

    # 设置WEMInfos列表
    DIDX.WEMInfos = wemInfoList

    # 6.读取完成后关闭文件
    input_file.close()

    # 全部拿到后放到类里
    bnkFileInfo.BKHD_Section = BKHD
    bnkFileInfo.DIDX_Section = DIDX
    bnkFileInfo.DATA_Section = DATA
    bnkFileInfo.REST_Section = REST

    return bnkFileInfo


def replace_wem(bnkFileInfo, wemPath, replaceNum):
    print("------------------------------------")
    print("开始替换指定wem文件")
    # 获取替换的wem信息
    replace_filesize = os.path.getsize(wemPath)
    replace_file = open(wemPath, "rb")
    replace_file_bytes = replace_file.read(replace_filesize)
    replace_file.close()

    # 4.逐步替换，替换第replaceNum个wem文件
    # 替换DIDX的bytes,length,WEMInfos部分
    DIDX = bnkFileInfo.DIDX_Section
    DATA = bnkFileInfo.DATA_Section

    # 获取wemInfos
    wemInfos = DIDX.WEMInfos

    # 替换第replaceNum个wemInfo
    newWemInfo = WEMInfo()
    newWemInfo.id = wemInfos[replaceNum - 1].id
    newWemInfo.offset = wemInfos[replaceNum - 1].offset
    newWemInfo.wem_bytes = replace_file_bytes
    # 获取oldLength  旧的wemInfo的length
    oldLength = wemInfos[replaceNum - 1].length
    # 替换后的wemInfo的length
    newWemInfo.length = replace_filesize

    # 计算length偏移量差值，后面小于等于replaceNum的都不用修改偏移量差值，大于的offset都要加上便宜量差值
    diff = newWemInfo.length - oldLength

    # 替换
    wemInfos[replaceNum - 1] = newWemInfo

    # 重新修改wemInfos中各个wemInfo的offset
    newWemInfos = []
    # 重新编写wemInfo的bytes
    newWemInfoBytes = bytes()

    wemNum = 1
    for wemInfo in wemInfos:
        '''
          ○ uint32: .wem file id
          ○ uint32: offset from start of DATA section
          ○ uint32: length in bytes of .wem file
        '''
        # 小于等于replaceNum的都不用修改偏移量差值，大于的offset都要加上便宜量差值
        if wemNum > replaceNum:
            wemInfo.offset = wemInfo.offset + diff

        newWemInfoBytes = newWemInfoBytes + int.to_bytes(wemInfo.id, 4, "little")
        newWemInfoBytes = newWemInfoBytes + int.to_bytes(wemInfo.offset, 4, "little")
        newWemInfoBytes = newWemInfoBytes + int.to_bytes(wemInfo.length, 4, "little")

        newWemInfos.append(wemInfo)
        wemNum = wemNum + 1

    # 更新修改后的各个wemInfo
    DIDX.WEMInfos = newWemInfos
    # 更新DIDX length
    DIDX.didx_length = DIDX.didx_length
    # 更新didx bytes
    DIDX.didx_bytes = DIDX.didx_name + int.to_bytes(DIDX.didx_length, 4, "little") + newWemInfoBytes

    # (3)更新DATA的bytes和length部分
    # 更新DATA的length部分  整体长度肯定要加上偏移量
    print("开始更新DATA部分")

    print("")

    print("原始DATA的长度：")
    print(DATA.data_length)
    print("差值：")
    print(diff)
    print("原始长度加上差值后的值：")
    DATA.data_length = DATA.data_length + diff
    print(DATA.data_length)

    print("oldsize = ")
    print(DATA.data_bytes.__sizeof__())

    print("DATA.name:")
    print(DATA.data_name)

    newDataBytes = DATA.data_name + int.to_bytes(DATA.data_length, 4, "little")

    last_offset = 0
    last_length = 0
    for wemInfo in DIDX.WEMInfos:
        # 计算空隙长度
        null_length = wemInfo.offset - last_offset -last_length
        # 填充空隙部分
        i = 1
        while i <= null_length:
            newDataBytes = newDataBytes + b'\x00'
            i = i +  1
        # 填充wembytes
        newDataBytes = newDataBytes + wemInfo.wem_bytes
        last_offset = wemInfo.offset
        last_length = wemInfo.length

    DATA.data_bytes = newDataBytes
    print("newsize = ")
    print(DATA.data_bytes.__sizeof__())

    # (4)更新BNKInfo
    bnkFileInfo.DIDX_Section = DIDX
    bnkFileInfo.DATA_Section = DATA
    return bnkFileInfo


def save_bnk(newBNKFileInfo,outputPath):
    print("---------------------------------")
    print("开始保存bnk文件")
    BKHD = newBNKFileInfo.BKHD_Section
    DIDX = newBNKFileInfo.DIDX_Section
    DATA = newBNKFileInfo.DATA_Section
    REST = newBNKFileInfo.REST_Section
    newBNKBytes = BKHD.bkhd_bytes + DIDX.didx_bytes + DATA.data_bytes + REST.rest_bytes

    # 写出
    output_bnk_file = open(outputPath, "wb")
    output_bnk_file.write(newBNKBytes)
    output_bnk_file.flush()
    output_bnk_file.close()
    print("保存bnk文件完成")
    print("---------------------------------")


def save_all_wem(wemInfos, wem_output_folder, is_generate_wav=False, wav_output_folder="",testexe_path=""):

    # 遍历WEMInfos列表并写出wem文件
    for wemInfo in wemInfos:
        wem_path = wem_output_folder + str(wemInfo.id) + ".wem"
        output_wem_file = open(wem_path, "wb")
        output_wem_file.write(wemInfo.wem_bytes)
        output_wem_file.flush()
        output_wem_file.close()

        if is_generate_wav:
            wav_path = wav_output_folder + str(wemInfo.id) + ".wav"
            convert_wem_to_wav(testexe_path, wem_path, wav_path)


def refresh_cache(bnk_info, testexe_file, wav_cache_path, wem_cache_path,tmp_cache_path):
    # 删除临时文件夹下面的所有文件(只删除文件,不删除文件夹)
    del_file(wav_cache_path)
    del_file(wem_cache_path)
    del_file(tmp_cache_path)

    # 读取后写到wemCache目录作为临时文件,并写到wavCache目录作为wav临时文件
    DIDX = bnk_info.DIDX_Section
    save_all_wem(DIDX.WEMInfos, wem_cache_path + "\\", is_generate_wav=True, wav_output_folder=wav_cache_path + "\\",
                 testexe_path=testexe_file)


def convert_wem_to_wav(testexe_path, input_wem_file, output_wav_file):
    # wem文件转为wav文件
    shell_text = testexe_path + ' -o ' + output_wav_file + ' ' + input_wem_file
    decode_process = subprocess.Popen(shell_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                      encoding='gb2312')
    print(decode_process.communicate()[0])

def convert_wav_to_wem(testexe_path, input_wav_file, output_wem_file):
    # wav文件转为wem文件
    shell_text = testexe_path + ' -o ' + output_wem_file + ' ' + input_wav_file
    decode_process = subprocess.Popen(shell_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                      encoding='gb2312')
    print(decode_process.communicate()[0])

def del_file(path_data):
    for i in os.listdir(path_data):  # os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
        file_data = path_data + "\\" + i  # 当前文件夹的下面的所有东西的绝对路径
        if os.path.isfile(file_data):  # os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
            os.remove(file_data)
        else:
            del_file(file_data)


def copyfiles(source_folder, target_folder):
    # 把一个文件夹下所有文件复制到另一个文件夹
    for file_name in os.listdir(source_folder):  # os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
        source_file = source_folder + "\\" + file_name  # 当前文件夹的下面的所有东西的绝对路径
        target_file = target_folder + "\\" + file_name
        shutil.copy(source_file, target_file)


