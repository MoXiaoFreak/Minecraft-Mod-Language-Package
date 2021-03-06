#!/usr/bin/python3
# @Author TartaricAcid
# @Title 语言文件分析工具
######################################

print("info Script Loading")

import re
import os
import time

# 存储分析信息
info_list = list()
fre_list = list()

# 开始遍历 assets 文件夹
for root, dirs, files in os.walk("./assets", topdown=False):
    for name in files:
        # 找到符合这个正则匹配的语言文件
        modid = re.findall(r"./assets/(.*)/lang/en_us.lang",
                           os.path.join(root, name))

        # 不符合的会抛出异常，先用try语句包裹
        # 读取文件
        try:
            en_us = open("./assets/" + modid[0] +
                         "/lang/en_us.lang", 'r', encoding='UTF-8')
            zh_cn = open("./assets/" + modid[0] +
                         "/lang/zh_cn.lang", 'r', encoding='UTF-8')
        except:
            print("文件不存在")
            continue

        # 放置中英文映射表
        en_dict = dict()
        zh_dict = dict()

        # 放置英文空key，用以for循环查找
        en_key = list()

        try:
            for entry in en_us.readlines():
                if entry != None and entry[0] != '#' and entry[0] != '/' and '=' in entry:
                    entry_list = entry.split('=', 1)        # 依据等号切分语言文件条目
                    # 空key文件为之后for循环查找提供参考
                    en_key.append(entry_list[0])
                    en_dict[entry_list[0]] = entry_list[1]

            for entry in zh_cn.readlines():
                if entry != None and entry[0] != '#' and entry[0] != '/' and '=' in entry:
                    entry_list = entry.split('=', 1)        # 依据等号切分语言文件条目
                    zh_dict[entry_list[0]] = entry_list[1]
        except:
            print("编码有问题")

        en_us.close()
        zh_cn.close()

        # 分析数据记录初始化
        total = len(en_key)
        english = chinese = 0

        for entry in en_key:
            is_english = False  # 记录是否为英文文本

            try:        # 如果给定的英文key在中文映射表中不存在，抛出异常
                en_dict[entry] = zh_dict[entry]
                chinese = chinese + 1
            except:
                for charset in en_dict[entry]:
                    # 在 0041 到 005a, 0061 到 007a 之间为 26 个基本英文字母
                    if (u'\u0041' <= charset <= u'\u005a') or (u'\u0061' <= charset <= u'\u007a'):
                        is_english = True

                if is_english:
                    english = english + 1

        # 将分析得到的数据全部处理，放入 list 中
        info_list.append(modid[0] + "/" + str(total) +
                         "/" + str(english) + "/" + str(chinese))
        fre_list.append(str(english) + "/" + modid[0])

# 这个函数是给之后排序用的
# 功能是拆分字符串，将英文词条数变成int类型


def trans_int(str):
    a = str.split("/", 1)
    b = int(a[0])
    return b


# 然后调用这个函数来处理字符串
# 而后排序，注意是降序排序
fre_list.sort(key=trans_int, reverse=True)

# 排序，这样就能够得到按照字母排序的模组信息列表了
info_list.sort()

# 创建 process.md 文件
process = open("process.md", 'w', encoding='UTF-8')

