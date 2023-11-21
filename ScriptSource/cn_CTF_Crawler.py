import re
import requests

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
