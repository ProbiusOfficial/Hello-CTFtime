import json
from datetime import datetime
import re

def parse_cn_datetime(time_str):
    """解析中文时间格式，支持补零和不补零两种格式"""
    if not time_str:
        return None
    normalized = re.sub(r'(\d{4})年(\d{1,2})月(\d{1,2})日', 
                        lambda m: f"{m.group(1)}年{int(m.group(2)):02d}月{int(m.group(3)):02d}日", 
                        time_str)
    try:
        return datetime.strptime(normalized, '%Y年%m月%d日 %H:%M')
    except ValueError:
        return None

def get_register_events(data):
    """获取正在报名的赛事（当前时间在报名时间区间内，且比赛尚未开始）"""
    register_events = []
    now = datetime.now()
    
    for event in data.get('data', {}).get('result', []):
        reg_start = parse_cn_datetime(event.get('reg_time_start', ''))
        reg_end = parse_cn_datetime(event.get('reg_time_end', ''))
        comp_start = parse_cn_datetime(event.get('comp_time_start', ''))
        
        # 如果无法解析时间，跳过
        if not reg_start or not reg_end or not comp_start:
            continue
        
        # 当前时间在报名时间区间内，且比赛尚未开始
        if reg_start <= now <= reg_end and now < comp_start:
            register_events.append(event)
    
    return register_events

def process_global_events(events):
    upcoming_events = []
    now_running_events = []
    past_events = []
    for event in events:
        if event['比赛状态'] == 'oncoming':
            upcoming_events.append(event)
        elif event['比赛状态'] == 'nowrunning':
            now_running_events.append(event)
        elif event['比赛状态'] == 'past':
            past_events.append(event)
    return upcoming_events, now_running_events, past_events

def process_cn_events(data):
    upcoming_events = []
    now_running_events = []
    past_events = []
    for event in data['data']['result']:
        status = event['status']
        if status == "即将开始":  # 即将开始
            upcoming_events.append(event)
        elif status == "正在进行":  # 正在进行
            now_running_events.append(event)
        elif status == "已经结束":  # 已经结束
            past_events.append(event)
    return upcoming_events, now_running_events, past_events


def create_md_content(events, template, event_type="global"):
    md_content = []
    for event in events:

        event_with_defaults = {
            '比赛名称': event.get('比赛名称', ''),
            '比赛链接': event.get('比赛链接', ''),
            '比赛标志': event.get('比赛标志', ''),
            '比赛形式': event.get('比赛形式', ''),
            '比赛时间': event.get('比赛时间', ''),
            '比赛权重': event.get('比赛权重', ''),
            '赛事主办': event.get('赛事主办', ''),
            '添加日历': event.get('添加日历', ''),
            'name': event.get('name', ''),
            'url': event.get('link', ''),
            'type': event.get('type', ''),
            'reg_time_start': event.get('reg_time_start', ''),
            'reg_time_end': event.get('reg_time_end', ''),
            'comp_time_start': event.get('comp_time_start', ''),
            'comp_time_end': event.get('comp_time_end', ''),
            'readmore': event.get('readmore', '').replace('\n', ' ').replace('\r', ' '),
        }
        if event_type == "global":
            md_content.append(template.format(**event_with_defaults))
        else:
            md_content.append(template.format(**event_with_defaults))
    return "\n".join(md_content)

def create_html_content(register_cn_count, upcoming_cn_count, running_cn_count, upcoming_global_count, running_global_count):
    html_template = """                    <div>
                        <strong id="greeting"></strong><br>
                        <br>
                        <b>国内</b> 共有 {0} 场比赛正在报名,<br>
                        <a href="Upcoming_events/#_2">{1}</a> 场比赛即将开始,
                        <a href="Now_running/#_2">{2}</a> 场比赛正在进行。<br>
                        <b>国外</b> 共有 <a href="Upcoming_events/#_3">{3}</a> 场比赛即将开始,<br>
                        <a href="Now_running/#_3">{4}</a> 场比赛正在进行。<br>
                        <br>
                        您可以点击左侧栏来查看不同状态的比赛详细。

                    </div>
"""
    return html_template.format(register_cn_count, upcoming_cn_count, running_cn_count, upcoming_global_count, running_global_count)

