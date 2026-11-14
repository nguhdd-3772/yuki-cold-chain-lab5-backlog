#!/usr/bin/env python3
"""Kiểm backlog-source.yaml: cấu trúc, độ hạt, độ phủ so với LAB-4 và LAB-1; in tổng theo epic.

Chạy: python3 working/scripts/check-backlog-coverage.py  (từ thư mục lab-5-task-breakdown-progress)
Thoát mã 1 nếu có lỗi cấu trúc / độ phủ.
"""
import fnmatch
import re
import sys

from backlog_estimate_rules import LAB5, hours, lab1_md, load, walk

LAB4 = LAB5.parent / "lab-4-design" / "specs" / "specs"


def lab4_inventory():
    guide = (LAB4 / "_common" / "ai-authoring-guide.md").read_text()
    design = (LAB4 / "_common" / "YUKI_DESIGN.md").read_text()
    return {
        "G": sorted(set(re.findall(r"^\| (G-\d+) \|", guide, re.M))),
        "Q": sorted(set(re.findall(r"^\| (Q\d+) \|", design, re.M)), key=lambda q: int(q[1:])),
        "SPEC": sorted(p.name.replace("_SPEC.md", "") for p in LAB4.glob("*/screen-specification/*_SPEC.md")),
        "TECH": sorted(p.stem for p in LAB4.glob("*/technical-design/*_TECH.md")),
        "API": sorted(p.name.replace("_API.md", "") for p in LAB4.glob("system-design/api-design/*/*_API.md")),
    }


def check_leaf(it, meta, errors):
    k = it["key"]
    if it["kind"] == "coarse":
        if not it.get("lab1"):
            errors.append(f"{k}: issue thô thiếu lab1")
        return
    if "code_h" not in it and "hours_override" not in it:
        errors.append(f"{k}: issue lá thiếu code_h")
    if "hours_override" in it and not it.get("override_why"):
        errors.append(f"{k}: hours_override thiếu override_why")
    if not it.get("ac"):
        errors.append(f"{k}: thiếu tiêu chí nghiệm thu (ac)")


def main():
    src, lab1 = load()
    meta = src["meta"]
    errors, keys, refs_all, lab1_used, rows = [], set(), set(), {}, []

    for epic in src["epics"]:
        refs_all.update(epic.get("refs", []))
        for lid in epic.get("lab1", []):
            lab1_used.setdefault(lid, []).append(epic["key"])
        t = {"issues": 0, "leaves": 0, "coarse": 0}
        for it, _ in walk(epic["issues"]):
            k = it["key"]
            if k in keys:
                errors.append(f"trùng key {k}")
            keys.add(k)
            refs_all.update(it.get("refs", []))
            if not it.get("refs"):
                errors.append(f"{k}: thiếu refs (cấm bịa)")
            if it.get("owner") and it["owner"] not in meta["owners"]:
                errors.append(f"{k}: owner lạ {it['owner']}")
            t["issues"] += 1
            if it.get("subs"):
                if "code_h" in it or "hours_override" in it:
                    errors.append(f"{k}: issue cha không ghi giờ")
                continue
            t["leaves"] += 1
            if not it.get("owner"):
                errors.append(f"{k}: issue lá thiếu owner")
            check_leaf(it, meta, errors)
            if it["kind"] == "coarse":
                t["coarse"] += 1
                for lid in it.get("lab1", []):
                    if lid not in lab1:
                        errors.append(f"{k}: mã LAB-1 lạ {lid}")
                    elif epic.get("coarse"):
                        lab1_used.setdefault(lid, []).append(k)
            elif hours(it, src, lab1) > meta["max_leaf_hours"]:
                errors.append(f"{k}: {hours(it, src, lab1)}h > {meta['max_leaf_hours']}h, phải tách sub-issue")
        hrs = sum(hours(i, src, lab1) for i in epic["issues"])
        l1 = hrs / meta["md_hours"] if epic.get("coarse") else lab1_md(epic.get("lab1", []), lab1)
        rows.append((epic["key"], epic["title"][:58], t, hrs, l1))

    outside = [p for o in src["lab1_outside_backlog"] for p in o["ids"]]
    for lid, task in lab1.items():
        used, is_out = lab1_used.get(lid, []), any(fnmatch.fnmatch(lid, p) for p in outside)
        if len(used) > 1:
            errors.append(f"LAB-1 {lid} gán nhiều nơi: {used}")
        if not used and not is_out:
            errors.append(f"LAB-1 {lid} ({task['name'][:40]}) chưa thuộc epic nào và không có lý do ngoài backlog")
        if used and is_out:
            errors.append(f"LAB-1 {lid} vừa trong backlog vừa trong danh sách ngoài")

    inv, flat = lab4_inventory(), " ".join(refs_all)
    for kind, items in inv.items():  # G / Q khớp chính xác; SPEC / TECH / API khớp chuỗi con
        for x in items:
            if x not in refs_all and (kind in "GQ" or x not in flat):
                errors.append(f"LAB-4 {kind} {x} chưa có issue")

    mdh = meta["md_hours"]
    print(f"{'Epic':5} {'Tên':58} {'Issue':>5} {'Lá':>4} {'Thô':>4} {'Giờ':>6} {'MD':>6} {'LAB-1':>6} {'%':>4}")
    g = [0, 0, 0, 0, 0]
    for key, title, t, hrs, l1 in rows:
        print(f"{key:5} {title:58} {t['issues']:5} {t['leaves']:4} {t['coarse']:4} {hrs:6.0f} {hrs/mdh:6.1f} {l1:6.0f} {hrs/mdh/l1*100:4.0f}")
        for i, v in enumerate((t["issues"], t["leaves"], t["coarse"], hrs, l1)):
            g[i] += v
    det = [r for r in rows if not any(e["key"] == r[0] and e.get("coarse") for e in src["epics"])]
    dh, dl = sum(r[3] for r in det), sum(r[4] for r in det)
    print(f"{'Tổng':64} {g[0]:5} {g[1]:4} {g[2]:4} {g[3]:6.0f} {g[3]/mdh:6.1f} {g[4]:6.0f}")
    print(f"Phần chi tiết E01–E10: {dh:.0f}h = {dh/mdh:.1f} MD so với LAB-1 {dl:.0f} MD ({dh/mdh/dl*100:.0f}%)")
    print("LAB-4 inventory: " + ", ".join(f"{k} {len(v)}" for k, v in inv.items()) + f" · epic {len(src['epics'])} · key {len(keys)}")
    if errors:
        print(f"\n{len(errors)} LỖI:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("0 lỗi")


if __name__ == "__main__":
    main()
