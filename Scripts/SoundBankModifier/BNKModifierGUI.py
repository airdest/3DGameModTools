from SoundBankUtil import *
import PySimpleGUI as sg
import os


def make_window():
    # 设置贴边
    sg.set_options(element_padding=(0, 0))

    # 顶部导航菜单
    menu_def = [['File', ['Open', 'Save As...']], ['Export All', ['Export .wem Format To...', 'Export .wav Format To...']]]
    # wem文件列表的右键菜单
    right_click_menu_def = ['', ['Play', 'Replace With .wem File', 'Replace With .wav File', 'Export to .wem File', 'Export to .wav File']]
    # wem文件列表
    table_def = [[]]

    # 创建layout
    layout = [
        [sg.Menu(menu_def, key='menu')],
        [sg.Table(table_def
                  , headings=["Id", "Offset", "Length (Bytes)", "Replacing with"]
                  , key="_table_"
                  , expand_x=True
                  , expand_y=True
                  , right_click_selects=True
                  , right_click_menu=right_click_menu_def)]
    ]

    # 创建窗口，黄金比例
    window = sg.Window("SoundBankModifier",
                       layout,
                       size=(600, 371))

    return window


def main():
    bnk_info = None  # bnk文件信息
    relative_path = os.path.dirname(__file__)  # 项目运行路径
    cache_path = relative_path + "\\.cache"  # .cache路径
    wav_cache_path = cache_path + "\\wavCache"  # wavCache路径
    wem_cache_path = cache_path + "\\wemCache"  # wemCache路径
    tmp_cache_path = cache_path + "\\tmpCache"  # tmpCache路径
    # 判断如果缓存路径不存在，则创建缓存路径
    if not os.path.exists(cache_path):
        os.mkdir(cache_path)
        print("不存在临时缓存目录，进行创建")
    if not os.path.exists(wav_cache_path):
        os.mkdir(wav_cache_path)
        print("不存在wav临时缓存目录，进行创建")
    if not os.path.exists(wem_cache_path):
        os.mkdir(wem_cache_path)
        print("不存在wem临时缓存目录，进行创建")
    if not os.path.exists(tmp_cache_path):
        os.mkdir(tmp_cache_path)
        print("不存在tmp临时缓存目录，进行创建")

    testexe_file = relative_path + '\\vgmstream-win\\test.exe'  # vgmstream中的test.exe路径

    # 创建GUI界面
    window = make_window()

    # 事件处理
    while True:
        event, value = window.read()
        if event == sg.WIN_CLOSED:
            break

        elif event == 'Open':
            # 获取bnk文件路径
            input_bnk_path = sg.popup_get_file('SoundBank file to open', no_window=True, file_types=(("Wwise SoundBank File", "*.bnk .bnk"), ))

            # 判断是否没打开任何文件
            if input_bnk_path.endswith(".bnk"):
                print("打开文件路径：" + input_bnk_path)
                bnk_name = input_bnk_path.split("/")[-1]
                # 更新标题
                sg.Window.set_title(window, "SoundBankModifier    Moding: " + bnk_name)

                # 读取BNK文件信息
                bnk_info = get_bnk_info(input_bnk_path)

                # 刷新本地缓存
                refresh_cache(bnk_info, testexe_file, wav_cache_path, wem_cache_path,tmp_cache_path)

                # 动态添加table列
                DIDX = bnk_info.DIDX_Section
                wem_infos = DIDX.WEMInfos
                wem_table = []
                i = 0
                for wem_info in wem_infos:
                    wem_table.append([])
                    wem_table[i].append([str(wem_info.id)])
                    wem_table[i].append([str(wem_info.offset)])
                    wem_table[i].append([str(wem_info.length)])
                    wem_table[i].append([])

                    i = i+1

                window["_table_"].update(wem_table)
                window.refresh()
            else:
                print("未打开任何bnk文件")

        elif event == 'Save As...':
            output_bnk_path = sg.popup_get_file('SoundBank file to save', no_window=True,save_as=True,
                                               file_types=(("Wwise SoundBank File", "*.bnk .bnk"),))
            print(output_bnk_path)
            if output_bnk_path != "":
                if bnk_info is None:
                    sg.popup_error("请先打开一个bnk文件")
                else:
                    save_bnk(bnk_info, output_bnk_path)
                    sg.popup("导出成功！")
            else:
                print("空路径无法保存")

        elif event == 'Export .wem Format To...':
            output_wav_folder = sg.popup_get_folder("Which folder to save wem files", no_window=True)

            if output_wav_folder != "":
                if bnk_info is None:
                    if output_wav_folder != "":
                        sg.popup_error("请先打开一个bnk文件")
                else:
                    output_wav_folderPath = output_wav_folder + "/"
                    DIDX = bnk_info.DIDX_Section
                    save_all_wem(DIDX.WEMInfos, output_wav_folderPath)
                    sg.popup("导出成功！")
            else:
                print("未选择要导出到的文件夹")

        elif event == 'Export .wav Format To...':
            output_wav_folder = sg.popup_get_folder("Which folder to save wav files", no_window=True)

            if output_wav_folder != "":
                if bnk_info is None:
                    sg.popup_error("请先打开一个bnk文件")
                else:
                    # 刷新本地缓存
                    refresh_cache(bnk_info, testexe_file, wav_cache_path, wem_cache_path,tmp_cache_path)
                    # 将缓存中的wav复制到目标目录
                    copyfiles(wav_cache_path, output_wav_folder)
                    sg.popup("导出成功！")
            else:
                print("未选择要导出到的文件夹")

        elif event == 'Play':
            if bnk_info is None:
                sg.popup_error("请先打开一个bnk文件")
            else:
                row, col = window["_table_"].get_last_clicked_position()
                table_info = window["_table_"].get()
                print(table_info[row][0][0])
                subprocess.call(
                    "C:\Program Files\Windows Media Player\wmplayer.exe " + wav_cache_path + "\\" + table_info[row][0][
                        0] + ".wav")

        elif event == 'Replace With .wem File':
            replace_wem_path = sg.popup_get_file('wem file to replace', no_window=True,
                                               file_types=(("Wwise wem File", "*.wem .wem"),))

            if replace_wem_path != "":
                if bnk_info is None:
                    sg.popup_error("请先打开一个bnk文件")
                else:
                    replace_wem_name = replace_wem_path.split("/")[-1]
                    print(replace_wem_name)

                    row, col = window["_table_"].get_last_clicked_position()
                    table_info = window["_table_"].get()
                    print("获取到table_info: ")
                    print(table_info)
                    # 用指定的wem进行替换
                    bnk_info = replace_wem(bnk_info, replace_wem_path, int(row)+1)
                    # 替换后先刷新本地缓存
                    refresh_cache(bnk_info, testexe_file, wav_cache_path, wem_cache_path, tmp_cache_path)

                    # 更新列表状态
                    # 更新用哪个进行的替换
                    table_info[row][3] = [replace_wem_name]
                    # 更新offset 和length
                    DIDX = bnk_info.DIDX_Section
                    i = 0
                    for wem_info in DIDX.WEMInfos:
                        table_info[i][1] = wem_info.offset
                        table_info[i][2] = wem_info.length
                        i = i + 1
                    window["_table_"].update(table_info)
                    window.refresh()
                    sg.popup("替换成功")

        elif event == 'Replace With .wav File':
            replace_wav_path = sg.popup_get_file('wav file to replace', no_window=True,
                                                 file_types=(("wav File", "*.wav .wav"),))

            if replace_wav_path != "":
                if bnk_info is None:
                    sg.popup_error("请先打开一个bnk文件")
                else:
                    # 调用vgmstream，把wav文件转为wem文件
                    wav_name = replace_wav_path.split("/")[-1].split(".wav")[0]
                    tmp_wem_path = tmp_cache_path + '\\'+wav_name
                    convert_wav_to_wem(testexe_file, replace_wav_path, tmp_wem_path)

                    row, col = window["_table_"].get_last_clicked_position()
                    table_info = window["_table_"].get()
                    print("获取到table_info: ")
                    print(table_info)
                    # 用指定的wem进行替换
                    bnk_info = replace_wem(bnk_info, tmp_wem_path, int(row) + 1)
                    # 替换后先刷新本地缓存
                    refresh_cache(bnk_info, testexe_file, wav_cache_path, wem_cache_path,tmp_cache_path)

                    # 更新列表状态
                    # 更新用哪个进行的替换
                    table_info[row][3] = [wav_name+".wav"]
                    # 更新offset 和length
                    DIDX = bnk_info.DIDX_Section
                    i = 0
                    for wem_info in DIDX.WEMInfos:
                        table_info[i][1] = wem_info.offset
                        table_info[i][2] = wem_info.length
                        i = i + 1
                    window["_table_"].update(table_info)
                    window.refresh()
                    sg.popup("替换成功")

        elif event == 'Export to .wem File':
            output_wav_folder = sg.popup_get_folder("Which folder to save wem file", no_window=True)
            if output_wav_folder != "":
                if bnk_info is None:
                    if output_wav_folder != "":
                        sg.popup_error("请先打开一个bnk文件")
                else:
                    output_wav_folderPath = output_wav_folder + "/"
                    row, col = window["_table_"].get_last_clicked_position()
                    table_info = window["_table_"].get()
                    copy_wav_path = wem_cache_path+"\\" + table_info[row][0][0] + ".wem"
                    output_wav_path = output_wav_folderPath + table_info[row][0][0] + ".wem"
                    shutil.copy(copy_wav_path, output_wav_path)
                    sg.popup("导出成功！")
            else:
                print("未选择要导出到的文件夹")


        elif event == 'Export to .wav File':
            output_wav_folder = sg.popup_get_folder("Which folder to save wav file", no_window=True)
            if output_wav_folder != "":
                if bnk_info is None:
                    if output_wav_folder != "":
                        sg.popup_error("请先打开一个bnk文件")
                else:
                    output_wav_folderPath = output_wav_folder + "/"
                    row, col = window["_table_"].get_last_clicked_position()
                    table_info = window["_table_"].get()
                    copy_wav_path = wav_cache_path+"\\" + table_info[row][0][0] + ".wav"
                    output_wav_path = output_wav_folderPath + table_info[row][0][0] + ".wav"
                    shutil.copy(copy_wav_path, output_wav_path)
                    sg.popup("导出成功！")
            else:
                print("未选择要导出到的文件夹")



    # 关闭窗口前，清空.cache目录下所有文件
    # 删除临时文件夹下面的所有文件(只删除文件,不删除文件夹)
    del_file(wav_cache_path)
    del_file(wem_cache_path)
    del_file(tmp_cache_path)
    # 关闭窗口
    window.close()
    # 正常退出
    exit(0)


if __name__ == '__main__':
    # # 测试替换指定wem文件
    # bnkPath = "C:/Users/user/Desktop/dialogue_outgame_tarka.bnk"
    # wemPath = "C:/Users/user/Desktop/45593967.wem"
    # replaceNum = 10
    # Todo 指定codec进行转换（比较难还在摸索） 最后的难点
    # Todo 调用语音识别接口，自动识别每个语音文件的内容
    # Todo 展示wem文件的vorbis信息
    # Todo 读取本地csv表格文件来添加一列语音内容
    # Todo wem文件批量展示器
    # Todo 可以任意标记wem文件，记录到csv文件
    # Todo 优化逻辑提高速度，目前每次刷新缓存都是全量，后面改成只刷新对应的被修改过的那一条的缓存
    #

    main()


