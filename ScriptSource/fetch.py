import json
import requests
import datetime
from bs4 import BeautifulSoup

# 国内CTF数据的URL和国外CTF数据的URL
cn_ctf_url = 'https://www.su-sanha.cn:443/api/events/list'
global_ctf_url = 'https://ctftime.org/event/list/upcoming/rss/'

# 代理设置，根据需要进行调整
proxies = {
    'http': 'http://localhost:7890',
    'https': 'http://localhost:7890'
}

def fetch_cn_ctf_data(url):
    # 使用POST请求获取国内CTF数据
    response = requests.post(url, proxies=proxies)
    return response.json()

def fetch_global_ctf_content(url):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    response = requests.get(url, proxies=proxies, headers=header)
    return response.content

# 提取数据的函数保持不变
def extract_data(item):
    title = item.find('title').text
    link = item.find('link').text
    description = item.find('description').text
    start_date = item.find('start_date').text
    finish_date = item.find('finish_date').text
    format_text = item.find('format_text').text
    url = item.find('url').text
    logo_url = item.find('logo_url').text
    weight = item.find('weight').text
    organizers = item.find('organizers').text
    
    # 提取比赛名称和链接
    ctf_name = title
    ctf_link = link
    
    # 提取比赛时间并转换为 UTC+8 时间
    start_date = datetime.datetime.strptime(start_date, '%Y%m%dT%H%M%S')
    finish_date = datetime.datetime.strptime(finish_date, '%Y%m%dT%H%M%S')
    start_date = start_date + datetime.timedelta(hours=8)
    finish_date = finish_date + datetime.timedelta(hours=8)
    time_range = f'{start_date.strftime("%Y-%m-%d %H:%M:%S")} - {finish_date.strftime("%Y-%m-%d %H:%M:%S")} UTC+8'
    
    # 提取添加日历链接
    calendar_link = None
    calendar_start_index = description.find('[add to calendar]')
    if calendar_start_index != -1:
        calendar_end_index = description.find('</a>', calendar_start_index)
        calendar_link_start_index = description.rfind('href="', 0, calendar_start_index) + 6
        calendar_link = 'https://ctftime.org' + description[calendar_link_start_index:calendar_end_index]
        calendar_link = calendar_link.replace('">[add to calendar]','')
    
    # 提取比赛形式、链接、标志、权重和主办方
    format_text = format_text
    ctf_link = url
    logo_url = 'https://ctftime.org' + logo_url
    weight = weight
    organizers = json.loads(organizers)
    organizer_name = organizers[0]['name']
    organizer_id = organizers[0]['id']
    organizer_link = 'https://ctftime.org/team/' + str(organizer_id)
    
    # 构建提取后的数据
    extracted_data = {
        '比赛名称': f'{ctf_name} ({ctf_link})',
        '比赛时间': time_range,
        '添加日历': calendar_link,
        '比赛形式': format_text,
        '比赛链接': ctf_link,
        '比赛标志': logo_url,
        '比赛权重': weight,
        '赛事主办': f'{organizer_name} ({organizer_link})'
    }
    
    return extracted_data

def clean_and_extract_global_data(rss_content):
    soup = BeautifulSoup(rss_content, 'html.parser')
    items = soup.find_all('item')
    extracted_data = []
    for item in items:
        extracted_data.append(extract_data(item))
    return extracted_data

# 获取并处理国内CTF数据
cn_ctf_data = fetch_cn_ctf_data(cn_ctf_url)
cn_json_data = json.dumps(cn_ctf_data, ensure_ascii=False)
with open('CN.json', 'w', encoding='utf-8') as cn_file:
    cn_file.write(cn_json_data)

# 获取并处理国外CTF数据
global_ctf_content = fetch_global_ctf_content(global_ctf_url)
global_ctf_data = clean_and_extract_global_data(global_ctf_content)
global_json_data = json.dumps(global_ctf_data, ensure_ascii=False)
with open('Global.json', 'w', encoding='utf-8') as global_file:
    global_file.write(global_json_data)


print("数据抓取完成，保存为 CN.json 和 Global.json")
