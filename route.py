# -*- coding: utf-8 -*-
import pandas as pd
import os
import json

def extract_location(locations):
    location_list = eval(locations)  # 将字符串转换为列表
    try:
        # 检查列表是否有足够的元素
        if len(location_list) > 2 and isinstance(location_list, list) and location_list[2]:
            return location_list[2]
        else:
            print('无法解析', locations)
            return None  
    except Exception as e:
        print('无法解析', locations)
        return None
    
def expand_dates(row):
    start_date = row['行程开始时间']
    end_date = row['行程结束时间']
    location = row['地点']
    date_range = pd.date_range(start=start_date, end=end_date).tolist()  # 将日期范围转换为列表
    data = [[date, location] for date in date_range]  # 创建包含日期和地点的数据列表
    return pd.DataFrame(data, columns=['日期', '地点'])  # 创建DataFrame

def process_excel(file_name, output_dir):
    # 1. 打开指定名称的excel文件
    try:
        df = pd.read_excel(file_name)
    except Exception as e:
        print(f"无法打开文件：{e}")
        return

    # 2. 提取内容
    # （1）读取文件内容的前三列内容
    df['地点'] = df['地点'].apply(extract_location)  # 提取地点中的第三个数据
    columns = ['行程开始时间', '行程结束时间', '地点']
    df_selected = df[columns]

    # （2）每行处理后的数据
    df_processed = df_selected.copy()
    df_processed['行程开始时间'] = pd.to_datetime(df_processed['行程开始时间'])
    df_processed['行程结束时间'] = pd.to_datetime(df_processed['行程结束时间'])

    # 3. 分拆和合并数据
    # （1）将行程开始时间、行程结束时间形成的时间段，拆分成单个时间
    df_expanded = pd.concat([expand_dates(row) for _, row in df_processed.iterrows()], ignore_index=True)

    # （2）将行相同的数据去重
    df_expanded.drop_duplicates(inplace=True)

    # 4. 按照日期顺序，输出处理后的数据，生成数据文件
    df_expanded.sort_values(by='日期', inplace=True)
 
    # 将'日期'列转换为datetime类型
    df_expanded['日期'] = pd.to_datetime(df_expanded['日期'])

    #生成分组
    df_expanded = create_group(df_expanded)

    #设置日期格式
    df_expanded['日期'] = pd.to_datetime(df_expanded['日期']).dt.strftime('%Y/%m/%d')
   
    #生成新的文件名    
    stat_file_name = os.path.basename(file_name).replace('.xlsx', '_stat.xlsx')
    stat_file_name = os.path.join(output_dir, stat_file_name)
    df_expanded.to_excel(stat_file_name, index=False)

    print(f"处理后的数据已保存到文件：{stat_file_name}")


def create_group(df):
    
    # 将'日期'列转换为datetime类型
    df['日期'] = pd.to_datetime(df['日期'])

    # 初始化组号列，默认为1
    df['组'] = 1

    # 计算相邻行的日期差
    df['日期差'] = df['日期'].diff()

    # 标记组号变化的位置，即日期差超过8天的位置
    df['组变化'] = df['日期差'] > pd.Timedelta(days=8)

    # 使用cumsum()对组变化进行累加，得到新的组号
    df['组'] = df['组变化'].cumsum() + 1
    # 设置“组”列居中显示，这里假设最大宽度为5个字符
    df['组'] = df['组'].apply(lambda x: str(x).center(5))

    # 删除辅助列'日期差'
    df.drop('日期差', axis=1, inplace=True)

    return df[['组', '日期', '地点']].sort_values('日期')

def find_xlsx_files(directory):
    # 这个列表将存储找到的.xlsx文件的完整路径
    xlsx_files = []
    
    # os.walk()遍历目录及子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 检查文件后缀是否为.xlsx
            if file.endswith('.xlsx'):
                # 将文件的完整路径添加到列表中
                xlsx_files.append(os.path.join(root, file))
    
    return xlsx_files

def process_dir_excel(input_dir, output_dir):
    xlsx_file_list = find_xlsx_files(input_dir)
    for file_name in xlsx_file_list:
        process_excel(file_name, output_dir)     

