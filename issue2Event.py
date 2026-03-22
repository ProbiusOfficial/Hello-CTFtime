import sys
import json
from openai import OpenAI

apikey = sys.argv[1]

client = OpenAI(
    api_key=apikey,
    base_url="https://api.moonshot.cn/v1",
)

system_prompt = """
你是一个CTF比赛信息助手，负责从给定的文本中提取结构化信息。国内赛事数据仅保留以下五个字段，请严格使用 JSON 输出，不要增加其他键。

字段说明（时间格式统一为：yyyy年mm月dd日 hh:mm，月与日若为单位数也需补零，例如 2024年09月07日 09:00）：
- name：比赛名称（优先英文或常见写法如 XXXCTF 2024；若无则可用中文全称）
- link：比赛官网或报名页 URL（完整 http/https 链接）
- comp_time_start：比赛开始时间
- comp_time_end：比赛结束时间
- detail：比赛详细说明（主办方、报名方式、QQ群、参赛对象、赛制要点等原文中有用的信息，整理为一段连贯文字；若无则填空字符串）

请使用如下 JSON 格式输出（仅这些键）：

{
  "name": "",
  "link": "",
  "comp_time_start": "yyyy年mm月dd日 hh:mm",
  "comp_time_end": "yyyy年mm月dd日 hh:mm",
  "detail": ""
}
"""

with open("temp", "r", encoding="utf-8") as f:
    issue_body = f.read()

matchInformationText = issue_body


def matchInformationText2json():
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": matchInformationText},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    print(completion.choices[0].message.content)
    json_content = completion.choices[0].message.content

    return json_content


def add_Event(json_data):
    with open("./CN.json", "r", encoding="utf-8") as f:
        CN = json.load(f)

    print("Now:" + str(CN["data"]["result"][0]))

    print("Insert " + str(json_data) + " into CN.json")

    CN["data"]["result"].insert(0, json_data)

    print(CN["data"]["result"][0])

    CN["data"]["total"] = len(CN["data"]["result"])

    with open("./CN.json", "w", encoding="utf-8") as f:
        json.dump(CN, f, ensure_ascii=False, indent=4)

    print("Insert Done")


json_data = json.loads(matchInformationText2json())

with open("temp_name", "w", encoding="utf-8") as f:
    f.write(json_data["name"].replace(" ", "-"))

with open("temp_json", "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

add_Event(json_data)