def main():
    # Load Global.json and CN.json
    with open('Global.json', 'r', encoding='utf-8') as file:
        global_data = json.load(file)
    with open('CN.json', 'r', encoding='utf-8') as file:
        cn_data = json.load(file)

    # Process events
    upcoming_global, running_global, past_global = process_global_events(global_data)
    upcoming_cn, running_cn, past_cn = process_cn_events(cn_data)
    register_events = get_register_events(cn_data)

    # Markdown templates
    global_template = (
        '??? Quote "[{比赛名称}]({比赛链接})"  \n'
        "    [![]({比赛标志}){{ width=\"200\" align=left }}]({比赛链接})  \n"
        "    **比赛名称** : [{比赛名称}]({比赛链接})  \n"
        "    **比赛形式** : {比赛形式}  \n"
        "    **比赛时间** : {比赛时间}  \n"
        "    **比赛权重** : {比赛权重}  \n"
        "    **赛事主办** : {赛事主办}  \n"
        "    **添加日历** : {添加日历}  \n"
        "    "
    )
    cn_template = (
        '??? Quote "{name}"  \n'
        "    **比赛名称** : [{name}]({url})  \n"
        "    **比赛类型** : {type}  \n"
        "    **报名时间** : {reg_time_start} - {reg_time_end}  \n"
        "    **比赛时间** : {comp_time_start} - {comp_time_end}  \n"
        "    **其他说明** : {readmore}  \n"
        "    "
    )

    # Generate Markdown content 先生成国内赛事
    registration_md = "---\ncomments: true\n---\n# 正在报名\n\n## 国内赛事\n\n" + create_md_content(register_events, cn_template, "cn")

    now_running_md = "---\ncomments: true\n---\n# 正在进行\n\n## 国内赛事\n\n" + create_md_content(running_cn, cn_template, "cn") + "\n\n## 国际赛事\n\n" + create_md_content(running_global, global_template)

    upcoming_events_md = "---\ncomments: true\n---\n# 即将开始\n\n## 国内赛事\n\n" + create_md_content(upcoming_cn, cn_template, "cn") + "\n\n## 国际赛事\n\n" +  create_md_content(upcoming_global, global_template)

    past_events_md = "---\ncomments: true\n---\n# 已经结束\n\n## 国内赛事\n\n" + create_md_content(past_cn, cn_template, "cn") + "\n\n## 国际赛事\n" +  create_md_content(past_global, global_template)

    html_content = create_html_content(len(register_events),len(upcoming_cn), len(running_cn), len(upcoming_global), len(running_global))

    with open('Out/Now_running.md', 'w', encoding='utf-8') as file:
        file.write(now_running_md)
    with open('Out/Upcoming_events.md', 'w', encoding='utf-8') as file:
        file.write(upcoming_events_md)
    with open('Out/Past_events.md', 'w', encoding='utf-8') as file:
        file.write(past_events_md)
    with open('Out/events.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

    # 生成index.md
    global_template_index = (
        '        ??? Quote "[{比赛名称}]({比赛链接})"  \n'
        "            [![]({比赛标志}){{ width=\"200\" align=left }}]({比赛链接})  \n"
        "            **比赛名称** : [{比赛名称}]({比赛链接})  \n"
        "            **比赛形式** : {比赛形式}  \n"
        "            **比赛时间** : {比赛时间}  \n"
        "            **比赛权重** : {比赛权重}  \n"
        "            **赛事主办** : {赛事主办}  \n"
        "            **添加日历** : {添加日历}  \n"
        "            "
    )
    cn_template_index = (
        '        ??? Quote "[{name}]({url})"  \n'
        "            **比赛名称** : [{name}]({url})  \n"
        "            **比赛类型** : {type}  \n"
        "            **报名时间** : {reg_time_start} - {reg_time_end}  \n"
        "            **比赛时间** : {comp_time_start} - {comp_time_end}  \n"
        "            **其他说明** : {readmore}  \n"
        "            "
    )
    cn_template_index_register = (
        '    ??? Quote "[{name}]({url})"  \n'
        "        **比赛名称** : [{name}]({url})  \n"
        "        **比赛类型** : {type}  \n"
        "        **报名时间** : {reg_time_start} - {reg_time_end}  \n"
        "        **比赛时间** : {comp_time_start} - {comp_time_end}  \n"
        "        **其他说明** : {readmore}  \n"
        "        "
    )


    register_events_md_index = """    === "查看比赛:"

    !!! warning "健康比赛忠告"
        抵制不良比赛，拒绝盗版比赛。注意自我保护，谨防受骗上当。  
        适度CTF益脑，沉迷CTF伤身。合理安排时间，享受健康生活。

=== "*正在报名*"
""" + create_md_content(register_events, cn_template_index_register, "cn")
    
    now_running_md_index = """
=== "*即将开始*"
    === "国内赛事"
""" + create_md_content(upcoming_cn, cn_template_index, "cn") + """
    === "国外赛事"
""" + create_md_content(upcoming_global, global_template_index)

    upcoming_events_md_index = """
=== "*正在进行*"
    === "国内赛事"
""" + create_md_content(running_cn, cn_template_index, "cn") + """
    === "国外赛事"
""" + create_md_content(running_global, global_template_index)
    
    past_events_md_index = """
=== "*已经结束*"
    === "国内赛事"
""" + create_md_content(past_cn, cn_template_index, "cn") + """
    === "国外赛事"
""" + create_md_content(past_global, global_template_index)

    with open('Out/index.md', 'w', encoding='utf-8') as file:
        # 在所有内容前加一个 Tab 缩进
        content = register_events_md_index + now_running_md_index + upcoming_events_md_index + past_events_md_index
        content = content.replace("\n", "\n    ")
        file.write(content)

    print("Done!")

    # 根据比赛时间排序，国内国外分别生成最近的四场比赛并且输出为home.md
    upcoming_cn.sort(key=lambda x: x['comp_time_start'])
    upcoming_global.sort(key=lambda x: x['比赛时间'])
    upcoming_cn = upcoming_cn[:4]
    upcoming_global = upcoming_global[:4]
    upcoming_cn_md = """    === "国内比赛"
""" + create_md_content(upcoming_cn, cn_template_index, "cn")
    
    upcoming_global_md = """    
    === "国外比赛"
""" + create_md_content(upcoming_global, global_template_index)
    with open('Out/home.md', 'w', encoding='utf-8') as file:
        content = upcoming_cn_md + upcoming_global_md
        file.write(content)
    
if __name__ == "__main__":
    main()
