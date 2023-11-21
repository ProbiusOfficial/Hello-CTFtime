import json

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
        if status in [0, 1, 2]:
            upcoming_events.append(event)
        elif status == 3:
            now_running_events.append(event)
        elif status == 4:
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
            'bmks': event.get('bmks', ''),
            'bmjz': event.get('bmjz', ''),
            'bsks': event.get('bsks', ''),
            'bsjs': event.get('bsjs', ''),
            'readmore': event.get('readmore', '').replace('\n', ' ').replace('\r', ' '),
        }
        if event_type == "global":
            md_content.append(template.format(**event_with_defaults))
        else:
            md_content.append(template.format(**event_with_defaults))
    return "\n".join(md_content)

def main():
    # Load Global.json and CN.json
    with open('Global.json', 'r', encoding='utf-8') as file:
        global_data = json.load(file)
    with open('CN.json', 'r', encoding='utf-8') as file:
        cn_data = json.load(file)

    # Process events
    upcoming_global, running_global, past_global = process_global_events(global_data)
    upcoming_cn, running_cn, past_cn = process_cn_events(cn_data)

    # Markdown templates
    global_template = (
        '??? Abstract "[{比赛名称}]({比赛链接})"  \n'
        "    [![]({比赛标志})]({比赛链接})  \n"
        "    **比赛名称** : [{比赛名称}]({比赛链接})  \n"
        "    **比赛形式** : {比赛形式}  \n"
        "    **比赛时间** : {比赛时间}  \n"
        "    **比赛权重** : {比赛权重}  \n"
        "    **赛事主办** : {赛事主办}  \n"
        "    **添加日历** : {添加日历}  \n"
        "    "
    )
    cn_template = (
        '??? Abstract "{name}"  \n'
        "    **比赛名称** : [{name}]({url})  \n"
        "    **比赛类型** : {type}  \n"
        "    **报名时间** : {bmks} - {bmjz}  \n"
        "    **比赛时间** : {bsks} - {bsjs}  \n"
        "    **其他说明** : {readmore}  \n"
        "    "
    )

    # Generate Markdown content 先生成国内赛事
    now_running_md = "---\ncomments: true\n---\n# 正在进行\n\n## 国内赛事\n\n" + create_md_content(running_cn, cn_template, "cn") + "\n\n## 国际赛事\n\n" + create_md_content(running_global, global_template)

    upcoming_events_md = "---\ncomments: true\n---\n# 即将开始\n\n## 国内赛事\n\n" + create_md_content(upcoming_cn, cn_template, "cn") + "\n\n## 国际赛事\n\n" +  create_md_content(upcoming_global, global_template)

    past_events_md = "---\ncomments: true\n---\n# 已经结束\n\n## 国内赛事\n\n" + create_md_content(past_cn, cn_template, "cn") + "\n\n## 国际赛事\n" +  create_md_content(past_global, global_template)

    with open('Out/Now_running.md', 'w', encoding='utf-8') as file:
        file.write(now_running_md)
    with open('Out/Upcoming_events.md', 'w', encoding='utf-8') as file:
        file.write(upcoming_events_md)
    with open('Out/Past_events.md', 'w', encoding='utf-8') as file:
        file.write(past_events_md)

if __name__ == "__main__":
    main()
