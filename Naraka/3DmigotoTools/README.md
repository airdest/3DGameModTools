
# 开发记录：
## 开发日志：V3000
dump人物模型时，尽量在大厅=>英雄=>外观=>时装界面dump，这样dump出的模型比较少
目前可以完美导入大厅界面人物模型，但是无法导入骨骼，重点研究骨骼的导入

新增特性：

1.优化了脚本运行速度，目前运行超快

## 开发日志：V3001
新增特性：

1.遇到pointlist自动跳过且不复制到output目录，因为目前blender导入vb ib 的txt文件不支持pointlist类型

2.自动导入dds文件到output目录

3.自动导入vs-cb2文件到output目录

4.解决TANGENT报错的BUG


## TODO列表
人物骨骼如何导入 vs-cb2 Shader不行的话，绑定IB试一试

3dmigoto导出的都是什么？如何修改？如何填补空缺部分？填补后如何替换到游戏内从而实现人物模型补充？是不是需要学习blender？

解决缺少first vertex 和 vertex count时脚本报错的问题（暂时不用）
