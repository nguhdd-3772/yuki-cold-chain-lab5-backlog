"""Quy tắc ra giờ dùng chung cho mọi script LAB-5 (một nguồn, không lặp công thức).

Giờ issue lá:
  - kind coarse  : tổng MD LAB-1 × md_hours (chưa có spec, giữ nguyên LAB-1)
  - hours_override: giờ chốt tay (phải có override_why)
  - còn lại      : ceil(code_h × (1 + Σ hệ số của nhóm)), nhóm theo kind / owner / pure (meta.estimate_rule)
Issue cha = tổng giờ con.
"""
import json
import math
from pathlib import Path

import yaml

LAB5 = Path(__file__).resolve().parents[2]
SRC = LAB5 / "working" / "backlog-source.yaml"
LAB1_WBS = next((LAB5.parent / "lab-1-estimation-proposal" / "06-estimate-wbs").glob("*.json"))


def load():
    src = yaml.safe_load(SRC.read_text())
    lab1 = {t["id"]: t for c in json.loads(LAB1_WBS.read_text())["options"][0]["categories"] for t in c["tasks"]}
    return src, lab1


def rule_group(it):
    kind, owner = it["kind"], it.get("owner", "")
    if kind in ("test", "clarify", "spike"):
        return kind
    side = "fe" if owner.startswith("FE") else "be"
    return f"{side}_pure" if it.get("pure") else side


def breakdown(it, rules):
    """Trả dict thành phần giờ (trước làm tròn) của một issue lá không thô."""
    code = it["code_h"]
    parts = {"code": code}
    for name, coef in rules[rule_group(it)].items():
        parts[name] = code * coef
    return parts


def lab1_md(ids, lab1):
    return sum(lab1[i]["total_md"] for i in ids if i in lab1)


def hours(it, src, lab1):
    if it.get("subs"):
        return sum(hours(s, src, lab1) for s in it["subs"])
    meta = src["meta"]
    if it["kind"] == "coarse":
        return lab1_md(it.get("lab1", []), lab1) * meta["md_hours"]
    if "hours_override" in it:
        return it["hours_override"]
    return math.ceil(sum(breakdown(it, meta["estimate_rule"]).values()) - 1e-9)


def walk(issues, parent=None):
    for it in issues:
        yield it, parent
        yield from walk(it.get("subs", []), it)
