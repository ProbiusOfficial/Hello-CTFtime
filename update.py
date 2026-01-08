from datetime import datetime, timedelta
import feedparser
import requests
import base64
import json
import hashlib
import re

# 国外赛事更新:

rssUpcoming = 'https://ctftime.org/event/list/upcoming/rss/'
rssActive = 'https://ctftime.org/event/list/archive/rss/'
rssNowrunning = 'https://ctftime.org/event/list/running/rss/'

def fetch_global_ctf_content(rss_url):
    try:
        feed = feedparser.parse(rss_url)
    except Exception as e:
        print(f'RSS源获取失败: {e}')
        return False
    
    events = []
    
    # 检查feed是否有效
    if not feed or 'feed' not in feed or 'title' not in feed.get('feed', {}):
        print('RSS源解析失败，请检查URL是否正确')
        return False

    for entry in feed.entries:
        try:
            eventName = getattr(entry, 'title', 'Unknown Event')

            # 时间处理部分
            start_date_str = getattr(entry, 'start_date', None)
            finish_date_str = getattr(entry, 'finish_date', None)
            
            if not start_date_str or not finish_date_str:
                print(f'Warning: Event "{eventName}" missing date info, skipping')
                continue
                
            start_date = datetime.strptime(start_date_str, '%Y%m%dT%H%M%S')
            finish_date = datetime.strptime(finish_date_str, '%Y%m%dT%H%M%S')
            start_date_utc8 = start_date + timedelta(hours=8)
            finish_date_utc8 = finish_date + timedelta(hours=8)
            time_range = f'{start_date_utc8.strftime("%Y-%m-%d %H:%M:%S")} - {finish_date_utc8.strftime("%Y-%m-%d %H:%M:%S")} UTC+8'
            eventTime = time_range

            # 添加日历部分
            description = getattr(entry, 'description', '')
            addCalendar = None
            calendar_start_index = description.find('[add to calendar]')
            if calendar_start_index != -1:
                calendar_end_index = description.find('</a>', calendar_start_index)
                calendar_link_start_index = description.rfind('href="', 0, calendar_start_index) + 6
                calendar_link = description[calendar_link_start_index:calendar_end_index]
                calendar_link = calendar_link.replace('">[add to calendar]','')
                addCalendar = calendar_link

            # 主办方部分
            organizers_str = getattr(entry, 'organizers', '[]')
            try:
                organizers_data = json.loads(organizers_str)
            except json.JSONDecodeError:
                organizers_data = []
            
            organizers_names = []
            organizers_urls = []
            for organizer in organizers_data:
                name = organizer.get('name', 'Unknown')
                org_id = organizer.get('id', '')
                url = f'https://ctftime.org/team/{org_id}' if org_id else ''
                organizers_names.append(name)
                organizers_urls.append(url)
            organizers_names_str = ', '.join(organizers_names)
            organizers_urls_str = ', '.join(organizers_urls)

            eventUrl = getattr(entry, 'url', '')
            eventType = getattr(entry, 'format_text', '')
            logo_url = getattr(entry, 'logo_url', '')
            eventLogo = f'https://ctftime.org{logo_url}' if logo_url else ''
            eventWeight = getattr(entry, 'weight', '0.00')
            eventOrganizers = f'{organizers_names_str} ({organizers_urls_str})' if organizers_names_str else ''
            
            eventData = {
                '比赛名称': eventName,
                '比赛时间': eventTime,
                '添加日历': addCalendar,
                '比赛形式': eventType,
                '比赛链接': eventUrl,
                '比赛标志': eventLogo,
                '比赛权重': eventWeight,
                '赛事主办': eventOrganizers,
                '比赛ID': getattr(entry, 'ctf_id', ''),
                '比赛状态': ''
            }
            
            if rss_url == rssUpcoming:
                eventData['比赛状态'] = 'oncoming'
            elif rss_url == rssActive:
                eventData['比赛状态'] = 'past'
            elif rss_url == rssNowrunning:
                eventData['比赛状态'] = 'nowrunning'

            events.append(eventData)
            
        except Exception as e:
            print(f'Warning: Failed to parse entry "{getattr(entry, "title", "Unknown")}": {e}')
            continue

    return events

upcoming_events = fetch_global_ctf_content(rssUpcoming)
active_events = fetch_global_ctf_content(rssActive)
running_events = fetch_global_ctf_content(rssNowrunning)
all_events = None

