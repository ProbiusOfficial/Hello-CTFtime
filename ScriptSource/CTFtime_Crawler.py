import json
import requests
import datetime
from bs4 import BeautifulSoup

rss_url_archive = 'https://ctftime.org/event/list/archive/rss/'

rss_url_oncomoing = 'https://ctftime.org/event/list/upcoming/rss/'

proxies = {
    'http': 'http://localhost:7890',
    'https': 'http://localhost:7890'
}

def fetch_rss_content(rss_url):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    response = requests.get(rss_url, proxies=proxies, headers=header)
    return response.content,rss_url

def extract_data(item,rss_url):
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
        '赛事主办': f'{organizer_name} ({organizer_link})',
        '比赛状态': ''
    }

    extracted_data['比赛状态'] = 'past' if rss_url == rss_url_archive else 'oncoming' if rss_url == rss_url_oncomoing else 'nowrunning'

    return extracted_data


def clean_and_extract_data(rss_content):
    soup = BeautifulSoup(rss_content, 'html.parser')
    items = soup.find_all('item')
    extracted_data = []
    for item in items:
        extracted_data.append(extract_data(item))
    return extracted_data

def clean_and_extract_data(rss_content):
    soup = BeautifulSoup(rss_content, 'html.parser')
    items = soup.find_all('item')
    extracted_data = []
    for item in items:
        extracted_data.append(extract_data(item))
    return extracted_data


def print_json(rss_content):
    extracted_data = clean_and_extract_data(rss_content)
    for data in extracted_data:
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.replace('\n', '')
    
    output_data = []
    for data in extracted_data:
        output_data.append(data)

    return json.dumps(output_data, ensure_ascii=False)

rss_content_archive = fetch_rss_content(rss_url_archive)
rss_comtent_oncoming = fetch_rss_content(rss_url_oncomoing)

print("-------------------archive---------------\n")
print(print_json(rss_content_archive))
print("------------------oncoming---------------\n")
print(print_json(rss_comtent_oncoming))