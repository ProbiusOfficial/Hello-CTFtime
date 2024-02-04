import json

# 从 .gihub/issues/temp 文件中提取issue_body

with open(".github/issues/temp", "r", encoding="utf-8") as f:
    issue_body = f.read()

def getIssueBody(issue_body):
    sections = issue_body.split("###")[1:]  


    structured_data = {}

    for section in sections:
        lines = section.strip().split("\n", 2)  
        title = lines[0].strip()
        content = lines[-1].strip()  

        if "赛事名称" in title:
            structured_data["name"] = content
        elif "比赛链接" in title:
            structured_data["link"] = content
        elif "比赛类型" in title:
            structured_data["type"] = content
        elif "报名开始时间" in title:
            structured_data["bmks"] = content
        elif "报名结束时间" in title:
            structured_data["bmjz"] = content
        elif "比赛开始时间" in title:
            structured_data["bsks"] = content
        elif "比赛结束时间" in title:
            structured_data["bsjs"] = content
        elif "备注信息" in title:
            structured_data["readmore"] = content
        elif "比赛状态" in title:

            status, _ = content.split(" - ", 1)
            structured_data["status"] = int(status)

    print(json.dumps(structured_data, ensure_ascii=False, indent=4))
    
    with open(f"待审核/{structured_data['name']}.json", "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=4)

getIssueBody(issue_body)