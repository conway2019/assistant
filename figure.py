# -*- coding: utf-8 -*-
import pandas as pd
import json

# 输入：json文件名称，excel文件名称
# 将json转换成excel
#从position（职位信息）中提取出personId（人物ID）、personType（职位信息）、title（职位描述）、region（职位所在地）中的第一项（例如：阿联酋）
#提取出userName（中文名）、englishName（英文名）、deadFlag（删除标志）
def json_to_excel(json_file_name, excel_filename):
    # 将JSON文件转换为Python对象
    with open(json_file_name, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # 初始化一个空列表来存储提取的数据
    extracted_data = []

    # 遍历JSON数据中的每个条目
    for item in json_data:
        position_info = item['position'][0]
        person_id = position_info.get('personId')
        person_type = position_info.get('personType')
        title = position_info.get('title')
        
        #提取地区名称，如果region不为空，则提取第一项
        region = ''
        if position_info.get('region'):  # 如果region不为空
            region = position_info['region'].split('/')[0]  # 提取第一项
        
        
        # 提取userName、englishName、deadFlag
        user_name = item['userName']
        english_name = item['englishName']
        dead_flag = item['deadFlag']
        
        # 将提取的数据添加到列表中
        extracted_data.append({
            'personId': person_id,
            'personType': person_type,
            'title': title,
            'region': region,
            'userName': user_name,
            'englishName': english_name,
            'deadFlag': dead_flag
        })
    
    # 将提取的数据转换为DataFrame，设置标题
    df = pd.DataFrame(extracted_data)
    df.columns = ['人物ID', '职位信息', '职位描述', '职位所在地', '中文名', '英文名', '删除标志']

    # 将DataFrame保存为Excel文件
    df.to_excel(excel_filename, index=False)

#从excel日志文件中，提取第一行
#例如：151177	2752	蔡丽新	cailixin	\N	0	更新人物职位	{"birthday":"1971-10"
#提取出人物ID、中文名、英文名、操作，用\t分割
def log_to_excel(log_file_name, excel_filename):
    # 初始化一个空列表来存储提取的数据
    extracted_data = []

    # 读取excel文件，并转换成pandas，遍历第一列
    df = pd.read_excel(log_file_name, header=None)
    lines = df.iloc[:, 0]
    for line in lines:
        # 提取人物ID、中文名、英文名、操作，用\t分割
        data = line.split('\t')
        if len(data) >= 7:
            person_id = data[1]
            user_name = data[2]
            english_name = data[3]
            operation = data[6]
    
            # 将提取的数据添加到列表中
            extracted_data.append({
            'person_id,': person_id,
            'user_name': user_name,
            '英english_name': english_name,
            'operation': operation
            })  
            
    # 将提取的数据转换为DataFrame，设置标题
    df = pd.DataFrame(extracted_data)
    df.columns = ['人物ID', '中文名', '英文名', '操作']
    # 将DataFrame保存为Excel文件
    df.to_excel(excel_filename, index=False)

#输入两个excel文件
# 文件1的字段包括：人物ID	职位信息	职位描述	职位所在地	中文名	英文名	删除标志
# 文件2的字段包括：人物ID
# 生成一个新的文件，用文件2中的人物ID过滤文件1
def filter_excel(file1, file2, output_file):
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)
    df1 = df1[df1['人物ID'].isin(df2['人物ID'])]
    df1.to_excel(output_file, index=False)

#输入：词表、原文件，输出：目标文件
#源文件是excel中的第3列，如果某个值包含词表中的某个词，则忽略这个数值，把剩下的内容输出到目标excel文件中
def filter_excel_by_word(word_file, source_file, target_file):
    #读取词表，excel文件第一列
    df = pd.read_excel(word_file)
    df = df.iloc[:, 0]
    words = df.values
    words = [word.strip() for word in words]
    
    #读取源文件第3列，去掉重复数据
    df = pd.read_excel(source_file) 
    lines = df.iloc[:, 2]
    lines = list(set(lines))
    
    #输出到目标excel文件第一列，标题为职务描述
    #循环读取数据，如果不包含词表中的词，则拷贝到目标数据中
    new_lines = []
    for line in lines:
        #如果不是字符串，则忽略
        if not isinstance(line, str):
            continue
        if not any(word in line for word in words):
            new_lines.append(line)
                        
    df = pd.DataFrame(new_lines)
    df.columns = ['职务描述']
    df.to_excel(target_file, index=False)                     
               
                        
if __name__ == '__main__':
    json_file_name = 'D:/kw/数据业务部/数据业务/采编助手/人像库/figure.json'
    excel_filename = 'D:/kw/数据业务部/数据业务/采编助手/人像库/figure.xlsx'
    log_filename = 'D:/kw/数据业务部/数据业务/采编助手/人像库/log.xlsx'
    operation_filename = 'D:/kw/数据业务部/数据业务/采编助手/人像库/operation.xlsx'
    
    #json_to_excel(json_file_name, excel_filename)
    #log_to_excel(log_filename, operation_filename)
    
    source_filename = 'D:/kw/数据业务部/数据业务/采编助手/人像库/人像库.xlsx'
    filter_filename = 'D:/kw/数据业务部/数据业务/采编助手/人像库/人物操作.xlsx'
    filter_filename2 = 'D:/kw/数据业务部/数据业务/采编助手/人像库/人物操作2.xlsx'
    #filter_excel(source_filename, filter_filename, filter_filename2)
    
    source_filename = 'D:/kw/数据业务部/数据业务/采编助手/人像库/人像库.xlsx'
    word_filename = 'D:/kw/数据业务部/数据业务/采编助手/人像库/职务.xlsx'
    target_filename = 'D:/kw/数据业务部/数据业务/采编助手/人像库/剩余职务.xlsx'
    filter_excel_by_word(word_filename, source_filename, target_filename)

    print('Done!')
