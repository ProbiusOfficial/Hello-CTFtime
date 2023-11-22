from datetime import datetime, timedelta
import feedparser
import requests
import json

cn_ctf_url = 'https://www.su-sanha.cn:443/api/events/list'

rssUpcoming = 'https://ctftime.org/event/list/upcoming/rss/'
rssActive = 'https://ctftime.org/event/list/archive/rss/'
rssNowrunning = 'https://ctftime.org/event/list/running/rss/'

def fetch_cn_ctf_data(url):
    # 使用POST请求获取国内CTF数据
    response = requests.post(url)
    return response.json()

def fetch_global_ctf_content(rss_url):
    feed = feedparser.parse(rss_url)
    events = []  
    try:
        feedTitle = feed['feed']['title']
    except KeyError:
        print('RSS源解析失败，请检查URL是否正确')

    for entry in feed.entries:

        eventName = entry.title

        # 时间处理部分
        start_date = datetime.strptime(entry.start_date, '%Y%m%dT%H%M%S')
        finish_date = datetime.strptime(entry.finish_date, '%Y%m%dT%H%M%S')
        start_date_utc8 = start_date + timedelta(hours=8)
        finish_date_utc8 = finish_date + timedelta(hours=8)
        time_range = f'{start_date_utc8.strftime("%Y-%m-%d %H:%M:%S")} - {finish_date_utc8.strftime("%Y-%m-%d %H:%M:%S")} UTC+8'
        eventTime = time_range

        # 添加日历部分
        calendar_start_index = entry.description.find('[add to calendar]')
        if calendar_start_index != -1:
            calendar_end_index = entry.description.find('</a>', calendar_start_index)
            calendar_link_start_index = entry.description.rfind('href="', 0, calendar_start_index) + 6
            calendar_link = entry.description[calendar_link_start_index:calendar_end_index]
            calendar_link = calendar_link.replace('">[add to calendar]','')
            addCalendar = calendar_link
        else:
            addCalendar = None

        # 主办方部分
        organizers_data = json.loads(entry.organizers)
        organizers_names = []
        organizers_urls = []
        for organizer in organizers_data:
            name = organizer['name']
            url = 'https://ctftime.org/team/' + str(organizer['id'])
            organizers_names.append(name)
            organizers_urls.append(url)
        organizers_names_str = ', '.join(organizers_names)
        organizers_urls_str = ', '.join(organizers_urls)

        eventUrl = entry.url
        eventName = f'{eventName}'
        eventType = entry.format_text
        eventLogo = 'https://ctftime.org' + entry.logo_url
        eventWeight = entry.weight
        eventOrganizers =  f'{organizers_names_str} ({organizers_urls_str})'
        
        eventData= {
                    '比赛名称': eventName,
                    '比赛时间': eventTime,
                    '添加日历': addCalendar,
                    '比赛形式': eventType,
                    '比赛链接': eventUrl,
                    '比赛标志': eventLogo,
                    '比赛权重': eventWeight,
                    '赛事主办': eventOrganizers,
                    '比赛ID' : entry.ctf_id,
                    '比赛状态': ''
                }
        if rss_url == rssUpcoming:
            eventData['比赛状态'] = 'oncoming'
        elif rss_url == rssActive:
            eventData['比赛状态'] = 'past'
        elif rss_url == rssNowrunning:
            eventData['比赛状态'] = 'nowrunning'

        events.append(eventData)

    return events

upcoming_events = fetch_global_ctf_content(rssUpcoming)
active_events = fetch_global_ctf_content(rssActive)
running_events = fetch_global_ctf_content(rssNowrunning)

all_events = upcoming_events + running_events + active_events 
with open('Global.json', 'w', encoding='utf-8') as file:
    json.dump(all_events, file, ensure_ascii=False, indent=4)

cn_ctf_data = fetch_cn_ctf_data(cn_ctf_url)
cn_json_data = json.dumps(cn_ctf_data, ensure_ascii=False)
with open('CN.json', 'w', encoding='utf-8') as cn_file:
    cn_file.write(cn_json_data)

print("数据抓取完成，保存为 CN.json 和 Global.json")