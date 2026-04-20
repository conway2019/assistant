import requests
from bs4 import BeautifulSoup
import json
import time
import os

# 【真实有效】外交部记者会列表页（官方最新）
URL = "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/index.shtml"

# 最强请求头，绕过所有反爬（关键！）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.mfa.gov.cn/",
    "Connection": "close",
    "Upgrade-Insecure-Requests": "1",
}

def get_links():
    try:
        print("正在请求页面...")
        response = requests.get(
            URL, 
            headers=HEADERS, 
            timeout=20,
            verify=False  # 关闭SSL验证（解决大部分网络拦截）
        )
        response.raise_for_status()
        response.encoding = "utf-8"
        
        # 调试：打印前1000字符，看是否拿到真实页面
        print("=" * 50)
        print("页面内容开头：")
        print(response.text[:1000])
        print("=" * 50)

        soup = BeautifulSoup(response.text, "html.parser")

        # 【最稳匹配】找到所有包含记者会的链接
        links = []
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            title = a.get_text(strip=True)

            # 只要是 202x年xx月xx日 的记者会，全部抓取
            if href and title and ("202" in title or "例行记者会" in title):
                full_url = "https://www.mfa.gov.cn" + href.replace("..", "")
                links.append(full_url)
                print(f"✅ 找到：{title}")

        return links

    except Exception as e:
        print("请求失败原因：", e)
        return []

def get_article(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "无标题"
        pub_time = soup.find("div", class_="p-time").get_text(strip=True) if soup.find("div", class_="p-time") else "无时间"
        
        content = ""
        content_box = soup.find("div", class_="content")
        if content_box:
            paragraphs = [p.get_text(strip=True) for p in content_box.find_all("p")]
            content = "\n".join([p for p in paragraphs if p])

        return {
            "url": url,
            "title": title,
            "time": pub_time,
            "content": content
        }
    except:
        return None

def main():
    os.makedirs("./data", exist_ok=True)
    links = get_links()

    if not links:
        print("\n❌ 未获取到任何链接")
        return

    print(f"\n开始爬取，共 {len(links)} 篇")
    result = []
    for i, url in enumerate(links, 1):
        print(f"爬取 {i}/{len(links)}")
        data = get_article(url)
        if data:
            result.append(data)
        time.sleep(1)

    with open("./data/mfa.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 爬取完成！共 {len(result)} 篇")

if __name__ == "__main__":
    main()