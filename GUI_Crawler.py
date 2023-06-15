# 图形化编程 = 一生之敌（
# 　　　┏┓　 ┏┓
# 　　┏┛┻━━━┛┻━━┓
# 　　┃　     　 ┃
# 　　┃　＞　　＜┃
# 　　┃　　　　　┃
# 　　┃ .. ⌒ ..┃
# 　　┃　　　　　┃
# 　　┗━┓　　　┏━┛
# 　　　┃　　　┃　Codes are far away from bugs with the animal protecting　　　　　　　
# 　　　┃　　　┃                  神兽保佑,代码无bug
# 　　　┃　　　┃　　　　　　　　　　　
# 　　　┃　　　┗━━━┓
# 　　　┃　　　　　　┣┓
# 　　　┃　　　　____┏┛
# 　　　┗┓┓┏━┳┓┏┛
# 　　　　┃┫┫　┃┫┫
# 　　　　┗┻┛　┗┻┛

import re
import json
import datetime
import requests
import tkinter as tk
from bs4 import BeautifulSoup

# GUI窗口
window = tk.Tk()
window.title("CTF赛事查询系统")

# 按钮点击事件处理函数
def cn_ctf():
    def fetch_ctf_events():
        url = "https://www.su-sanha.cn/events/"
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        Cookie = {
            "lg": "cn;",
            "PbootSystem": "cbvq2lqffmubftgima304r574c",
        }
        request = requests.get(url=url, cookies=Cookie, headers=header)
        res1 = re.findall(r'<div><label>(.*?)</.?></div>', request.text)

        events = []
        event = {}
        for i in range(len(res1) - 1):
            if "比赛名称" in res1[i]:
                if event:  # If the event is not empty, add it to the events list
                    events.append(event)
                event = {}  # Start a new event

            # Remove the label tag and field name
            field_name, field_value = re.sub(r'</label><.*?>', '', res1[i]).split("：", 1)

            # If the field_value is empty, set it to null
            if not field_value.strip():
                field_value = None

            event[field_name] = field_value

        if event:  # Add the last event to the events list
            events.append(event)

        return events

    events = fetch_ctf_events()

    # 将数据转换为JSON格式并输出
    json_data = json.dumps(events, ensure_ascii=False)
    update_output_text(json_data)


def global_ctf():

    proxies = {
    'http': 'http://localhost:7890',
    'https': 'http://localhost:7890'
}

    rss_url = 'https://ctftime.org/event/list/upcoming/rss/'
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    response = requests.get(rss_url, proxies=proxies, headers=header)
    rss_content = response.content

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
            calendar_link = calendar_link.replace('">[add to calendar]', '')

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

    def clean_and_extract_data(rss_content):
        soup = BeautifulSoup(rss_content, 'html.parser')
        items = soup.find_all('item')
        extracted_data = []
        for item in items:
            extracted_data.append(extract_data(item))
        return extracted_data

    extracted_data = clean_and_extract_data(rss_content)

    # 处理换行符
    for data in extracted_data:
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.replace('\n', '')

    # 输出数据为集合形式
    output_data = []
    for data in extracted_data:
        output_data.append(data)

    # 将数据转换为JSON格式并输出
    json_data = json.dumps(output_data, ensure_ascii=False)
    update_output_text(json_data)


# 按钮控件
btn_cn_ctf = tk.Button(window, text="国内赛事查询", command=cn_ctf)
btn_cn_ctf.pack()

btn_global_ctf = tk.Button(window, text="国外赛事查询", command=global_ctf)
btn_global_ctf.pack()

# 显示区域控件
output_text = tk.Text(window, height=20, width=100)
output_text.pack()

# 设置输出文本为只读
output_text.configure(state='disabled')


# 更新显示区域的函数
def update_output_text(data):
    # 启用输出文本的编辑状态
    output_text.configure(state='normal')
    # 清空文本内容
    output_text.delete('1.0', 'end')
    # 将新数据插入文本框
    formatted_data = json.dumps(json.loads(data), ensure_ascii=False, indent=4)
    output_text.insert('1.0', formatted_data)
    # 禁用输出文本的编辑状态
    output_text.configure(state='disabled')


# 运行GUI窗口
window.mainloop()
