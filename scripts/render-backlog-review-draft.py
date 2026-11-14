#!/usr/bin/env python3
"""Sinh working/backlog-draft-for-review.md từ backlog-source.yaml để PL duyệt trước khi tạo issue trên GitHub."""
from backlog_estimate_rules import LAB5, breakdown, hours, lab1_md, load, rule_group

OUT = LAB5 / "working" / "backlog-draft-for-review.md"
KIND = {"feat": "làm mới", "gap": "sửa gap", "test": "test", "clarify": "hỏi khách", "spike": "spike", "coarse": "thô"}


def calc_text(it, src):
    """Chuỗi cách ra giờ để PL soát: code_h × (1 + hệ số)."""
    if it.get("subs") or it["kind"] == "coarse":
        return "Σ con" if it.get("subs") else "MD LAB-1 × 8"
    if "hours_override" in it:
        return f"chốt tay: {it['override_why']}"
    coefs = src["meta"]["estimate_rule"][rule_group(it)]
    extra = "+".join(f"{v:g}" for v in coefs.values() if v)
    return f"{it['code_h']} × (1+{extra}) [{rule_group(it)}]" if extra else f"{it['code_h']} [{rule_group(it)}]"


def main():
    src, lab1 = load()
    mdh = src["meta"]["md_hours"]
    summary, body = [], []
    for ep in src["epics"]:
        hrs = sum(hours(i, src, lab1) for i in ep["issues"])
        l1 = hrs / mdh if ep.get("coarse") else lab1_md(ep.get("lab1", []), lab1)
        tag = " ★ ràng buộc đặc thù" if ep.get("constraint") else ""
        summary.append(f"| {ep['key']} | {ep['title']}{tag} | {hrs:.0f} | {hrs/mdh:.1f} | {l1:.0f} | {hrs/mdh/l1*100:.0f}% |")
        body += [f"## {ep['key']} — {ep['title']}", "",
                 f"Nguồn LAB-4: {', '.join(ep.get('refs', []))} · LAB-1 thay thế: {', '.join(ep.get('lab1', [])) or '— (tính theo issue)'}", "",
                 "| Key | Issue / sub-issue | Loại | Phụ trách | Giờ | Cách ra giờ | Nguồn |", "|---|---|---|---|---:|---|---|"]
        for it in ep["issues"]:
            for x, pre in [(it, "")] + [(s, "↳ ") for s in it.get("subs", [])]:
                name = f"**{x['title']}**" if x.get("subs") else x["title"]
                refs = ", ".join(x.get("refs", []) + ([f"LAB-1 {'/'.join(x['lab1'])}"] if x.get("lab1") else []))
                body.append(f"| {x['key']} | {pre}{name} | {KIND[x['kind']]} | {x.get('owner', '—')} | "
                            f"{hours(x, src, lab1):.0f} | {calc_text(x, src)} | {refs} |")
        body.append("")
    rule_rows = [f"| {g} | " + ", ".join(f"{k} +{v:g}" for k, v in c.items()) + " |" if c else f"| {g} | không cộng |"
                 for g, c in src["meta"]["estimate_rule"].items()]
    out = ["# Backlog LAB-5 — bản nháp để PL duyệt (sinh từ `backlog-source.yaml`, không sửa tay)", "",
           "Giờ issue lá = ceil(code_h × (1 + hệ số nhóm)); issue thô = MD LAB-1 × 8; issue cha = tổng con.", "",
           "| Nhóm | Hệ số cộng thêm trên giờ code |", "|---|---|", *rule_rows, "",
           "| Epic | Tên | Giờ LAB-5 | MD LAB-5 | MD LAB-1 cùng phạm vi | LAB-5 / LAB-1 |", "|---|---|---:|---:|---:|---:|",
           *summary, "", *body]
    OUT.write_text("\n".join(out))
    print(f"wrote {OUT.relative_to(LAB5)}")


if __name__ == "__main__":
    main()
