import sys
import json
import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI

apikey = sys.argv[1]

client = OpenAI(
    api_key=apikey,
    base_url="https://api.moonshot.cn/v1",
)
 
system_prompt = """
你是一个 CTF 比赛信息抽取助手。你的任务：从用户给定的原始文本中抽取比赛信息，并输出**严格符合 JSON 语法**的一个对象（只能输出 JSON，不要输出任何解释、注释、Markdown）。

要求与约束（非常重要）：
1) 只输出一个 JSON 对象，不能包含注释、不能包含多余字段、不能包含尾随逗号。
2) 字段名必须与下面模板完全一致，大小写一致。
3) 时间一律使用北京时间（Asia/Shanghai）。
4) 时间格式必须是："YYYY年MM月DD日 HH:MM"（24小时制，补零）。
5) 缺失值使用 JSON 的 null（小写），不要使用字符串 "NULL"。
6) `info_confirmed` 只有在**同时**抽取到 `comp_time_start`、`comp_time_end`、`link` 三者时才为 1，否则为 0。
7) `status` 只能是以下四种之一："即将开始"、"正在进行"、"已经结束"、"未确定"。
8) `limit`：个人赛填 1；团队赛尽量填最大队伍人数；未提及则填 0。必须是数字（JSON number）。
9) `type`：默认"线上Jeopardy解题赛"；若有明显 AWD/攻防/对抗字样则填"AWD对抗赛"；若明确线下则在前面加"线下"（如"线下Jeopardy解题赛"）。
10) `tag` 只能是："普通赛"、"公益赛"、"行业赛" 之一；无法判断填空字符串""。
11) `readmore`：用一句话组合（主办方信息 + 沟通群组 + 其他补充信息）。缺哪个就省略哪个部分。

当前北京时间：{NOW_CN}

请按如下 JSON 模板输出（注意：下面是字段说明，不是可输出的注释；你的最终输出必须是纯 JSON）：
{
  "name": "比赛名称",
  "info_confirmed": 0,
  "mid_join": null,
  "link": "",
  "status": "未确定",
  "is_reg": null,
  "limit": 0,
  "type": "线上Jeopardy解题赛",
  "reg_time_start": "",
  "reg_time_end": "",
  "comp_time_start": "",
  "comp_time_end": "",
  "organizer": "",
  "contac": {
    "QQ群": ""
  },
  "tag": "",
  "readmore": ""
}

字段填充规则（用于你推断/补全）：
- name：优先英文名称（例如 XXXCTF 2026）；若全文只有中文就用中文。
- mid_join：若明确说明“比赛中可报名/可随时加入”则为 1；若明确“必须赛前报名/报名截止后不能参加”则为 0；否则 null。
- link：优先提取比赛主页/报名页面/官方公告链接（URL）。
- is_reg：如果存在报名时间区间，并且当前时间在报名区间内则为 1；如果明确报名已结束则为 0；否则 null。
- reg_time_start：若未给出报名开始时间，则用当前北京时间代替。
- reg_time_end：若未给出报名结束时间，则用比赛开始时间减 1 分钟；若连比赛开始也没有，则用当前北京时间加 7 天代替。
- comp_time_start/comp_time_end：尽量从文本中提取；若只给日期无具体时间，默认开始 09:00，结束 21:00；若跨天请正确处理。
- organizer：提取主办/承办/协办等单位。
- contac：提取用于沟通的群组/渠道：QQ群号、Discord、Telegram、微信群等；只要发现就加入对象中，键名用渠道名（例如"Discord"），没有则只保留QQ群空值。
"""

with open("temp", "r", encoding="utf-8") as f:
    issue_body = f.read()

matchInformationText = issue_body

now_cn = datetime.datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y年%m月%d日 %H:%M")
system_prompt_rendered = system_prompt.format(NOW_CN=now_cn)

def matchInformationText2json():
    try:
        completion = client.chat.completions.create(
            model="kimi-k2-0905-preview",
            messages=[
                {"role": "system", "content": system_prompt_rendered},
                {"role": "user", "content": matchInformationText},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        # Fail fast with a clear message
        raise RuntimeError(f"LLM request failed: {e}")

    content = completion.choices[0].message.content
    print(content)
    return content

def add_Event(json_data):

    with open('./CN.json', 'r', encoding='utf-8') as f:
        CN = json.load(f)

    # Ensure structure exists
    CN.setdefault('data', {})
    CN['data'].setdefault('result', [])

    if CN['data']['result']:
        print("Now:" + str(CN['data']['result'][0]))
    else:
        print("Now: CN.json result list is empty")

    print("Insert " + str(json_data) + " into CN.json")

    # De-duplicate by link if possible
    link = json_data.get('link')
    if link:
        CN['data']['result'] = [x for x in CN['data']['result'] if not (isinstance(x, dict) and x.get('link') == link)]

    CN['data']['result'].insert(0, json_data)

    print("After insert:" + str(CN['data']['result'][0]))

    with open('./CN.json', 'w', encoding='utf-8') as f:
        json.dump(CN, f, ensure_ascii=False, indent=4)
    
    print("Insert Done")

json_data = json.loads(matchInformationText2json())

# --- normalize / guardrails ---
if "contac" in json_data and "contact" not in json_data:
    json_data["contact"] = json_data.pop("contac")

# Ensure contact is an object
if not isinstance(json_data.get("contact"), dict):
    json_data["contact"] = {"QQ群": ""}
else:
    json_data["contact"].setdefault("QQ群", "")

# Ensure limit is a number
try:
    json_data["limit"] = int(json_data.get("limit", 0))
except Exception:
    json_data["limit"] = 0

# Clamp status to allowed set
allowed_status = {"即将开始", "正在进行", "已经结束", "未确定"}
if json_data.get("status") not in allowed_status:
    json_data["status"] = "未确定"

# info_confirmed must be consistent with required fields
required = ["comp_time_start", "comp_time_end", "link"]
if all(json_data.get(k) for k in required):
    json_data["info_confirmed"] = 1
else:
    json_data["info_confirmed"] = 0

safe_name = str(json_data.get("name", "event")).strip()
safe_name = safe_name.replace(" ", "-")
safe_name = "".join(ch for ch in safe_name if ch.isalnum() or ch in "-_")
if not safe_name:
    safe_name = "event"
with open("temp_name", "w", encoding="utf-8") as f:
    f.write(safe_name)

with open("temp_json", "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

add_Event(json_data)