if False not in [upcoming_events, active_events, running_events]:
    all_events = upcoming_events + running_events + active_events
    with open('Global.json', 'w', encoding='utf-8') as file:
        json.dump(all_events, file, ensure_ascii=False, indent=4)
    print("国际赛事数据已更新至Global.json")
else:
    print("国际赛事数据更新失败")


# 国内赛事状态更新

with open('./CN.json', 'r', encoding='utf-8') as f:
    CN = json.load(f)

date = datetime.now() + timedelta(hours=8)

# 更新状态

with open('Achieve/CN_archive.json', 'r', encoding='utf-8') as file:
    archive = json.load(file)

def parse_cn_datetime(time_str):
    """解析中文时间格式，支持补零和不补零两种格式"""
    formats = [
        '%Y年%m月%d日 %H:%M',  # 2026年01月01日 12:00
        '%Y年%m月%d日 %H:%M',  # 标准格式
    ]
    # 尝试标准化：将不补零的格式转换为补零格式
    import re
    normalized = re.sub(r'(\d{4})年(\d{1,2})月(\d{1,2})日', 
                        lambda m: f"{m.group(1)}年{int(m.group(2)):02d}月{int(m.group(3)):02d}日", 
                        time_str)
    try:
        return datetime.strptime(normalized, '%Y年%m月%d日 %H:%M')
    except ValueError:
        return None

# 收集需要归档的赛事，避免遍历时修改列表
events_to_archive = []

for event in CN['data']['result']:
    reg_time_start = parse_cn_datetime(event.get('reg_time_start', ''))
    if not reg_time_start:
        reg_time_start = date
    
    reg_time_end = parse_cn_datetime(event.get('reg_time_end', ''))
    if not reg_time_end:
        reg_time_end = date
    
    comp_time_start = parse_cn_datetime(event.get('comp_time_start', ''))
    if not comp_time_start:
        print(f"Warning: Invalid comp_time_start format for event '{event.get('name', 'Unknown')}': {event.get('comp_time_start')}")
        continue
    
    comp_time_end = parse_cn_datetime(event.get('comp_time_end', ''))
    if not comp_time_end:
        print(f"Warning: Invalid comp_time_end format for event '{event.get('name', 'Unknown')}': {event.get('comp_time_end')}")
        continue
    
    if date < comp_time_start:
        event['status'] = "即将开始"
    elif date < comp_time_end:
        event['status'] = "正在进行"
    elif date > comp_time_end:
        event['status'] = "已经结束"
        
        if date > comp_time_end + timedelta(days=60):
            print(event.get('name', 'Unknown') + "已结束超过60天，移至存档")
            events_to_archive.append(event)

    if date >= comp_time_start and date < comp_time_end:
        event['status'] = "正在进行"

# 在遍历结束后处理归档
for event in events_to_archive:
    archive['archive']['result'].append(event)
    CN['data']['result'].remove(event)

        
# 更新存档
            
with open('Achieve/CN_archive.json', 'w', encoding='utf-8') as file:
    json.dump(archive, file, ensure_ascii=False, indent=4)
        
# 定义状态映射表
status_order = {
    '即将开始': 0,
    '正在进行': 1,
    '已经结束': 2
}

# 使用get方法提供默认排序值，避免KeyError
CN['data']['result'] = sorted(CN['data']['result'], key=lambda x: status_order.get(x['status'], float('inf')))


with open('./CN.json', 'w', encoding='utf-8') as f:
    json.dump(CN, f, ensure_ascii=False, indent=4)

if all_events == None:
    with open('Global.json', 'r', encoding='utf-8') as f:
        all_events = json.load(f)
        
