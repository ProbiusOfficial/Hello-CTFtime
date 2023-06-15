## CTFevent

~~(emm，本人的python爬虫实训的大作业x)~~

聚合国内外赛事的API，基于 云函数 Serverless ，结合爬虫技术，返回json格式的数据包，方便进一步利用。

注意，目前的版本路由数据 可能不适合您直接访问 它更倾向于对接bot，不用担心，我很快会进行下一次更新。

### 国外赛事

```json
" API地址 " : "http://event.ctf.probius.xyz/global_CTF"
" 调用方法 " :"/GET"
" 返回格式 " :"json"
[
    {
        "比赛名称": "BSides Indore CTF 2023 (http://ctf.bsidesindore.in/)",
        "比赛时间": "2023-06-17 01:30:00 - 2023-06-18 01:30:00 UTC+8",
        "添加日历": "https://ctftime.org/event/2017.ics",
        "比赛形式": "Jeopardy",
        "比赛链接": "http://ctf.bsidesindore.in/",
        "比赛标志": "https://ctftime.org/media/events/Red_Black_Logo_Transparent.png",
        "比赛权重": "0.00",
        "赛事主办": "BSides Indore (https://ctftime.org/team/227864)"
    },
    {
        "比赛名称": "Codegate CTF 2023 Preliminary (https://codegate2023.org/)",
        "比赛时间": "2023-06-17 09:00:00 - 2023-06-18 09:00:00 UTC+8",
        "添加日历": "https://ctftime.org/event/2006.ics",
        "比赛形式": "Jeopardy",
        "比赛链接": "https://codegate2023.org/",
        "比赛标志": "https://ctftime.org",
        "比赛权重": "25.00",
        "赛事主办": "CODEGATE (https://ctftime.org/team/39352)"
    },
    {},
    {},
    ...
]
```

![image-20230616002335288](https://nssctf.wdf.ink//img/WDTJ/202306160023392.png)

### 国内赛事

```json
" API地址 " : "http://event.ctf.probius.xyz/cn_CTF"
" 调用方法 " :"/GET"
" 返回格式 " :"json"
[
    {
        "比赛名称": "2023XCTF分站赛-SCTF",
        "比赛链接": "https://sctf2023.xctf.org.cn",
        "比赛类型": "团队赛",
        "报名开始": "无需报名",
        "报名截止": "无需报名",
        "比赛开始": "2023年06月17日09:00",
        "比赛结束": "2023年06月19日09:00",
        "其他说明": "QQ群：729402738"
    },
    {},
    {},
    ...
]
```

![image-20230616002421813](https://nssctf.wdf.ink//img/WDTJ/202306160024937.png)

### 部署

该代码部署环境为 python 3.7 基于 Web型云函数

![image-20230616003550725](https://nssctf.wdf.ink//img/WDTJ/202306160035810.png)

您可以下载代码包 直接上传部署

也可以只编辑 app.py 自行添加依赖部署：

requirements.txt:

```
Flask==1.0.2
werkzeug==0.16.0
requests==2.27.1
beautifulsoup4==4.10.0
```

注意在云函数上部署时 注意目录层级 以及 您需要先在终端本地化依赖环境后再上传：

```
cd /src
pip install -r requirements.txt -t .
```

### 代码逻辑

- 主程序为 app.py
- cn_CTF_Crawler.py 为 /cn_CTF 路由的核心代码
- CTFtime_Crawler.py 为 /global_CTF 路由的核心代码

源码中已给出注释。
