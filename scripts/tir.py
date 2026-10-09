#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tir.py - Time Investment Report / 时间投资评估报告 · 确定性计算器

纯 Python 标准库，无第三方依赖，不联网，不写文件（除 scaffold 输出到 stdout）。
用途：把报告中可计算的格子交给脚本，避免心算错误与数据幻觉。

子命令
------
timeline   沿时间轴的分布分析：加权均分 / 好评区间时长 / 崩点 / 尾部占比
budget     时间账单与净收益测算：日历周期 / 预计完成日期 / 期望节省 / 净收益
scaffold   生成 Markdown 报告骨架

用法
----
    python3 scripts/tir.py timeline --input segments.json
    python3 scripts/tir.py timeline --input segments.json --format json
    python3 scripts/tir.py budget --hours 70.2 --per-week 6
    python3 scripts/tir.py budget --hours 95 --per-week 6 --accuracy 0.8 --worthless-rate 0.5
    python3 scripts/tir.py scaffold --title "Machine Learning Specialization" --type course

timeline 输入 JSON 格式
----------------------
{
  "object": "权力的游戏",
  "scale": 10,                 // 评分区间上限，默认 10
  "good": 7.0,                 // 好评阈值（>= 视为好评区间），默认 7.0
  "bad": 6.0,                  // 低分阈值（< 视为低分区间），默认 6.0
  "segments": [
    {"label": "S1", "minutes": 550, "rating": 9.1, "note": "可选"},
    {"label": "S2", "minutes": 560, "rating": 9.3},
    {"label": "S3", "minutes": 570, "rating": 9.0}
  ]
}

