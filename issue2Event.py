import re
import json
import datetime

with open("temp", "r", encoding="utf-8") as f:
    issue_body = f.read()


def body2json(issue_body):
    print(issue_body)

    result_dict = {}
    
    sections = issue_body.split("###")[1:]  
    sections = [section.strip().split("\n\n", 1) for section in sections] 
    
    for item in sections:
        if len(item) == 2:  
            key, vals = item[0].strip(), item[1].strip()
            if "时间" in key:
                date_formats = [
                (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', '%Y-%m-%d %H:%M'),
                (r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}', '%Y/%m/%d %H:%M'),
                (r'\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}', '%Y年%m月%d日 %H:%M')
            ]
                for pattern, date_format in date_formats:
                    if re.match(pattern, vals):
                        vals = datetime.datetime.strptime(vals, date_format).strftime('%Y年%m月%d日 %H:%M')
                        break                
            if key == "比赛状态":
                match = re.search(r'\d+', vals)
                if match:
                    vals = match.group()
                    vals = int(vals)
            result_dict[key] = vals
    json_data = json.dumps(result_dict, ensure_ascii=False, indent=4).replace("时间", "")
    json_dic = {"赛事名称":"name", "比赛链接":"link", "比赛类型":"type", "报名开始":"bmks", "报名结束":"bmjz", "比赛开始":"bsks", "比赛结束":"bsjs", "备注信息":"readmore", "比赛状态":"status"}
    for key, value in json_dic.items():
        json_data = json_data.replace(key, value)

    print(json_data)

    return json_data

def add_Event(json_data):

    with open('./CN.json', 'r', encoding='utf-8') as f:
        CN = json.load(f)
    
    print("Now:" + str(CN['data']['result'][0]))

    print("Insert " + str(json_data) + "into CN.json")
    
    CN['data']['result'].insert(0, json_data)

    print(CN['data']['result'][0])

    with open('./CN.json', 'w', encoding='utf-8') as f:
        json.dump(CN, f, ensure_ascii=False, indent=4)
    
    print("Insert Done")

json_data = json.loads(body2json(issue_body))

with open("temp_name", "w", encoding="utf-8") as f:
    f.write(json_data['name'].replace(" ","-"))

with open("temp_json", "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

add_Event(json_data)




