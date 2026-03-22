"""国内赛事 CN.json：时间与状态推导（不写回 status 字段时由时间计算）。"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

CN_TIME_FMT = "%Y年%m月%d日 %H:%M"


def utc8_now() -> datetime:
    return datetime.now() + timedelta(hours=8)


def parse_cn_time(s: str) -> datetime:
    return datetime.strptime(s.strip(), CN_TIME_FMT)


def cn_derived_status(event: dict, now: Optional[datetime] = None) -> str:
    """根据比赛起止时间与当前 UTC+8 时间推导：即将开始 / 正在进行 / 已经结束。"""
    now = now or utc8_now()
    start = parse_cn_time(event["comp_time_start"])
    end = parse_cn_time(event["comp_time_end"])
    if now < start:
        return "即将开始"
    if now < end:
        return "正在进行"
    return "已经结束"
