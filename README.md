## 关于

本项目为 [Hello-CTF](https://github.com/ProbiusOfficial/Hello-CTF) 的关联项目，这是一个基于 Issue模板 + GitHub Action 实现的自动化赛事信息更新。  

如需查看赛事信息，请前往：[https://hello-ctf.com/Event/](https://hello-ctf.com/Event/)

## 数据来源

国外赛事数据来源于 CTFtime RSS源 - https://ctftime.org

国内赛事由本项目收集维护，如需要添加赛事信息，请选择Issue中的[添加比赛模板](https://github.com/ProbiusOfficial/Hello-CTFtime/issues/new/choose).

如有疑问，请开空白issue，或者在 [赛事群](https://qm.qq.com/q/HxicU7ee2e) 中联系本人或者三哈.

> [!IMPORTANT]
> **我们很支持您将本项目的数据共享给他人，这样能极大的促进CTF社区的发展，但同时我们也希望您注明数据来源。**
>
> 如果您引用了该项目的数据，请尽量标注:
>
> [**数据来源：[Hello-CTFTime](https://github.com/ProbiusOfficial/Hello-CTFtime)**] 或者 [**数据来源：[Hello-CTF](https://github.com/ProbiusOfficial/Hello-CTF)**]

## 日历订阅

自动化程序提供适用于 RFC 5545 标准的日历订阅链接，您可以通过下面的链接获取订阅文件：

国内赛事：https://raw.githubusercontent.com/ProbiusOfficial/Hello-CTFtime/main/calendar/CN.ics

国外赛事：https://raw.githubusercontent.com/ProbiusOfficial/Hello-CTFtime/main/calendar/Global.ics

参考：

[在 Outlook.com 或 Outlook 网页版中导入或订阅日历](https://support.microsoft.com/zh-cn/office/%E5%9C%A8-outlook-com-%E6%88%96-outlook-%E7%BD%91%E9%A1%B5%E7%89%88%E4%B8%AD%E5%AF%BC%E5%85%A5%E6%88%96%E8%AE%A2%E9%98%85%E6%97%A5%E5%8E%86-cff1429c-5af6-41ec-a5b4-74f2c278e98c)

[订阅其他人的 Google 日历 - 使用链接添加公开日历](https://support.google.com/calendar/answer/37100?hl=zh-Hans&ref_topic=10510447&sjid=13834461551378859207-AP)

## 获取数据

> [!WARNING]
> 在某些情况下，通过Github直链获取json的方法可能会因为网络原因失效，在此情况下，我们提供国内Gitee的仓库镜像来解决该问题：
>
> 国内赛事：https://gitee.com/Probius/Hello-CTFtime/raw/main/CN.json
>
> 国外赛事：https://gitee.com/Probius/Hello-CTFtime/raw/main/Global.json
>
> （若上述链接失效，可能因为赛事名字触发河蟹审查，请使用`.b64`版本：CN.b64 / Global.b64）

所有的比赛信息均以 json 格式呈现，您可以通过下面的链接直接获取json数据：

国内赛事:https://raw.githubusercontent.com/ProbiusOfficial/Hello-CTFtime/main/CN.json

国外赛事:https://raw.githubusercontent.com/ProbiusOfficial/Hello-CTFtime/main/Global.json

```
状态说明:
"status": 0 # 报名未开始
"status": 1 # 报名进行中
"status": 2 # 报名已结束
"status": 3 # 比赛进行中
"status": 4 # 比赛已结束
```

## 自动化流程

国外赛事每小时自动更新.

国内赛事：提交Issue → Bot提交Pr审核 → 管理员审核通过添加.

每小时根据 UTC+8 时间更新国内比赛状态.

国内超过60天的比赛会被归档在 /Achieve/CN_CTF.json 中.

## TODO

暂无，期待issue.
