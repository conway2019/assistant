# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json

def extract_mfa_info(url):
    """
    提取中国外交部官网记者会内容：标题、时间、正文
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    try:
        # 1. 请求网页
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. 提取标题
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else '未获取到标题'

        # 3. 提取发布时间
        time_text = None
        time_pattern = re.compile(r'202\d-\d{2}-\d{2}')
        for tag in soup.find_all(['p', 'div', 'span']):
            text = tag.get_text(strip=True)
            match = time_pattern.search(text)
            if match:
                time_text = match.group()
                break

        # 4. 提取正文（过滤无关内容，保留问答主体）
        content_lines = []
        main_content = soup.find('div', class_=re.compile('content|article|main'))
        if main_content:
            paragraphs = main_content.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                # 过滤空行、日期行、导航行
                if text and not re.match(r'^\d{4}-\d{2}-\d{2}', text) and len(text) > 5:
                    content_lines.append(text)

        main_text = '\n\n'.join(content_lines)

        # 5. 返回结果
        return {
            'title': title,
            'time': time_text if time_text else '未获取到时间',
            'content': main_text
        }

    except Exception as e:
        return {'error': f'抓取失败：{str(e)}'}

def save_df_to_excel(target_url, filename):
       #循环处理 target_url 中的每个 URL，保存到record中
    records = []
    for url in target_url:
        # 执行提取 
        result = extract_mfa_info(url)
        record = {}
        if 'error' not in result:
            # 控制台输出
            print('=' * 60)
            print(f'【标题】{result["title"]}')
            print(f'【时间】{result["time"]}')

            #将result保存到records中
            record['title'] = result['title']
            record['time'] = result['time']
            record['content'] = result['content']
            records.append(record)
        else:
            print(result['error'])
            
    # 保存excel文件，设置列名
    title = ['title', 'time', 'content']
    df = pd.DataFrame(records, columns=title)
    df.to_excel(filename, index=False)

    print(f'\n✅ 内容已完整保存至：{filename}')

def save_json_to_excel(target_url, filename):
       #循环处理 target_url 中的每个 URL，保存到record中
    records = []
    for url in target_url:
        # 执行提取 
        result = extract_mfa_info(url)
        if 'error' not in result:
            # 控制台输出
            print('=' * 60)
            print(f'【标题】{result["title"]}')
            print(f'【时间】{result["time"]}')

            #将result保存到records中
            record = {}
            record['title'] = result['title']
            record['time'] = result['time']
            record['content'] = result['content']
            json_record = json.dumps(record, ensure_ascii=False)

            records.append(json_record)
        else:
            print(result['error'])
            
    # 保存excel文件，没有列名
    df = pd.DataFrame(records)
    df.to_excel(filename, index=False,  header=False)

    print(f'\n✅ 内容已完整保存至：{filename}')

# ==================== 主程序 ====================
if __name__ == '__main__':
    #target_url = ["https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202604/t20260415_11892411.shtml"]
    target_url = [
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202604/t20260415_11892411.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202604/t20260414_11891610.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202604/t20260413_11890974.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202604/t20260410_11889948.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202604/t20260409_11889143.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202604/t20260408_11888456.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202604/t20260407_11887644.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202604/t20260403_11886540.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202604/t20260402_11886005.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202604/t20260401_11885126.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260331_11884120.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260330_11883715.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260327_11882425.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260326_11881537.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260325_11880819.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260324_11880190.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260323_11879269.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260320_11878245.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260319_11877656.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260318_11876825.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260317_11876240.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260316_11875472.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260313_11874556.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260312_11873576.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260311_11872831.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260310_11872097.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260309_11871477.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260306_11870039.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260305_11869312.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260304_11868732.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260303_11867941.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202603/t20260302_11867140.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202602/t20260227_11865619.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202602/t20260226_11863973.shtml",
    "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202602/t20260225_11863408.shtml"
    ]

    filename = './data/mfa_info.xlsx'
    save_json_to_excel(target_url, filename)
    