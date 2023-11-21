# 图形化编程 真的是 一生之敌 
#　　 ┏┓     ┏┓
#　　┏┛┻━━━━━┛┻┓
#　　┃　　　　　 ┃
#　　┃　　━　　　┃
#　　┃　┳┛　┗┳  ┃
#　　┃　　　　　 ┃
#　　┃　　┻　　　┃
#　　┃　　　　　 ┃
#　　┗━┓　　　┏━┛　Code is far away from bug with the animal protecting
#　　　 ┃　　　┃                神兽保佑,代码无bug
#　　　　┃　　　┃
#　　　　┃　　　┗━━━┓
#　　　　┃　　　　　　┣┓
#　　　　┃　　　　　　┏┛
#　　　　┗┓┓┏━┳┓┏┛
#　　　　 ┃┫┫ ┃┫┫
#　　　　 ┗┻┛ ┗┻┛
#
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton

class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.json_format = QTextCharFormat()
        self.json_format.setForeground(QColor("#008000"))  # 设置颜色为绿色

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#FF4500"))  # 设置颜色为橙色

        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#0000FF"))  # 设置颜色为蓝色

        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#000080"))  # 设置颜色为深蓝色
        self.keyword_format.setFontWeight(QFont.Bold)  # 设置为粗体

        self.value_separator_format = QTextCharFormat()
        self.value_separator_format.setForeground(QColor("#800080"))  # 设置颜色为紫色

        self.set_rules()

    def set_rules(self):
        rules = [
            (r'"[^"\\]*(?:\\.[^"\\]*)*"', self.string_format),  # 匹配双引号字符串
            (r'\b(true|false|null)\b', self.keyword_format),  # 匹配关键字 true、false、null
            (r'\b\d+(?:\.\d+)?\b', self.number_format),  # 匹配数字
            (r':', self.value_separator_format)  # 匹配冒号
        ]

        self.highlight_rules = [(QRegExp(pattern), fmt) for pattern, fmt in rules]

    def highlightBlock(self, text):
        for pattern, fmt in self.highlight_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)


class CTFEventQuerySystem(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CTF赛事查询系统")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        btn_cn_ctf = QPushButton("国内赛事查询")
        btn_cn_ctf.clicked.connect(self.cn_ctf)
        layout.addWidget(btn_cn_ctf)

        btn_global_ctf = QPushButton("国外赛事查询")
        btn_global_ctf.clicked.connect(self.global_ctf)
        layout.addWidget(btn_global_ctf)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def cn_ctf(self):
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
        json_data = json.dumps(events, ensure_ascii=False, indent=4)
        self.update_output_text(json_data)

    def global_ctf(self):
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
        json_data = json.dumps(output_data, ensure_ascii=False, indent=4)
        self.update_output_text(json_data)

    def update_output_text(self, data):
        # 创建 JsonHighlighter 对象，并设置高亮显示的文档
        highlighter = JsonHighlighter(self.output_text.document())

        # 将 JSON 数据设置到 QTextEdit 中
        self.output_text.setPlainText(data)



if __name__ == "__main__":
    app = QApplication([])
    window = CTFEventQuerySystem()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    app.exec_()