# 生成国内比赛的日历订阅内容
def create_CN_ical_event(event):
    try:
        comp_start = parse_cn_datetime(event.get('comp_time_start', ''))
        comp_end = parse_cn_datetime(event.get('comp_time_end', ''))
        
        if not comp_start or not comp_end:
            return None
            
        start_date = comp_start - timedelta(hours=8)
        finish_date = comp_end - timedelta(hours=8)
        
        event_name = event.get('name', 'Unknown Event')
        event_link = event.get('link', '')
        event_type = event.get('type', '')
        reg_start = event.get('reg_time_start', '')
        reg_end = event.get('reg_time_end', '')
        readmore = re.sub(r"\s+", "", event.get('readmore', ''))
        
        description = f"{event_type} | {event_link} | 报名---{reg_start}-{reg_end}-备注-{readmore}"
        
        eventData = {
            'BEGIN': 'VEVENT',
            'SUMMARY': event_name,
            'DTSTART': start_date.strftime("%Y%m%dT%H%M%SZ"),
            'DTEND': finish_date.strftime("%Y%m%dT%H%M%SZ"),
            'UID': hashlib.md5(event_name.encode('utf-8')).hexdigest(),
            'VTIMEZONE': 'Asia/Shanghai',
            'DTSTAMP': datetime.now().strftime("%Y%m%dT%H%M%SZ"),
            'CREATED': datetime.now().strftime("%Y%m%dT%H%M%SZ"),
            'URL': event_link,
            'DESCRIPTION': description,
            'END': 'VEVENT'
        }
        return eventData
    except Exception as e:
        print(f"Warning: Failed to create ical event for '{event.get('name', 'Unknown')}': {e}")
        return None

# 生成国外比赛的日历订阅内容

def create_Global_ical_event(event):
    start_date = event['比赛时间'].split(' - ')[0]
    finish_date = event['比赛时间'].split(' - ')[1].replace(' UTC+8', '')
    start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=8)
    finish_date = datetime.strptime(finish_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=8)
    eventData= {
                'BEGIN':'VEVENT',
                'SUMMARY':event['比赛名称'],
                'DTSTART':start_date.strftime("%Y%m%dT%H%M%SZ"),
                'DTEND':finish_date.strftime("%Y%m%dT%H%M%SZ"),
                'UID':hashlib.md5(event['比赛名称'].encode('utf-8')).hexdigest(),
                'VTIMEZONE':'Asia/Shanghai',
                'DTSTAMP':datetime.now().strftime("%Y%m%dT%H%M%SZ"),
                'CREATED':datetime.now().strftime("%Y%m%dT%H%M%SZ"),
                'URL':event['比赛链接'],
                'DESCRIPTION':event['比赛形式']+' | '+event['比赛链接']+' | '+' | '+'比赛ID - '+str(event['比赛ID']),
                'END':'VEVENT'
            }
    return eventData

# 生成国内赛事日历
CN_ical_events = []
for event in CN['data']['result']:
    ical_event = create_CN_ical_event(event)
    if ical_event:
        CN_ical_events.append(ical_event)

with open('./calendar/CN.ics', 'w', encoding='utf-8') as f:
    f.write('BEGIN:VCALENDAR\n')
    f.write('VERSION:2.0\n')
    f.write('PRODID:-//CTF//CN//\n')
    f.write('CALSCALE:GREGORIAN\n')
    f.write('X-WR-CALNAME:CN\n')
    for event in CN_ical_events:
        for key, value in event.items():
            f.write(f'{key}:{value}\n')
        f.write('\n')
    f.write('END:VCALENDAR')

# 生成国际赛事日历
Global_ical_events = []
for event in all_events:
    Global_ical_events.append(create_Global_ical_event(event))

with open('./calendar/Global.ics', 'w', encoding='utf-8') as f:
    f.write('BEGIN:VCALENDAR\n')
    f.write('TZID:Asia/Shanghai\n')
    f.write('VERSION:2.0\n')
    f.write('PRODID:-//CTF//Global//\n')
    f.write('CALSCALE:GREGORIAN\n')
    f.write('X-WR-CALNAME:Global\n')
    for event in Global_ical_events:
        for key, value in event.items():
            f.write(f'{key}:{value}\n')
        f.write('\n')
    f.write('END:VCALENDAR')

# 将Global.json 和 CN.json 通过Base64编码后存储为 Global.b64 以供大陆用户使用
with open('Global.json', 'r', encoding='utf-8') as f:
    Global = f.read()
    Global = Global.encode('utf-8')
    Global = base64.b64encode(Global).decode('utf-8')
    with open('Global.b64', 'w', encoding='utf-8') as f:
        f.write(Global)

with open('CN.json', 'r', encoding='utf-8') as f:
    CN = f.read()
    CN = CN.encode('utf-8')
    CN = base64.b64encode(CN).decode('utf-8')
    with open('CN.b64', 'w', encoding='utf-8') as f:
        f.write(CN)  
