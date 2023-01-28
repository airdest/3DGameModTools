from Methods import *


if __name__ == "__main__":
    # 殷紫萍衣服
    # Naraka_INPUT_VB = "9f655a36"

    # 殷紫萍身体
    Naraka_INPUT_VB = "76c673f1"

    main()
    move_dds_file()
    move_cb_file()

    # 默认不移动buf文件，因为对不上
    # move_buf_file()

    print("全部转换完成！")
    os.system("pause")


