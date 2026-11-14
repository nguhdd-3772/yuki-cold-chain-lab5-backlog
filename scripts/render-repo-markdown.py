#!/usr/bin/env python3
"""Render working/md-templates/*.md → repo yuki-cold-chain-lab5-backlog/*.md.

Placeholder:
  {E06-10} / {E06}     → [#số](url) E06-10   (số lấy từ github-sync-state.json; chưa tạo issue → giữ mã, in cảnh báo)
  {{PROJECT_LINK}}, {{COUNT_*}}, {{E06_HOURS}}, {{E06_LAB1}}, {{TABLE_SPEC_TO_ISSUE}}
Mọi con số lấy từ backlog-source.yaml qua backlog_estimate_rules — không gõ tay.
"""
import json
import re
from importlib import import_module

from backlog_estimate_rules import LAB5, hours, lab1_md, load, walk

TEMPLATES = LAB5 / "working" / "md-templates"
REPO = LAB5 / "yuki-cold-chain-lab5-backlog"
STATE = json.loads((LAB5 / "working" / "github-sync-state.json").read_text())

# (spec LAB-4, token để tìm trong refs, phần chưa thành issue và vì sao)
SPEC_ROWS = [
    ("S-RC-02_SPEC (入荷検品)", ["S-RC-02"], "—"),
    ("RECV_INSPECT_TECH · API-RC-02", ["RECV_INSPECT_TECH", "API-RC-02"], "—"),
    ("S-IV-04_SPEC (品質ステータス)", ["S-IV-04"], "—"),
    ("S-OD-04_SPEC (引当実行・結果)", ["S-OD-04"], "—"),
    ("ALLOC_RUN_TECH · API-OD-04", ["ALLOC_RUN_TECH", "API-OD-04"], "—"),
    ("S-RT-01_SPEC (配車計画ボード)", ["S-RT-01"], "—"),
    ("S-RT-02-03_SPEC (改善基準チェック結果・ルート版履歴)", ["S-RT-02-03"], "—"),
    ("ROUTE_CHECK_TECH · API-RT-02", ["ROUTE_CHECK_TECH", "API-RT-02"], "Ngoại lệ 改善基準告示 (2 người lái, フェリー, 分割休息…): ngoài gói theo ASM-02, không có issue"),
    ("S-DR-03_SPEC (納品・POD登録)", ["S-DR-03"], "—"),
    ("POD_COMPLETE_TECH · API-DR-02", ["POD_COMPLETE_TECH", "API-DR-02"], "—"),
    ("S-TP-02-03_SPEC (アラーム対応キュー・再測定)", ["S-TP-02-03"], "—"),
    ("S-TP-04_SPEC (逸脱ケース)", ["S-TP-04"], "—"),
    ("TEMP_IMPORT_TECH · API-TP-02", ["TEMP_IMPORT_TECH", "API-TP-02"], "Kết nối logger trực tuyến (OPT-02): ngoài gói"),
    ("S-TR-01_SPEC (トレース検索)", ["S-TR-01"], "—"),
    ("S-CM-03_SPEC (承認待ち一覧・承認)", ["S-CM-03"], "—"),
    ("APPROVAL_DECIDE_TECH · API-CM-03", ["APPROVAL_DECIDE_TECH", "API-CM-03"], "—"),
    ("_common: api-conventions · error-codes · common-spec", ["api-conventions", "error-codes", "common-spec"], "—"),
    ("_common: api-list (35 API)", ["api-list"], "29 API không có file thiết kế chi tiết: làm cùng màn hình của nó; API của màn hình chưa có spec nằm trong issue thô E11"),
    ("_common: YUKI_DESIGN (kiến trúc, NFR)", ["NFR-PERF-02", "NFR-AVL-02", "NFR-OPS-01"], "NFR hạ tầng (giám sát, sao lưu, bảo mật pipeline) nằm trong issue thô E14 / E15"),
    ("ADR-001 … ADR-011", ["ADR-00", "ADR-01"], "ADR-001 (stack) không thành issue riêng: hiện thực ở E14-06 (môi trường, CI/CD)"),
    ("Database design: 5 file YUKI_*_DB + _er-overview", ["YUKI_INVENTORY_DB", "YUKI_ORDER_DB", "YUKI_ROUTE_DB", "YUKI_TEMP_DB"],
     "Không tách issue DB riêng: migration nằm trong DoD của issue dùng bảng đó. YUKI_MASTER_DB thuộc màn hình master (issue thô E11-02 / E11-03)"),
    ("Gap G-01 … G-36", ["G-"], "36/36 gap có issue (script kiểm). G-33 chưa có thiết kế → issue hỏi khách E04-08"),
    ("Câu hỏi khách Q1 … Q12", ["Q"], "Q6 (lịch batch ERP) chưa có issue riêng: hỏi khi viết spec E13-01"),
]


OWNER_REPO = "nguhdd-3772/yuki-cold-chain-lab5-backlog"


