# -*- coding: utf-8 -*-
import json
import re
import pandas as pd

def json_to_excel(filter, idFlag, json_file_name, excel_file_name):
    # 读取JSON文件
    with open(json_file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 初始化列表来存储解析后的数据
    parsed_data = []
    
    # 遍历JSON数据
    for item in data:
        # "region": "国内-湖南省-长沙市"
        # "region": "国内-直辖市-北京市",
        # "region": "国内-直辖市-北京市-丰台区",
        # "region": "国内-特别行政区-香港特别行政区"
        region_list = item['region'].split('-')
        province = region_list[1] # 提取省名称
        region = region_list[2]  # 提取地级名称
        if province in ['直辖市', '特别行政区']:
            province = region_list[2] # 提取直辖市|特别行政区
            if len(region_list) >= 4: # 提取直辖市|特别行政区的区，可能为空
                region = region_list[3]
            else:
                region = ''

        # 如果省级名称不在过滤列表中
        if province not in filter:
            continue

        # 读取总文段信息, start_date, end_date，将start_date和end_date时间段的信息，分解成单个日期time_label，形成多条记录
        start_date = item['start_date']
        end_date = item['end_date']
        #枚举日期
        time_range = pd.date_range(start=start_date, end=end_date)
        for time_value in time_range:
            time_value = time_value.strftime('%Y-%m-%d')        
            record = {
                    'province': province,
                    'time_label': time_value,
                    'region': region,
                    'xianqu_label': '',
                    'xiangzhen_label': '',
                    'cun_label': '',
                    'label_special_place': '',
                    'label_small_special_place': ''
            }
            if idFlag:
                record['id'] = item['id']
            parsed_data.append(record)
                
        max_labels = 12  # 最大标签数量
        for i in range(1, max_labels + 1):
            time_label = f'time_label{i}'
            xianqu_label = f'xianqu_label{i}'
            xiangzhen_label = f'xiangzhen_label{i}'
            cun_label = f'cun_label{i}'
            label_special_place = f'label_special_place{i}'
            label_small_special_place = f'label_small_special_place{i}'
            
            # 获取标签值
            time_value = item.get(time_label, '')
            xianqu_value = item.get(xianqu_label, '')
            xiangzhen_value = item.get(xiangzhen_label, '')
            cun_value = item.get(cun_label, '')
            label_special_place_value = item.get(label_special_place, '')
            label_small_special_place_value = item.get(label_small_special_place, '')

            # 如果以上标签，至少有一个不为空，则添加到记录中
            if any([time_value, xianqu_value, xiangzhen_value, cun_value, label_special_place_value, label_small_special_place_value]):
                record = {
                    'province': province,
                    'time_label': time_value,
                    'region': region,
                    'xianqu_label': xianqu_value,
                    'xiangzhen_label': xiangzhen_value,
                    'cun_label': cun_value,
                    'label_special_place': label_special_place_value,
                    'label_small_special_place': label_small_special_place_value
                }
                if idFlag:
                    record['id'] = item['id']
                parsed_data.append(record)

    # 去重
    unique_data = []
    for record in parsed_data:
        if record not in unique_data:
            unique_data.append(record)

    # 创建DataFrame
    df = pd.DataFrame(unique_data)

    # 设置中文标题
    title =  ['省级','时间', '地级市' , '县/区', '乡/镇', '村/社区街道', '特殊地点', '特殊地点细粒度']
    if idFlag:
        title.append('id')

    df.columns = title
    # 排序
    df = df.sort_values(by=title)
    
    # 输出到Excel文件
    df.to_excel(excel_file_name, index=False)


def check_json(filter, json_file_name, log_file_name):
    # 读取JSON文件
    with open(json_file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 初始化错误信息列表
    error_messages = []
    
    # 遍历JSON数据
    for item in data:
        # "region": "国内-湖南省-长沙市"
        # "region": "国内-直辖市-北京市",
        # "region": "国内-直辖市-北京市-丰台区",
        # "region": "国内-特别行政区-香港特别行政区"
        region_list = item['region'].split('-')
        province = region_list[1] # 提取省名称
        region = region_list[2]  # 提取地级名称
        if province in ['直辖市', '特别行政区']:
            province = region_list[2] # 提取直辖市|特别行政区
            if len(region_list) >= 4: # 提取直辖市|特别行政区的区，可能为空
                region = region_list[3]
            else:
                region = ''

        # 如果省级名称不在过滤列表中
        if province not in filter:
            continue

        region_text = item['region-text']       # 地级市标注文稿

        # 必填项检测
        max_labels = 12  # 最大标签数量
        for i in range(1, max_labels + 1):
            # 获取标签值
            special_text = item.get(f'special-text{i}', '').strip()
            time_value = item.get(f'time_label{i}', '').strip()
            xianqu_value = item.get(f'xianqu_label{i}', '').strip()
            xiangzhen_value = item.get(f'xiangzhen_label{i}', '').strip()
            cun_value = item.get(f'cun_label{i}', '').strip()
            label_special_place_value = item.get(f'label_special_place{i}', '').strip()
            label_small_special_place_value = item.get(f'label_small_special_place{i}', '').strip()

            # 如果时间（time_label）、文稿（special-text）、县/区（xianqu_label）、乡/镇（xiangzhen_label）、村/社区街道（cun_label）、特殊地点（label_special_place）、特殊地点细粒度（label_small_special_place）都为空，则忽略这条记录。
            if not (time_value or special_text or xianqu_value or xiangzhen_value or cun_value or label_special_place_value or label_small_special_place_value):
                continue
            else:
                # 文稿（special-text）为空，则报错；
                if not special_text:
                    error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 文稿（special-text）为空"
                    error_messages.append(error_message)

                # 时间（time_label）为空，则报错；
                if not time_value:
                    error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 时间（time_label）为空"
                    error_messages.append(error_message)

                if label_small_special_place_value and not label_special_place_value:
                    # 如果“特殊地点细粒度”不为空，但“特殊地点”为空
                    error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 特殊地点细粒度不为空时，特殊地点不能为空"
                    error_messages.append(error_message)

            # 格式检测
            if time_value:
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', time_value):
                    # 时间格式不符合YYYY-MM-DD
                    error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 时间：[{time_value}], 错误原因: 时间格式不符合YYYY-MM-DD"
                    error_messages.append(error_message)

            # 遵照原文检测：县区、乡镇、村社区、特殊地点、特殊地点细粒度 在 地市级文稿 中
            if xianqu_value and region_text:
                if xianqu_value not in region_text:
                    error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 县/区内容与文稿不匹配"
                    error_messages.append(error_message)
            
            if xiangzhen_value and region_text:
                if xiangzhen_value not in region_text:
                    error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 乡/镇内容与文稿不匹配"
                    error_messages.append(error_message)
            
            if cun_value and region_text:
                # 支持多值，用半角和全角的分号分隔，用-分割
                cun_values = [v.strip() for v in re.split(';|；|-', cun_value)] 
                for v in cun_values:
                    if v not in region_text:
                        error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 村/社区街道【{v}】与文稿不匹配"
                        error_messages.append(error_message)
            
            if label_special_place_value and region_text:
                # 支持多值，用半角和全角的分号分隔，用-分割
                label_special_place_values = [v.strip() for v in re.split(';|；|-', label_special_place_value)]
                # 只要发现一个不匹配，就报错，报出错误值    
                for v in label_special_place_values:
                    if v not in region_text:
                        error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 特殊地点【{v}】与文稿不匹配"
                        error_messages.append(error_message)
            
            if label_small_special_place_value and region_text:
                # 支持多值，用半角和全角的分号分隔
                label_small_special_place_values = [v.strip() for v in re.split(';|；|-', label_small_special_place_value)]
                # 只要发现一个不匹配，就报错，报出错误值  
                for v in label_small_special_place_values:
                    if v not in region_text:
                        error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 特殊地点细粒度【{v}】与文稿不匹配"
                        error_messages.append(error_message)

            # 遵照原文检测：县区、乡镇、村社区 在 文稿（special-text） 中
            check_special_text = False
            if check_special_text:
                if xianqu_value and special_text:
                    if xianqu_value not in special_text:
                        error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 县/区内容与文稿不匹配"
                        error_messages.append(error_message)
                
                if xiangzhen_value and special_text:
                    if xiangzhen_value not in special_text:
                        error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 乡/镇内容与文稿不匹配"
                        error_messages.append(error_message)
                
                if cun_value and special_text:
                    if cun_value not in special_text:
                        error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 村/社区街道内容与文稿不匹配"
                        error_messages.append(error_message)

            #文稿（special-text）内容，应包含在地市级文稿（region-text）中，否则报错
            #判断方法：将文稿字符串用标点符号空格等分隔符分割后，判断是否在
            check_special_content_text = False
            if check_special_content_text:
                special_text_list = re.split(r'[，。！？、；：“”《》（）【】「」『』（）、\s]|\n', special_text)
                for word in special_text_list:
                    if not word in region_text:
                        error_message = f"id: {item.get('id')}, docId: {item.get('docId')}, 块：{i}, 省: {province}, 地级市: {region}, 错误原因: 文稿内容【{word}】没有完全包含在地市级文稿中"
                        error_messages.append(error_message)
                        break
            
    # 错误信息输出到指定文本文件中
    with open(log_file_name, 'w', encoding='utf-8') as log_file:
        for message in error_messages:
            log_file.write(message + '\n')

# 导出start_date和end_date不同的记录，导出id, start_date, end_date,region 导出到excel中
# start_date和end_date提取日期
def export_diff_date_record(json_file_name, excel_file_name):
    with open(json_file_name, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        # 创建一个空的DataFrame
        df = pd.DataFrame(columns=['id', 'start_date', 'end_date', 'region'])
        # 遍历数据
        for item in data:
            # 获取id, start_date, end_date,region
            id = item.get('id')
            start_date = item.get('start_date').split(' ')[0]
            end_date = item.get('end_date').split(' ')[0]
            region = item.get('region')
            # 如果start_date和end_date不相等，则添加到DataFrame中
            if start_date != end_date:
                new_row = pd.DataFrame()
                new_row['id'] = [id]
                new_row['start_date'] = [start_date]
                new_row['end_date'] = [end_date]
                new_row['region'] = [region]
                df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(excel_file_name, index=False)                    
    
if __name__ == '__main__':
    json_file_name = 'D:\kw\数据业务部\数据业务\采编助手\行程\国内行程\第二阶段\全部.json'

    excel_file_name = 'D:\kw\数据业务部\数据业务\采编助手\行程\国内行程\第二阶段\_view.xlsx'
    id_excel_file_name = 'D:\kw\数据业务部\数据业务\采编助手\行程\国内行程\第二阶段\_id_view.xlsx'
    log_file_name = 'D:\kw\数据业务部\数据业务\采编助手\行程\国内行程\第二阶段\error.txt'

    # filter
    txm_filter = ['辽宁省','吉林省','黑龙江省', '河北省', '河南省', '山西省', '内蒙古自治区', '北京市', '天津市']
    kw_filter = ['江西省', '江苏省', '浙江省', '安徽省', '福建省', '山东省', '湖北省', '上海市']
    xm_filter = ['广西壮族自治区', '广东省', '湖南省', '海南省', '四川省', '云南省', '贵州省', '重庆市']
    lxc_filter = ['西藏自治区', '陕西省', '甘肃省', '青海省', '宁夏回族自治区', '新疆维吾尔自治区', '香港特别行政区', '澳门特别行政区']
    all_filter = xm_filter + kw_filter + xm_filter + lxc_filter
    
    # 生成视图
    json_to_excel(lxc_filter, True, json_file_name, id_excel_file_name)    #包括ID列
    json_to_excel(lxc_filter, False, json_file_name, excel_file_name)

    # 检测错误
    check_json(lxc_filter, json_file_name, log_file_name)

    #导出start_date和end_date不同的记录
    excel_file_name = 'D:\kw\数据业务部\数据业务\采编助手\行程\国内行程\第二阶段\diff_date.xlsx'
    #export_diff_date_record(json_file_name, excel_file_name)

    print('Done!')
