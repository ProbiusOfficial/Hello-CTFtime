import re
import sys
import json
import datetime
from openai import OpenAI

apikey = sys.argv[1]

client = OpenAI(
    api_key=apikey,
    base_url="https://api.moonshot.cn/v1",
)
 
system_prompt = """
你是一个CTF比赛信息助手，负责从给定的文本中提取结构化信息。请根据以下指南确保一致性和准确性。
 
请使用如下 JSON 格式输出你的回复：
 
{
  "name": "比赛名称", //比赛名称 优先使用英文名称 如 XXXCTF 2024 XXXGAME 2024 如果没有类似的结构 则使用中文
  "info_confirmed" : 1,//当能够匹配到比赛开始时间和结束时间以及比赛链接时设置为1，否则设置为0
  "mid_join" : 1,//是否可中途加入(比赛中报名) 1为可以 0为不可以 无法提取时设置为空NULL
  "link": "URL",//比赛的url地址
  "status": "",  // "即将开始"：比赛时间在当前时间之后；"正在进行":当前时间在比赛区间内 "已经结束" :当前时间在比赛结束日期后；如果不能够匹配到比赛开始时间和结束时间以及比赛链接，则标记为"未确定"
  "is_reg": 1, // /是否可报名，依据比赛信息中是否有报名时间和比赛开始时间比较，1 为可报名，0 为不可报名，当无法确定是为NULL
  "limit": "1", //人数限制 个人赛为 1 团队赛 请尝试提取团队人数 若没有要求则为 0
  "type": "线上或线下Jeopardy解题赛 或者 AWD对抗赛",大多数情况下默认为线上Jeopardy解题赛 除非有明显的AWD字样
  "reg_time_start" : "yyyy年mm月dd日 hh:mm", 报名开始时间 yyyy年mm月dd日 hh:mm 如果没有匹配到具体时间，则用当前时间代替
  "reg_time_end" : "yyyy年mm月dd日 hh:mm", 报名结束时间 yyyy年mm月dd日 hh:mm 如果没有匹配到具体时间，则用比赛开始时间-1分钟替代
  "comp_time_start" : "yyyy年mm月dd日 hh:mm", 比赛开始时间 yyyy年mm月dd日 hh:mm
  "comp_time_end" : "yyyy年mm月dd日 hh:mm", 比赛结束时间 yyyy年mm月dd日 hh:mm
  "organizer":"主办方信息",
  "contac": { //联系方式或者比赛群组，用于选手沟通的群聊， 如QQ群 Discord群组等
    "QQ群": "123456789", // 默认提取QQ群号码
    "其他联系方式(自定义字段名)": "自定义值" // 如果有其他联系方式，请提取并填写
  }, 
  "tag":"",//普通赛-办赛单位有政府机构的参与且对参赛人员无特殊要求的比赛； 公益赛-安全相关的社群组织/高校学校社团等自发组织的比赛； 行业赛-由行业或者政府相关机构发起（如金融 能源 民航等）且参赛人员有特定性的比赛
  "readmore": "其他补充信息" //由主办方信息 + 选手沟通群聊 + 其他补充信息 组成的合理语句
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
            {"role": "user", "content": matchInformationText}
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    print(completion.choices[0].message.content)
    json_content = completion.choices[0].message.content

    return json_content

def add_Event(json_data):

    with open('./CN.json', 'r', encoding='utf-8') as f:
        CN = json.load(f)
    
    if CN['data']['result']:
        print("Now:" + str(CN['data']['result'][0]))
    else:
        print("Now: CN.json result list is empty")

    print("Insert " + str(json_data) + " into CN.json")
    
    CN['data']['result'].insert(0, json_data)

    print("After insert:" + str(CN['data']['result'][0]))

    with open('./CN.json', 'w', encoding='utf-8') as f:
        json.dump(CN, f, ensure_ascii=False, indent=4)
    
    print("Insert Done")

json_data = json.loads(matchInformationText2json())

with open("temp_name", "w", encoding="utf-8") as f:
    f.write(json_data['name'].replace(" ","-"))

with open("temp_json", "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

add_Event(json_data)