def find_matching_records(file_path,log_file_path):
    print(file_path)

    # 读取Excel文件
    df = pd.read_excel(file_path)
    
    # 去除地点和docId前后的空格
    df['地点'] = df['地点'].str.strip()
    df['docId'] = df['docId'].str.strip()
    
    # 用于存储匹配的记录
    matching_records = []
    
    # 遍历数据帧中的每一行
    for index, row in df.iterrows():
        # 寻找匹配的记录
        for index2, row2 in df.iterrows():
            if index != index2:  # 确保不是与自身比较
                if row['地点'] == row2['地点'] and row['docId'] == row2['docId']:
                    if not (row['行程开始时间'] == row2['行程开始时间'] and row['行程结束时间'] == row2['行程结束时间']):
                        matching_records.append((row, row2))
    
        # 将匹配的记录写入日志文件
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        for record_pair in matching_records:
            log_file.write("记录1:\n")
            log_file.write(record_pair[0].iloc[:4].to_string(index=False))
            log_file.write("\n记录2:\n")
            log_file.write(record_pair[1].iloc[:4].to_string(index=False))
            log_file.write("\n" + "-" * 40 + "\n")

            print("记录1:")
            print(record_pair[0].iloc[:4])
            print("记录2:")
            print(record_pair[1].iloc[:4])
            print("-" * 40)


def check_dir_excel(input_dir, log_file):
    xlsx_file_list = find_xlsx_files(input_dir)
    for file_name in xlsx_file_list:
        find_matching_records(file_name, log_file)

def row_count(input_dir, file_extension, output_file):
    # 初始化一个空的DataFrame来存储结果
    result_df = pd.DataFrame(columns=['地点', '数量'])

    # 遍历目录中的所有文件
    for filename in os.listdir(input_dir):
        if filename.endswith(file_extension):
            # 构造完整的文件路径
            file_path = os.path.join(input_dir, filename)
            
           # 读取文件
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            elif file_extension == '.xlsx':
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file extension. Use '.csv' or '.xlsx'.")
            
            # 统计行数（实际行数-1，排除标题行）
            row_count = df.shape[0]
            
            # 获取地点名称（文件名去掉.csv后缀）
            location = os.path.splitext(filename)[0]
            
            # 将结果添加到DataFrame中
            temp_df = pd.DataFrame({'地点': [location], '数量': [row_count]})
            result_df = pd.concat([result_df, temp_df], ignore_index=True)
            
    # 按照数量从小到大排序
    result_df = result_df.sort_values(by='数量', ascending=True)
    
    # 将结果输出到Excel文件
    result_df.to_excel(output_file, index=False)


def convert_csv_to_xlsx(input_dir, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            # 构造完整的输入文件路径
            input_file_path = os.path.join(input_dir, filename)
            
            # 读取CSV文件
            df = pd.read_csv(input_file_path)
            
            # 构造输出文件名（相同的文件名，不同的后缀）
            output_filename = os.path.splitext(filename)[0] + '.xlsx'
            output_file_path = os.path.join(output_dir, output_filename)
            
            # 将DataFrame写入Excel文件
            df.to_excel(output_file_path, index=False)

    print(f'所有CSV文件已转换为XLSX格式并保存到 {output_dir}')


def process_stat(input_dir, file_extension, output_dir):
    # 检查文件扩展名是否为.xlsx或.json
    if file_extension not in ['.xlsx', '.json', '.csv']:
        raise ValueError("Unsupported file extension. Only .xlsx and .json are supported.")
    
    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_dir):
        if filename.endswith(file_extension):
            file_path = os.path.join(input_dir, filename)
            print('正在处理文件：{}', file_path)
            
            # 1. 读取文件
            # 处理.csv文件
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            # 处理.xlsx文件
            elif file_extension == '.xlsx':
                # 读取Excel文件到Pandas DataFrame
                df = pd.read_excel(file_path)
            # 处理.json文件
            elif file_extension == '.json':
                # 打开并读取JSON文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 提取需要的字段并创建DataFrame
                df = pd.DataFrame([
                    {
                        "行程开始时间": item.get("startTime-label", ""),
                        "行程结束时间": item.get("endTime-label", ""),
                        "地点": item.get("address-label", [])
                    } for item in data
                ])
                
            # 2. 提取内容
            # （1）读取文件内容的前三列内容
            df['地点'] = df['地点'].apply(extract_location)  # 提取地点中的第三个数据
            columns = ['行程开始时间', '行程结束时间', '地点']
            df_selected = df[columns]

            # （2）每行处理后的数据
            df_processed = df_selected.copy()
            df_processed['行程开始时间'] = pd.to_datetime(df_processed['行程开始时间'])
            df_processed['行程结束时间'] = pd.to_datetime(df_processed['行程结束时间'])

            # 3. 分拆和合并数据
            # （1）将行程开始时间、行程结束时间形成的时间段，拆分成单个时间
            df_expanded = pd.concat([expand_dates(row) for _, row in df_processed.iterrows()], ignore_index=True)

            # （2）将行相同的数据去重
            df_expanded.drop_duplicates(inplace=True)

            # 4. 按照日期顺序，输出处理后的数据，生成数据文件
            df_expanded.sort_values(by='日期', inplace=True)
        
            # 将'日期'列转换为datetime类型
            df_expanded['日期'] = pd.to_datetime(df_expanded['日期'])

            #生成分组
            df_expanded = create_group(df_expanded)

            #设置日期格式
            df_expanded['日期'] = pd.to_datetime(df_expanded['日期']).dt.strftime('%Y/%m/%d')
        
            #生成新的文件名    
            stat_file_name = os.path.basename(filename).replace(file_extension, '_stat.xlsx')
            stat_file_name = os.path.join(output_dir, stat_file_name)
            df_expanded.to_excel(stat_file_name, index=False)

            print(f"处理后的数据已保存到文件：{stat_file_name}")

