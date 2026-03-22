# 国内赛事 `CN.json` 变更说明（关联项目同步用）

本文档供 **Hello-CTFtime** 以外的关联仓库（如消费 `CN.json`、展示国内赛事、或复用同一数据结构的项目）对照修改。

---

## 1. 变更摘要

| 项目 | 说明 |
|------|------|
| 目的 | 国内赛事每条记录只保留「名称、链接、比赛起止时间、详细说明」五类信息，简化维护与 LLM 提取。 |
| 破坏性 | **是**。若下游仍读取已删除字段（如 `status`、`reg_time_*`、`readmore`、`type` 等），需改造。 |
| `status` | **不再写入** `CN.json`。展示「即将开始 / 正在进行 / 已经结束」时须用 **比赛时间与当前 UTC+8** 自行推导（见 §3）。 |
| 兼容 | 展示文案里原「其他说明」对应字段由 `readmore` 改为 **`detail`**；若需兼容旧数据，可读 `detail`，缺失时回退 `readmore`。 |

---

## 2. 数据结构（`CN.json`）

外层结构未变：

```json
{
  "success": true,
  "data": {
    "result": [ /* 比赛对象数组 */ ],
    "total": 0,
    "page": 1,
    "size": 20
  },
  "msg": ""
}
```

### 2.1 单条比赛对象（新）

仅包含以下键：

| 键 | 类型 | 说明 |
|----|------|------|
| `name` | string | 比赛名称 |
| `link` | string | 比赛地址（官网/报名页 URL） |
| `comp_time_start` | string | 比赛开始时间 |
| `comp_time_end` | string | 比赛结束时间 |
| `detail` | string | 比赛详细说明（原多字段合并后的长文本） |

时间格式（须与解析逻辑一致）：

```text
yyyy年mm月dd日 hh:mm
```

示例：`2024年10月12日 12:00`（月、日建议两位补零，与上游校验一致。）

### 2.2 已废弃字段（勿再依赖）

以下字段在 **Hello-CTFtime 当前 `CN.json` 中已不再出现**，关联项目应删除或改写相关逻辑：

- `status`（及历史上的数值型状态如 `3`、`4`）
- `info_confirmed`、`mid_join`、`is_reg`、`limit`
- `type`
- `reg_time_start`、`reg_time_end`
- `organizer`、`contac`、`tag`
- `readmore`（由 `detail` 替代；仅存档或旧快照中可能仍存在）

---

## 3. 状态推导（替代 `status`）

使用 **当前 UTC+8 时间** `now` 与 `comp_time_start`、`comp_time_end` 比较：

1. `now < comp_time_start` → **即将开始**
2. `comp_time_start <= now < comp_time_end` → **正在进行**
3. `now >= comp_time_end` → **已经结束**

参考实现（与本仓库 `cn_helpers.py` 一致）：

- `utc8_now()`：`datetime.now() + timedelta(hours=8)`
- `parse_cn_time(s)`：`datetime.strptime(s.strip(), "%Y年%m月%d日 %H:%M")`
- 按上列三条分支返回中文状态字符串

归档策略（若关联项目也有「超过 N 天移入存档」）：仅依据 **`comp_time_end`**，不再依赖 `status`。

---

## 4. Hello-CTFtime 侧已改动的文件（便于对照）

| 文件 | 变更要点 |
|------|----------|
| `cn_helpers.py` | **新建**：时间解析、`utc8_now`、`cn_derived_status`。 |
| `issue2Event.py` | LLM 只输出五字段；插入后更新 `data.total`。 |
| `json_to_md.py` | 国内分区用推导状态；模板展示 `detail`；`detail` 缺省时回退 `readmore`。 |
| `update.py` | 不再写 `status`；归档按结束时间 +60 天；排序用推导状态 + `comp_time_start`；`CN.ics` 描述用 `link` + `detail`。 |
| `CN.json` | 数据已迁移为新五字段。 |
| `.github/ISSUE_TEMPLATE/add-eventInfo.yml` | Issue 说明与占位文案更新。 |

---

## 5. 关联项目建议改造清单

1. **解析层**：国内赛事条目只校验 `name`、`link`、`comp_time_start`、`comp_time_end`、`detail`。
2. **展示层**：凡使用 `readmore` 处改为 `detail`（可选：`detail || readmore` 过渡）。
3. **状态/筛选**：删除对 `event.status` 的读取，改为 §3 的推导函数。
4. **报名相关 UI**：若曾依赖 `reg_time_*` / `is_reg`，需改为仅从 `detail` 文案展示或移除该功能。
5. **日历 / ICS**：若自建日历，描述字段以 `detail` 为准（本仓库 `DESCRIPTION` 为 `link` + 去空白后的 `detail`）。
6. **测试数据**：用一条完整五字段 JSON 做回归测试。

---

## 6. 示例（单条 `result` 元素）

```json
{
  "name": "示例赛 2025",
  "link": "https://example.com/ctf",
  "comp_time_start": "2025年06月01日 09:00",
  "comp_time_end": "2025年06月02日 18:00",
  "detail": "线上个人赛。报名见官网。QQ群：123456789。"
}
```

---

## 7. 数据获取方式（未变）

若关联项目通过 Raw URL 拉取 `CN.json`，地址仍以 **Hello-CTFtime 仓库发布路径** 为准（如 GitHub Raw / Gitee 镜像），仅 **内容结构** 按本文档升级。

---

*文档版本：与 Hello-CTFtime「国内赛事五字段」重构同期；后续若再改 schema，请同步更新本文件。*