rating 可省略（该段不参与评分计算，但仍计入时长）。
minutes 可为任意正数；若手头只有集数，可用等量估计值并在报告中标注 [推算]。
"""

import argparse
import json
import sys
from datetime import date, timedelta


# --------------------------------------------------------------------------
# 工具
# --------------------------------------------------------------------------

def _fmt_hm(minutes):
    """分钟 -> 小时(一位小数)"""
    return round(minutes / 60.0, 1)


def _weighted_mean(segments):
    """按时长加权的评分均值。无评分段不参与。"""
    num = 0.0
    den = 0.0
    for s in segments:
        r = s.get("rating")
        if r is None:
            continue
        m = float(s.get("minutes", 0) or 0)
        num += float(r) * m
        den += m
    return (num / den) if den else None


# --------------------------------------------------------------------------
# timeline
# --------------------------------------------------------------------------

def cmd_timeline(args):
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    object_name = data.get("object", "(未命名对象)")
    good = float(data.get("good", 7.0))
    bad = float(data.get("bad", 6.0))
    scale = float(data.get("scale", 10))
    segments = data.get("segments", [])

    if not segments:
        print("错误：segments 为空。", file=sys.stderr)
        return 2

    for i, s in enumerate(segments):
        s["_i"] = i
        s.setdefault("label", "段%d" % (i + 1))
        s["minutes"] = float(s.get("minutes", 0) or 0)

    total_minutes = sum(s["minutes"] for s in segments)
    rated = [s for s in segments if s.get("rating") is not None]
    unrated = [s for s in segments if s.get("rating") is None]

    wmean = _weighted_mean(rated)
    pmean = (sum(float(s["rating"]) for s in rated) / len(rated)) if rated else None

    good_min = sum(s["minutes"] for s in rated if float(s["rating"]) >= good)
    bad_min = sum(s["minutes"] for s in rated if float(s["rating"]) < bad)
    mid_min = sum(s["minutes"] for s in rated
                  if bad <= float(s["rating"]) < good)
    unrated_min = sum(s["minutes"] for s in unrated)

    # 崩点：最小的 i，使得从 i 开始的尾部加权均分 < 全局加权均分 - drop，
    #       且尾部时长占比 >= min_tail_share。
    drop = args.drop
    breakpoint_label = None
    breakpoint_index = None
    tail_minutes = 0.0
    tail_mean = None
    if wmean is not None:
        for i in range(len(rated)):
            tail = rated[i:]
            tm = _weighted_mean(tail)
            tmin = sum(s["minutes"] for s in tail)
            if tm is None:
                continue
            if tm < wmean - drop and (tmin / total_minutes) >= args.min_tail_share:
                breakpoint_index = rated[i]["_i"]
                breakpoint_label = rated[i]["label"]
                tail_minutes = tmin
                tail_mean = tm
                break

    result = {
        "object": object_name,
        "scale": scale,
        "thresholds": {"good": good, "bad": bad},
        "total_minutes": round(total_minutes, 1),
        "total_hours": _fmt_hm(total_minutes),
        "weighted_mean_rating": round(wmean, 2) if wmean is not None else None,
        "plain_mean_rating": round(pmean, 2) if pmean is not None else None,
        "mean_gap": (round(wmean - pmean, 2)
                     if (wmean is not None and pmean is not None) else None),
        "good_band": {"minutes": round(good_min, 1),
                      "hours": _fmt_hm(good_min),
                      "share_of_total": round(good_min / total_minutes, 3) if total_minutes else None,
                      "share_of_rated": round(good_min / (good_min + mid_min + bad_min), 3)
                      if (good_min + mid_min + bad_min) else None},
        "mid_band": {"minutes": round(mid_min, 1), "hours": _fmt_hm(mid_min)},
        "bad_band": {"minutes": round(bad_min, 1),
                     "hours": _fmt_hm(bad_min),
                     "share_of_total": round(bad_min / total_minutes, 3) if total_minutes else None},
        "unrated_minutes": round(unrated_min, 1),
        "breakpoint": {
            "segment_index": breakpoint_index,
            "label": breakpoint_label,
            "tail_minutes": round(tail_minutes, 1),
            "tail_hours": _fmt_hm(tail_minutes),
            "tail_share": round(tail_minutes / total_minutes, 3) if total_minutes else None,
            "tail_weighted_mean": round(tail_mean, 2) if tail_mean is not None else None,
            "drop_threshold": drop,
        } if breakpoint_label else None,
    }

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    # Markdown 输出
    print("## 时间轴分布分析 · %s\n" % object_name)
    print("| 指标 | 值 |")
    print("|---|---|")
    print("| 总时长 | %.1f 小时（%d 分钟） |" % (result["total_hours"], round(total_minutes)))
    if wmean is not None:
        print("| 时长加权均分 | %.2f / %.0f |" % (wmean, scale))
    if pmean is not None:
        print("| 算术均分（各段等权） | %.2f / %.0f |" % (pmean, scale))
    if result["mean_gap"] is not None:
        print("| 两种均分差值 | %+.2f |" % result["mean_gap"])
    print("| 好评区间（>= %.1f） | %.1f 小时，占总量 %.1f%% |"
          % (good, result["good_band"]["hours"],
             (result["good_band"]["share_of_total"] or 0) * 100))
    print("| 中间区间 | %.1f 小时 |" % result["mid_band"]["hours"])
    print("| 低分区间（< %.1f） | %.1f 小时，占总量 %.1f%% |"
          % (bad, result["bad_band"]["hours"],
             (result["bad_band"]["share_of_total"] or 0) * 100))
    if unrated_min:
        print("| 无评分段 | %.1f 小时（未参与评分计算） |" % _fmt_hm(unrated_min))

    if rated:
        lo = min(rated, key=lambda s: float(s["rating"]))
        print("")
        print("**最低分段**：「%s」，评分 %.1f，时长 %.1f 小时。"
              % (lo["label"], float(lo["rating"]), _fmt_hm(lo["minutes"])))

    bp = result["breakpoint"]
    print("")
    if bp:
        print("**崩点**：第 %d 段「%s」起，其后 %.1f 小时（占总量 %.1f%%）的加权均分跌至 %.2f，"
              "低于全局加权均分 %.2f 超过 %.1f 分。"
              % (bp["segment_index"] + 1, bp["label"], bp["tail_hours"],
                 bp["tail_share"] * 100, bp["tail_weighted_mean"],
                 wmean, drop))
    else:
        print("**崩点**：未检测到持续下跌段（阈值：尾部均分低于全局 %.1f 分且尾部占比 >= %.0f%%）。"
              % (drop, args.min_tail_share * 100))

    if wmean is not None and pmean is not None and abs(wmean - pmean) >= 0.3:
        print("")
        print("> 注意：加权均分与算术均分相差 %.2f 分，说明**各段时长不均**。"
              "报算术均分会误导，报告中必须使用加权值。" % abs(wmean - pmean))

    if unrated:
        print("")
        print("> 有 %d 段缺少评分（%.1f 小时），已在表中单列，未参与均分计算。"
              % (len(unrated), _fmt_hm(unrated_min)))
    return 0


# --------------------------------------------------------------------------
# budget
# --------------------------------------------------------------------------

def cmd_budget(args):
    hours = float(args.hours)
    per_week = float(args.per_week)
    if hours <= 0 or per_week <= 0:
        print("错误：--hours 与 --per-week 必须为正数。", file=sys.stderr)
        return 2

    total_minutes = hours * 60.0
    weeks = hours / per_week
    finish = date.today() + timedelta(weeks=weeks)

    # 净收益模型：期望节省 = 准确率 x 命中率(内容确属低价值的先验) x 全量时长 - 看提示的耗时
    accuracy = float(args.accuracy)
    worthless_rate = float(args.worthless_rate)
    cost_min = float(args.cost_minutes)

    expected_saved = accuracy * worthless_rate * total_minutes
    net_minutes = expected_saved - cost_min

    # 对照：同样方法用于一条 1 分钟短视频
    cmp_total = float(args.compare_minutes)
    cmp_saved = accuracy * worthless_rate * cmp_total
    cmp_net = cmp_saved - cost_min

    result = {
        "total_hours": round(hours, 1),
        "hours_per_week": per_week,
        "weeks_needed": round(weeks, 1),
        "estimated_finish_date": finish.isoformat(),
        "model": {
            "accuracy": accuracy,
            "worthless_rate": worthless_rate,
            "cost_minutes": cost_min,
            "expected_saved_minutes": round(expected_saved, 1),
            "net_minutes": round(net_minutes, 1),
            "net_hours": round(net_minutes / 60.0, 2),
        },
        "comparison_1min_content": {
            "net_minutes": round(cmp_net, 1),
        },
    }

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print("## 时间账单\n")
    print("| 指标 | 值 |")
    print("|---|---|")
    print("| 内容总时长 | %.1f 小时 |" % hours)
    print("| 你的节奏 | 每周 %.1f 小时 |" % per_week)
    print("| 需要的周数 | %.1f 周 |" % weeks)
    print("| 按今天起算的完成日 | %s |" % finish.isoformat())
    print("")
    print("## 评估净收益（模型）\n")
    print("假设：评估准确率 %.0f%%，内容确属低价值的先验概率 %.0f%%，阅读评估耗时 %d 分钟。"
          % (accuracy * 100, worthless_rate * 100, round(cost_min)))
    print("")
    print("| 项 | 值 |")
    print("|---|---|")
    print("| 期望节省 | %.0f 分钟 |" % expected_saved)
    print("| 减去评估耗时 | -%d 分钟 |" % round(cost_min))
    print("| **净收益** | **%.0f 分钟（%.1f 小时）** |" % (net_minutes, net_minutes / 60.0))
    print("| 对照：%.0f 分钟短内容的净收益 | %.1f 分钟 |" % (cmp_total, cmp_net))
    print("")

    if hours < 10:
        print("> **判定：不建议出报告。** 该对象不足 10 小时，净收益相对评估成本过小，"
              "用户自行试错（划走 / 跳读）更高效。")
    elif net_minutes < 30:
        print("> **判定：收益偏低。** 净收益不足 30 分钟，需确认用户的真实投入规模是否更大"
              "（例如含作业、复盘、二刷）。")
    else:
        if cmp_net > 0:
            print("> **判定：适合出报告。** 净收益 %.0f 分钟，约为对照短内容场景的 %.0f 倍。"
                  % (net_minutes, net_minutes / cmp_net))
        else:
            print("> **判定：适合出报告。** 净收益 %.0f 分钟；而对照的 %.0f 分钟短内容净收益为负"
                  "（%.1f 分钟），两者不在同一量级。"
                  % (net_minutes, cmp_total, cmp_net))
    return 0


# --------------------------------------------------------------------------
# scaffold
# --------------------------------------------------------------------------

TYPE_HINTS = {
    "course": {
        "zh": "课程",
        "unit": "周 / 模块",
        "extra": [
            "- 视频时长只占总投入的多大比例？（作业、实验、Quiz 分别多少小时）",
            "- 大纲最后一次更新是哪一年？是否覆盖用户目标所需的技术栈？",
            "- 是否存在公认较弱的一门课？（多个第三方评测交叉验证）",
        ],
    },
    "series": {
        "zh": "剧集",
        "unit": "季 / 集",
        "extra": [
            "- 各季单集评分沿时间的分布（必须看分布，不看全剧均分）",
            "- 崩塌精确到第几集：定位评分持续下跌的起始段",
            "- 注意峰终效应：结局占比虽小，但支配整体回报，必须单独提示",
        ],
    },
    "book": {
        "zh": "书籍",
        "unit": "篇章",
        "extra": [
            "- 作者本人是否发布过更短的免费原版？（PDF / 长文 / 演讲）——最高价值的发现",
            "- 成书篇幅是原版的几倍？超出部分是什么（案例 / 自传 / 展开论证）？",
            "- 核心规则是否可在 10 页内穷举？",
        ],
    },
    "report": {
        "zh": "研究报告",
        "unit": "章节",
        "extra": [
            "- 一手信源占比多少？有多少是公开数据的重新包装？",
            "- 数据截点距今多久？结论是否已过期？",
            "- 执行摘要是否已覆盖全文结论？",
        ],
    },
    "podcast": {
        "zh": "播客系列",
        "unit": "期",
        "extra": [
            "- 单期平均时长与总期数",
            "- 是否有文字稿？（文字稿的阅读速度通常是音频的 3-4 倍）",
            "- 嘉宾重复度与话题重复度",
        ],
    },
    "community": {
        "zh": "付费社群",
        "unit": "月 / 主题",
        "extra": [
            "- 历史内容沉淀量 vs 每年新增量",
            "- 活跃度衰减：近 3 个月的发言密度对比首月",
            "- 退费条款与内容导出权",
        ],
    },
}


def cmd_scaffold(args):
    t = TYPE_HINTS.get(args.type, TYPE_HINTS["book"])
    lines = []
    lines.append("# 时间投资评估报告 · %s\n" % args.title)
    lines.append("> 类型：%s ｜ 拆分单位：%s ｜ 生成日期：%s\n"
                 % (t["zh"], t["unit"], date.today().isoformat()))
    lines.append("> **本报告不给「值不值得」打分。** 只呈现可核验的结构事实与置信度，判断权在你。\n")

    lines.append("\n## 0 · 基础账\n")
    lines.append("| 项 | 值 | 来源 | 置信度 |")
    lines.append("|---|---|---|---|")
    lines.append("| 对象全名（含版本） | %s |  | [官方] |" % args.title)
    lines.append("| 总篇幅 / 总时长 |  |  |  |")
    lines.append("| 价格 |  |  |  |")
    lines.append("| 评分与评价人数 |  |  | [聚合] |")
    lines.append("| 最近更新时间 |  |  | [官方] |")

    lines.append("\n## 1 · 时间账单\n")
    lines.append("| 项 | 值 |")
    lines.append("|---|---|")
    lines.append("| 纯内容时长 | 小时 |")
    lines.append("| 含作业 / 练习的总投入 | 小时 |")
    lines.append("| 你的每周节奏 | 小时/周 |")
    lines.append("| 需要的周数 | 周 |")
    lines.append("| 预计完成日 |  |")

    lines.append("\n## 2 · 结构拆解（按%s）\n" % t["unit"])
    lines.append("| 段落 | 时长 / 篇幅 | 占比 | 评分（若有） | 说明 |")
    lines.append("|---|---|---|---|---|")
    lines.append("|  |  |  |  |  |")

    lines.append("\n## 3 · 密度异常点\n")
    lines.append("- **铺垫段**：")
    lines.append("- **崩塌点**（精确到具体段落）：")
    lines.append("- **注水段 / 公认短板**：")
    lines.append("")
    for h in t["extra"]:
        lines.append(h)

    lines.append("\n## 4 · 时效折损\n")
    lines.append("| 项 | 值 |")
    lines.append("|---|---|")
    lines.append("| 最近一次更新距今 |  |")
    lines.append("| 缺失的关键内容 |  |")
    lines.append("| 对用户目标的影响 |  |")

    lines.append("\n## 5 · 更短的替代来源\n")
    lines.append("| 替代源 | 篇幅 | 覆盖率 | 成本 | 链接 |")
    lines.append("|---|---|---|---|---|")
    lines.append("|  |  |  |  |  |")

    lines.append("\n## 6 · 你的三个选项（我们不替你选）\n")
    lines.append("### 选项 A · 全量投入")
    lines.append("- 投入： 小时")
    lines.append("- 适合：")
    lines.append("")
    lines.append("### 选项 B · 只取核心段")
    lines.append("- 投入： 小时（省下 小时）")
    lines.append("- 具体取舍：")
    lines.append("")
    lines.append("### 选项 C · 放弃")
    lines.append("- 省下： 小时")
    lines.append("- 改用：")

    lines.append("\n---\n")
    lines.append("## 数据来源与置信度\n")
    lines.append("- `[官方]` 来自出品方 / 平台官方页面")
    lines.append("- `[聚合]` 来自公开评价聚合，需注明样本规模")
    lines.append("- `[推算]` 由上述数据计算得出，附算式")
    lines.append("- `[未验证]` 未取得证据，已明确标注")
    lines.append("")
    lines.append("## 诚实声明\n")
    lines.append("本报告基于公开可核验的元数据与公开评价聚合生成，"
                 "报告作者对内容的实际接触程度为：____（如实填写，例如「未观看全部集数」）。")

    print("\n".join(lines))
    return 0


# --------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        prog="tir.py",
        description="时间投资评估报告 · 确定性计算器（纯标准库）")
    sub = p.add_subparsers(dest="cmd", required=True)

    tl = sub.add_parser("timeline", help="沿时间轴的分布分析")
    tl.add_argument("--input", required=True, help="segments JSON 文件路径")
    tl.add_argument("--format", choices=["md", "json"], default="md")
    tl.add_argument("--drop", type=float, default=1.0,
                    help="崩点判定：尾部均分低于全局均分多少分（默认 1.0）")
    tl.add_argument("--min-tail-share", type=float, default=0.05,
                    help="崩点判定：尾部时长最小占比（默认 0.05）")
    tl.set_defaults(func=cmd_timeline)

    bd = sub.add_parser("budget", help="时间账单与净收益测算")
    bd.add_argument("--hours", type=float, required=True, help="内容总小时数")
    bd.add_argument("--per-week", type=float, required=True, help="每周可投入小时数")
    bd.add_argument("--accuracy", type=float, default=0.8, help="评估准确率（默认 0.8）")
    bd.add_argument("--worthless-rate", type=float, default=0.5,
                    help="内容确属低价值的先验概率（默认 0.5）")
    bd.add_argument("--cost-minutes", type=float, default=10.0,
                    help="阅读评估所需分钟数（默认 10）")
    bd.add_argument("--compare-minutes", type=float, default=1.0,
                    help="对照内容的分钟数（默认 1，即一条短视频）")
    bd.add_argument("--format", choices=["md", "json"], default="md")
    bd.set_defaults(func=cmd_budget)

    sc = sub.add_parser("scaffold", help="生成 Markdown 报告骨架")
    sc.add_argument("--title", required=True, help="对象全名")
    sc.add_argument("--type", default="book",
                    choices=sorted(TYPE_HINTS.keys()), help="内容类型（默认 book）")
    sc.set_defaults(func=cmd_scaffold)

    args = p.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
