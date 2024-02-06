from datetime import datetime, timedelta
import feedparser
import requests
import json

# 国外赛事更新:

rssUpcoming = 'https://ctftime.org/event/list/upcoming/rss/'
rssActive = 'https://ctftime.org/event/list/archive/rss/'
rssNowrunning = 'https://ctftime.org/event/list/running/rss/'

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

print("国际赛事数据已更新至Global.json")

# 国内赛事状态更新

with open('./CN.json', 'r', encoding='utf-8') as f:
    CN = json.load(f)

date = datetime.now() + timedelta(hours=8)

# 更新状态
for event in CN['data']['result']:
    bmks = datetime.strptime(event['bmks'], '%Y年%m月%d日 %H:%M')
    bmjz = datetime.strptime(event['bmjz'], '%Y年%m月%d日 %H:%M')
    bsks = datetime.strptime(event['bsks'], '%Y年%m月%d日 %H:%M')
    bsjs = datetime.strptime(event['bsjs'], '%Y年%m月%d日 %H:%M')
    if date < bmks:
        event['status'] = 0 # 未开始
    elif date < bmjz:
        event['status'] = 1 # 报名中
    elif date < bsks:
        event['status'] = 2 # 报名结束
    elif date < bsjs:
        event['status'] = 3 # 进行中
    else:
        event['status'] = 4 # 已结束

# 按照状态排序 0 1 2 3 4
CN['data']['result'] = sorted(CN['data']['result'], key=lambda x: x['status'])

with open('./CN.json', 'w', encoding='utf-8') as f:
    json.dump(CN, f, ensure_ascii=False, indent=4)

    