def spec_to_epic(src, idx, epic_of):
    """README §5: mỗi dòng SPEC_ROWS → epic (#số — tên) + ghi chú ràng buộc đặc thù."""
    rows = ["| Spec (LAB-4 / PREMISE) | Epic | Ghi chú |", "|---|---|---|"]
    for label, tokens, _ in SPEC_ROWS:
        eps = sorted({epic_of[k] for k in epic_of if hit(idx[k].get("refs", []), tokens)}
                     | {e["key"] for e in src["epics"] if hit(e.get("refs", []), tokens)})
        names = ", ".join(f"{link(e)} — {idx[e]['title'].split(' (')[0].split(' — ')[0]}" for e in eps)
        note = "Ràng buộc đặc thù: giờ lái 2024" if "E06" in eps and len(eps) <= 2 else ""
        rows.append(f"| {label} | {names} | {note} |")
    for line, eps in (("PREMISE S1 (gợi ý chèn nghỉ)", ["E06"]), ("PREMISE S2 (truy xuất lô con)", ["E09"]),
                      ("PREMISE S5 (49 màn hình chưa spec → issue thô)", ["E11", "E12", "E13", "E14", "E15"])):
        rows.append(f"| {line} | {', '.join(link(e) for e in eps)} | {'Ràng buộc đặc thù: giờ lái 2024' if 'E06' in eps else ''} |")
    return "\n".join(rows)


def link(key):
    it = STATE["issues"].get(key)
    if not it:
        print("  ! chưa có issue:", key)
        return key
    return f"[#{it['number']}]({it['url']}) {key}"


def build_index(src):
    idx, epic_of, parent_of = {}, {}, {}
    for ep in src["epics"]:
        idx[ep["key"]] = ep
        for it, parent in walk(ep["issues"]):
            idx[it["key"]] = it
            epic_of[it["key"]] = ep["key"]
            parent_of[it["key"]] = parent["key"] if parent else None
    return idx, epic_of, parent_of


def hit(refs, tokens):
    for r in refs:
        for t in tokens:
            if t in ("G-", "ADR-00", "ADR-01"):
                if r.startswith(t):
                    return True
            elif t == "Q":
                if re.fullmatch(r"Q\d+", r):
                    return True
            elif r == t:
                return True
    return False


def spec_table(src, idx, epic_of, parent_of):
    rows = ["| Spec LAB-4 | Epic | Issue / sub-issue | Phần spec chưa thành issue và vì sao |", "|---|---|---|---|"]
    for label, tokens, note in SPEC_ROWS:
        matched = {k for k in epic_of if hit(idx[k].get("refs", []), tokens)}
        keys = [k for k in epic_of if k in matched and parent_of[k] not in matched]  # issue cha đã khớp thì không liệt kê con
        epics = sorted({epic_of[k] for k in keys} | {e["key"] for e in src["epics"] if hit(e.get("refs", []), tokens)})
        if label.startswith(("Gap", "Câu hỏi", "ADR")):
            shown = f"{len(matched)} issue ở {len(epics)} epic (xem dòng Nguồn trong từng issue)"
        elif not keys:
            shown = "— (tham chiếu ở mức epic)"
        else:
            shown = ", ".join(link(k) for k in keys)
        rows.append(f"| {label} | {', '.join(link(e) for e in epics) or '—'} | {shown} | {note} |")
    # Phần LAB-1 chưa có spec
    for ep in src["epics"]:
        if ep.get("coarse"):
            rows.append(f"| Chưa có spec LAB-4: {ep['title'].replace(' (issue thô)', '')} | {link(ep['key'])} | "
                        f"{len(ep['issues'])} issue thô | Chưa có spec: chỉ có giờ LAB-1, tách khi viết spec (PREMISE S5) |")
    return "\n".join(rows)


def main():
    src, lab1 = load()
    idx, epic_of, parent_of = build_index(src)
    e06 = idx["E06"]
    leaves = [it for k, it in idx.items() if k in epic_of and not it.get("subs")]
    values = {
        "PROJECT_LINK": f"[{STATE['project_url']}]({STATE['project_url']})",
        "COUNT_EPICS": str(len(src["epics"])),
        "COUNT_ISSUES": str(len(epic_of)),
        "COUNT_LEAVES": str(len(leaves)),
        "COUNT_COARSE": str(sum(1 for it in leaves if it["kind"] == "coarse")),
        "E06_HOURS": str(sum(hours(i, src, lab1) for i in e06["issues"])),
        "E06_LAB1": f"{lab1_md(e06['lab1'], lab1):g}",
        "TABLE_SPEC_TO_ISSUE": spec_table(src, idx, epic_of, parent_of),
        "REPO_URL": f"https://github.com/{OWNER_REPO}",
        "PAGES_URL": f"https://{OWNER_REPO.split('/')[0]}.github.io/{OWNER_REPO.split('/')[1]}",
        "TABLE_SPEC_TO_EPIC": spec_to_epic(src, idx, epic_of),
    }
    values.update(import_module("render-estimate-and-progress-tables").values(link))
    values.update(json.loads((TEMPLATES / "manual-values.json").read_text()))  # giá trị PL điền tay (mã học viên, kết quả review)
    REPO.mkdir(exist_ok=True)
    for tpl in sorted(TEMPLATES.glob("*.md")):
        text = tpl.read_text()
        text = re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], text)
        text = re.sub(r"\{(E\d\d(?:-\d\d[a-z]?)?)\}", lambda m: link(m.group(1)), text)
        (REPO / tpl.name).write_text(text)
        print("wrote", tpl.name)


if __name__ == "__main__":
    main()
