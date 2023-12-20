## 关于

本项目为 [Hello-CTF](https://github.com/ProbiusOfficial/Hello-CTF) 的关联项目，基于 GitHub Action 自动化更新赛事信息。  

## 数据来源

国内赛事数据来源于 三哈 - https://su-sanha.cn/events

国外赛事数据来源于 CTFtime RSS源 - https://ctftime.org

```
具体URL如下：
cn_ctf_url = 'https://www.su-sanha.cn:443/api/events/list'
rssUpcoming = 'https://ctftime.org/event/list/upcoming/rss/'
rssActive = 'https://ctftime.org/event/list/archive/rss/'
rssNowrunning = 'https://ctftime.org/event/list/running/rss/'
```

## 数据格式

所有的比赛信息均以 json 格式呈现，您可以通过下面的链接直接获取json数据：

国内赛事:https://raw.githubusercontent.com/ProbiusOfficial/Hello-CTFtime/main/CN.json

国外赛事:https://raw.githubusercontent.com/ProbiusOfficial/Hello-CTFtime/main/Global.json

## 同步原理

使用 GitHub Action 定时执行脚本，先 fetch 获取最新的比赛状态，再将 json 转化为 markdown 格式，存储到 Out 中。

`cron: '0 */8 * * *'` —— 每8小时执行一次
## CN.json 数据说明
```
"status": 0 # 报名未开始
"status": 1 # 报名进行中
"status": 2 # 报名已结束

"status": 3 # 比赛进行中

"status": 4 # 比赛已结束
```

## TODO

Archive