# 写入头文件
process.writelines("# 词条更新分频统计列表\n更新时间：" +
                   time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n\n")

# 感觉分频统计就挺好，暂时禁用这个全统计
# process.writelines("| 序号 | modid | 总条目 | 未翻译条目 | 已翻译条目 | 翻译比重 | \n")
# process.write("| :--: | :--: | :--: | :--: | :--: | :--: | \n")

# width, num 分别记录进度和序号
width, num = 0, 1
# 这三个用以统计全局数据
total_all, total_en, total_zh = 0, 0, 0

for entry in info_list:
    # 开始拆分字符串，读取出数据
    entry_list = entry.split("/", 3)

    # 先统计全局数据
    total_all = total_all + int(entry_list[1])
    total_en = total_en + int(entry_list[2])
    total_zh = total_zh + int(entry_list[3])

    # 极个别模组处理后不存在语言文件，分母为0，强制限定其为100%
    if int(entry_list[1]) == 0:
        width = 100
    else:
        width = (int(entry_list[1]) - int(entry_list[2])
                 ) / int(entry_list[1]) * 100
    width = round(width, 2)

    # process.write(" | " + str(num) + " | " + entry_list[0] + " | " + entry_list[1] +
    #              " | " + entry_list[2] + " | " + entry_list[3] + " | " + str(width) + "% | \n")

    # 别忘了，序号加一
    num = num + 1

# 最后，行尾加上全局统计数据
process.write("总计词条数：" + str(total_all) + "    \n")
process.write("英文条数：" + str(total_en) + "    \n")
process.write("中文条数：" + str(total_zh) + "    \n")

if total_all == 0:
    percentage = 100
else:
    percentage = round(((total_all - total_en) / total_all * 100), 2)

process.write(
    "完成率：" + str(percentage) + "%    \n")

# 对未翻译数按照数量，进行统计
# num用了记录个数
num1 = num2 = num3 = num4 = 1
# entry用来记录行数
entry1 = entry2 = entry3 = entry4 = 0

for entry in fre_list:
    # 开始拆分字符串，读取出数据
    entry_list = entry.split("/", 1)

    # 大于等于500的，单独一个表格
    # 用num1来判定是否写表格头文件
    # 如果写完一次头文件后，num1存储数值已经不是1了，就无法再次写入头文件
    # 从而避免头文件重复
    if num1 == 1:
        process.write("\n## 未翻译条目大于等于500行 \n")
        process.write("| 序号 | modid | 未翻译条目 | \n")
        process.write("| :--: | :--: | :--: | \n")
    if int(entry_list[0]) >= 500:
        process.write(" | " + str(num1) + " | " +
                      entry_list[1] + " | " + entry_list[0] + " | \n")
        num1 = num1 + 1
        entry1 = entry1 + int(entry_list[0])
        continue

    # 大于等于100的，单独一个表格
    if num2 == 1:
        process.write("\n## 未翻译条目大于等于100行 \n")
        process.write("| 序号 | modid | 未翻译条目 | \n")
        process.write("| :--: | :--: | :--: | \n")
    if 100 <= int(entry_list[0]) < 500:
        process.write(" | " + str(num2) + " | " +
                      entry_list[1] + " | " + entry_list[0] + " | \n")
        num2 = num2 + 1
        entry2 = entry2 + int(entry_list[0])
        continue

    # 大于等于10的，单独一个表格
    if num3 == 1:
        process.write("\n## 未翻译条目大于等于10行 \n")
        process.write("| 序号 | modid | 未翻译条目 | \n")
        process.write("| :--: | :--: | :--: | \n")
    if 10 <= int(entry_list[0]) < 100:
        process.write(" | " + str(num3) + " | " +
                      entry_list[1] + " | " + entry_list[0] + " | \n")
        num3 = num3 + 1
        entry3 = entry3 + int(entry_list[0])
        continue

    # 小于10个的单独一个表格
    if num4 == 1:
        process.write("\n## 未翻译条目小于10行 \n")
        process.write("| 序号 | modid | 未翻译条目 | \n")
        process.write("| :--: | :--: | :--: | \n")
    if 0 < int(entry_list[0]) < 10:
        process.write(" | " + str(num4) + " | " +
                      entry_list[1] + " | " + entry_list[0] + " | \n")
        num4 = num4 + 1
        entry4 = entry4 + int(entry_list[0])
        continue

# 最后，行尾加上分频统计数据
if total_en != 0:
    process.write("### 未翻译条目大于等于 500 行的模组有 " + str(num1) +
                  " 个，占到了未翻译行数的 " + str(round(entry1 / total_en * 100, 2)) + " % 。\n")
    process.write("### 未翻译条目大于等于 100 行的模组有 " + str(num2) +
                  " 个，占到了未翻译行数的 " + str(round(entry2 / total_en * 100, 2)) + " % 。\n")
    process.write("### 未翻译条目大于等于 10 行的模组有 " + str(num3) +
                  " 个，占到了未翻译行数的 " + str(round(entry3 / total_en * 100, 2)) + " % 。\n")
    process.write("### 未翻译条目大于等于 1 行的模组有 " + str(num4) +
                  " 个，占到了未翻译行数的 " + str(round(entry4 / total_en * 100, 2)) + " % 。\n")

process.close()