#检测是否人工更新过数据
def check_update(input_dir, output_file):
    # 用于存储所有更新过的记录
    updated_records = []

    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(input_dir, filename)
            
            # 打开并读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 遍历JSON文件中的每条记录
            for item in data:
                doc_id = item.get("docId")
                record_id = item.get("id")
                start_time = item.get("startTime").strip()
                start_time_label = item.get("startTime-label").strip()
                end_time = item.get("endTime").strip()
                end_time_label = item.get("endTime-label").strip()
                address = item.get("address").strip()
                address_label = item.get("address-label").strip()
                
                # 比较三对数据
                if (start_time != start_time_label) or (end_time != end_time_label) or (address != address_label):
                    # 如果至少有一对数据不相等，保存这条记录
                    updated_record = {
                        "docId": doc_id,
                        "id": record_id,
                        "startTime": start_time,
                        "startTime-label": start_time_label,
                        "endTime": end_time,
                        "endTime-label": end_time_label,
                        "address": address,
                        "address-label": address_label
                    }
                    updated_records.append(updated_record)
    
    # 如果有更新过的记录，将它们输出到文件中
    if updated_records:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_records, f, ensure_ascii=False, indent=4)
        print(f"Updated records have been saved to {output_file}")
    else:
        print("No updates found.")
     
if __name__ == "__main__":
    #生成目录下所有文件的统计数据
    input_dir = r'D:\kw\数据业务部\数据业务\采编助手\行程\国外行程\json_txm'
    output_dir = r'D:\kw\数据业务部\数据业务\采编助手\行程\国外行程\stat_txm'
    process_stat(input_dir, '.json', output_dir)

    #检测是否人工更新过数据
    input_dir = r'D:\kw\数据业务部\数据业务\采编助手\行程\国外行程\json_txm'
    output_file = r'D:\kw\数据业务部\数据业务\采编助手\行程\国外行程\update_txm.json'
    check_update(input_dir, output_file)   
    
    #检测单个文件
    #file_name = r'D:\kw\数据业务部\数据业务\采编助手\行程\数据20241107\kw\上海市.xlsx'
    #find_matching_records(file_name)

    #检测目录下所有文件
    #input_dir = r'D:\kw\数据业务部\数据业务\采编助手\行程\数据20241107\lxc'
    #log_file = r'D:\kw\数据业务部\数据业务\采编助手\行程\数据20241107\lxc_log.txt'
    #check_dir_excel(input_dir,  log_file)

    # 将目录下的所有CSV文件转换为XLSX格式
    #input_dir = r'D:\kw\数据业务部\数据业务\采编助手\国外行程\csv'
    #output_dir = r'D:\kw\数据业务部\数据业务\采编助手\国外行程\xlsx'
    #convert_csv_to_xlsx(input_dir, output_dir)

    #统计目录下所有文件的行数
    #input_dir = r'D:\kw\数据业务部\数据业务\采编助手\国内行程\行程标注数据1111'
    #output_file = r'D:\kw\数据业务部\数据业务\采编助手\国内行程\国内行程_stat.xlsx'
    #row_count(input_dir, '.xlsx', output_file)