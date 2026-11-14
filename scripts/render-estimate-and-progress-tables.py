#!/usr/bin/env python3
"""Bảng cho estimate.md và progress-report.md — mọi số lấy từ nguồn, không gõ tay.

Nguồn: backlog-source.yaml (giờ), github-sync-state.json (SWP đã ghi lên Project),
payload nhúng trong báo cáo HTML của tkm:estimate-swp (mẫu review, lan truyền), sprint-1-summary.json.
Dùng qua render-repo-markdown.py: values(link) trả về dict placeholder → nội dung.
"""
import json
import re
import statistics

from backlog_estimate_rules import LAB5, hours, lab1_md, load, walk

REPORT_NAME = "estimate-swp-yuki-cold-chain-backlog-p2-20261114.html"
REPORT = LAB5 / "yuki-cold-chain-lab5-backlog" / "reports" / REPORT_NAME
STATE = json.loads((LAB5 / "working" / "github-sync-state.json").read_text())
SPRINT = json.loads((LAB5 / "working" / "sprint-1-summary.json").read_text())
SWP = STATE["swp_done"]
NUM2KEY = {v["number"]: k for k, v in STATE["issues"].items()}
STATUS_NOTE = {"Done": "Đã review, đóng issue", "In review": "Code xong, chờ review / chạy lại test",
               "In progress": "Mang sang Sprint 2 (giờ còn lại ở bảng dưới)", "Blocked": "Chờ khách trả lời"}
COMMON_WHY = "LAB-1 làm tròn lên MD theo từng vai trò của mỗi task + buffer 15%; LAB-5 ước giờ từng việc lá đã có spec, buffer để ở dự phòng M.*"
WHY_LAB1 = {
    "E01": "Chung (*). LAB-4 gộp mã lỗi / phân quyền / audit thành quy ước chung; thêm khung chính sách có phiên bản",
    "E02": "Chung (*). Prototype LAB-2 đã có màn hình kiểm nhập + quy tắc nhiệt độ nhập (96 dòng); LAB-5 sửa theo gap",
    "E03": "Chung (*). Phạm vi rõ sau S-IV-04: 1 bảng chuyển trạng thái + 1 màn hình",
    "E04": "Prototype đã có allocation-rules-engine (117 dòng) + 10 unit test; LAB-1 tính QA 11 MD, LAB-5 còn 2 issue test (30h)",
    "E05": "Chung (*). Adapter bản đồ tách thành interface + bản giả cho test, nhà cung cấp thật 1 issue",
    "E06": "Cao hơn: thêm 4 ngưỡng kỳ (G-31), gợi ý chèn nghỉ (PREMISE S1), spike luật, seed nhiều ngày; prototype chỉ kiểm theo ngày",
    "E07": "Chung (*). POD offline tách 4 sub-issue; bằng chứng theo hợp đồng chờ Q1",
    "E08": "Prototype đã có quy tắc nhiệt độ + nhập CSV logger; LAB-5 sửa định nghĩa duration_min / SLA (gap) và làm case sai lệch",
    "E09": "Prototype đã có màn hình + API truy xuất; LAB-5 làm lại bộ máy xuôi / ngược, hiệu năng, lô con (PREMISE S2)",
    "E10": "Chung (*). Khung duyệt dùng chung cho 6 loại, chỉ cấu hình ma trận người duyệt",
}
# Lý do PL chốt — ghi theo lựa chọn PL đã chọn trong vòng review (2026-11-14)
SAMPLE_WHY = {
    "E01-03a": "Giữ: chỉ hỏi 1 câu và ghi vào Q&A list, không có code",
    "E02-01a": "Nâng lên mức vừa: phần khó là transaction + mã không trùng khi nhiều request song song; skill chỉ tính 1 hàm DB + 1 API",
    "E11-08": "Nâng: nhóm màn hình vận hành tuyến / POD có đồng bộ offline, rộng hơn skill chấm",
    "E11-05": "Giữ: nhiều màn hình nhưng chuyển trạng thái tồn kho là mẫu quen; giờ thật nằm ở cột giờ (MD LAB-1)",
    "E06-13": "Giữ: 1 màn hình, dùng lại khung chính sách E01-05; độ tin cậy thấp vì chưa có spec",
}
OUTLIER_ACTION = {
    "feat-fe": "Giữ giờ: skill coi 1 màn hình là phạm vi nhỏ, chưa tính tích hợp FE–API (+30%) và các trạng thái lỗi M_xx",
    "E05-03a": "Giữ giờ: interface + bộ travel_times giả cho test lập tuyến; dùng chung cho 4 issue E05/E06",
    "E07-01": "Giờ có thể thiếu: 4 thao tác ghi trong 1 transaction (so với E02-01a 18h). Ước lại khi lập kế hoạch sprint có E07",
    "low": "Lệch nhỏ, việc theo mẫu lặp lại (sinh ma trận quyền / bỏ vai trò DEMO): giữ giờ",
}


def payload():
    html = REPORT.read_text(encoding="utf-8")
    return json.loads(re.search(r'<script[^>]*application/json[^>]*>(.*?)</script>', html, re.S).group(1))


def key_of(ref):
    return NUM2KEY[int(ref.rsplit("#", 1)[1])]


def leaves(src, lab1):
    for ep in src["epics"]:
        for it, _ in walk(ep["issues"]):
            if not it.get("subs"):
                yield ep, it, hours(it, src, lab1)


def values(link):
    src, lab1 = load()
    p = payload()
    v = {"SWP_REPORT": f"[reports/{REPORT_NAME}](./reports/{REPORT_NAME})"}
    by_ref = {i["issueRef"]: i for i in p["issues"]}
    rows = ["| Issue | Vì sao skill chọn | Skill chấm (Scope × Complexity → SWP) | Bạn chốt | Lý do |", "|---|---|---|---|---|"]
    reason_vi = {"minimum": "nhỏ nhất", "lower-median": "trung vị", "maximum": "lớn nhất", "outlier": "lệch xa trung vị",
                 "lowest-confidence": "độ tin cậy thấp nhất", "split-boundary": "đề xuất tách", "coverage-fill": "phủ nhóm khác"}
    for r in p["representatives"]:
        i, k = by_ref[r["issueRef"]], key_of(r["issueRef"])
        rows.append(f"| {link(k)} {i['title'].split('] ', 1)[-1][:60]} | {', '.join(reason_vi[x] for x in r['selectionReasons'])} | "
                    f"{i['initialScope']} × {i['initialComplexity']} → **{i['initialSWP']}** | "
                    f"{i['finalScope']} × {i['finalComplexity']} → **{i['finalSWP']}** | {SAMPLE_WHY[k]} |")
    v["TABLE_SWP_SAMPLES"] = "\n".join(rows)
    prop = [i for i in p["issues"] if i["calibration"]["status"] == "propagated"]
    v["TABLE_SWP_PROPAGATED"] = "\n".join(["| Issue | SWP skill → sau hiệu chỉnh | Theo quy tắc |", "|---|---|---|"] +
                                          [f"| {link(key_of(i['issueRef']))} {i['title'].split('] ', 1)[-1][:55]} | {i['initialSWP']} → {i['finalSWP']} | "
                                           f"{i['calibration']['matchedRuleId']} |" for i in prop])
    v["COUNT_PROPAGATED"] = str(len(prop))
    v["SWP_INITIAL"], v["SWP_FINAL"] = str(sum(i["initialSWP"] for i in p["issues"])), str(sum(i["finalSWP"] for i in p["issues"]))

    lv = list(leaves(src, lab1))
    det = [(ep, it, h) for ep, it, h in lv if it["kind"] != "coarse"]
    med = statistics.median(h / SWP[it["key"]] for _, it, h in det)
    v["MEDIAN_H_PER_SWP"] = f"{med:.1f}".replace(".", ",")
    v["MEDIAN_H_PER_SWP_COARSE"] = f"{statistics.median(h / SWP[it['key']] for _, it, h in lv if it['kind'] == 'coarse'):.1f}".replace(".", ",")
    rows = ["| Issue | Loại | Giờ | SWP | Giờ / SWP | Xử lý |", "|---|---|---|---|---|---|"]
    for ep, it, h in det:
        q = h / SWP[it["key"]]
        if it["kind"] == "clarify" or med / 2 <= q <= med * 2:
            continue
        act = OUTLIER_ACTION.get(it["key"]) or (OUTLIER_ACTION["feat-fe"] if q > med else OUTLIER_ACTION["low"])
        rows.append(f"| {link(it['key'])} {it['title'][:50]} | {it['kind']} | {h} | {SWP[it['key']]} | {q:.1f} | {act} |")
    v["TABLE_SWP_OUTLIERS"] = "\n".join(rows)

    notes = {"E04": "Quy tắc phân bổ đã có code + 10 unit test ở prototype LAB-2", "E06": "Ràng buộc đặc thù; gồm spike + 2 câu hỏi khách",
             "E08": "Quy tắc nhiệt độ đã có code ở prototype LAB-2", "E11": "Issue thô: SWP chưa có nghĩa đến khi tách"}
    rows = ["| Epic | Số issue (việc lá) | Tổng SWP | Tổng giờ | MD | Ghi chú |", "|---|---|---|---|---|---|"]
    tot = [0, 0, 0, 0]
    for ep in src["epics"]:
        n_all = sum(1 for _ in walk(ep["issues"]))
        n_leaf = sum(1 for e, _, _ in lv if e is ep)
        h = sum(hours(i, src, lab1) for i in ep["issues"])
        note = notes.get(ep["key"]) or ("Issue thô: giờ = MD LAB-1 × 8" if ep.get("coarse") else "")
        rows.append(f"| {link(ep['key'])} {ep['title'][:48]} | {n_all} ({n_leaf}) | {SWP[ep['key']]} | {h} | {h / 8:.1f} | {note} |")
        tot = [tot[0] + n_all, tot[1] + n_leaf, tot[2] + SWP[ep["key"]], tot[3] + h]
    rows.append(f"| **Tổng** | **{tot[0]} ({tot[1]})** | **{tot[2]}** | **{tot[3]}** | **{tot[3] / 8:.1f}** | |")
    v["TABLE_EPIC_TOTALS"] = "\n".join(rows)
    v["TOTAL_HOURS"], v["TOTAL_MD"], v["TOTAL_SWP"] = str(tot[3]), f"{tot[3] / 8:g}".replace(".", ","), str(tot[2])
    v["DETAIL_SWP"] = str(sum(SWP[e["key"]] for e in src["epics"] if not e.get("coarse")))

    lab1_total = sum(t["total_md"] for t in lab1.values())
    out_md = {g["why"].split(" — ")[0]: sum(t["total_md"] for tid, t in lab1.items()
                                            if any(tid == x or (x.endswith(".*") and tid.startswith(x[:-1])) for x in g["ids"]))
              for g in src["lab1_outside_backlog"]}
    v["LAB1_TOTAL"] = f"{lab1_total:,}".replace(",", ".")
    why_out = {g["why"].split(" — ")[0]: g["why"].split(" — ", 1)[1] for g in src["lab1_outside_backlog"]}
    v["LAB1_OUTSIDE"] = "\n".join(f"| Ngoài backlog: {k} | {m} MD | — | — | {why_out[k]} |" for k, m in out_md.items())
    v["LAB1_DETAIL_ROWS"] = "\n".join(
        f"| {link(ep['key'])} | {lab1_md(ep['lab1'], lab1):g} MD | {sum(hours(i, src, lab1) for i in ep['issues']) / 8:.1f} MD | "
        f"{sum(hours(i, src, lab1) for i in ep['issues']) / 8 - lab1_md(ep['lab1'], lab1):+.1f} MD | {WHY_LAB1[ep['key']]} |"
        for ep in src["epics"] if not ep.get("coarse"))
    v["COMMON_WHY"] = COMMON_WHY
    v.update(sprint_values(link))
    # Dự báo: còn 8 sprint (Sprint 2–9) tới mốc xong 構築・システムテスト 2027-04-02 (LAB-1 slide 13).
    # Năng lực = nhân sự P2 LAB-1 (06-estimate-wbs.md) 9,4 người × 10 ngày × 8h; trừ Tết (5 ngày) và 1/1 (1 ngày).
    done_h, done_swp = SPRINT["status"]["Done"]["h"], SPRINT["status"]["Done"]["swp"]
    fte = 3.3 + 2.5 + 2.4 + 0.2 + 0.4 + 0.3 + 0.3
    cap = round(fte * 80)
    holiday = round(fte * 8 * (5 + 1))
    cap8 = cap * 8 - holiday
    left = tot[3] - done_h
    v.update(FC_FTE=f"{fte:.1f}".replace(".", ","), FC_CAP_SPRINT=str(cap), FC_HOLIDAY_H=str(holiday), FC_CAP_H=str(cap8),
             FC_LEFT_H=str(left), FC_MARGIN_H=str(cap8 - left), FC_NEED_PCT=str(round(100 * left / cap8)),
             FC_DONE_H=str(done_h), FC_DONE_PCT_CAP=str(round(100 * done_h / cap)), FC_S1_RATE_H=str(done_h * 8),
             FC_DETAIL_LEFT_SWP=str(int(v["DETAIL_SWP"]) - done_swp),
             FC_DETAIL_SPRINTS=f"{(int(v['DETAIL_SWP']) - done_swp) / done_swp:.1f}".replace(".", ","),
             FC_USED_PCT=str(round(100 * SPRINT["total_h"] / cap)))
    return v


def sprint_values(link):
    s = SPRINT
    v = {"SPRINT_" + k.upper(): str(s[k]) for k in ("iteration", "start", "end", "goal", "capacity_note", "total_swp", "total_h", "left_h_end")}
    order = ["Done", "In review", "In progress", "Blocked"]
    rows = ["| Trạng thái | Số issue | Tổng SWP | Giờ ước lượng | Ghi chú |", "|---|---|---|---|---|"]
    for st in order:
        x = s["status"].get(st)
        if x:
            rows.append(f"| {st} | {x['count']} | {x['swp']} | {x['h']} | {STATUS_NOTE[st]} |")
    rows.append(f"| **Tổng cam kết** | **{len(s['rows'])}** | **{s['total_swp']}** | **{s['total_h']}** | |")
    v["TABLE_SPRINT_STATUS"] = "\n".join(rows)
    done = s["status"]["Done"]["swp"]
    v["SPRINT_DONE_SWP"], v["SPRINT_DONE_PCT"] = str(done), str(round(100 * done / s["total_swp"]))
    v["TABLE_BURNDOWN"] = "\n".join(["| Cuối ngày | SWP còn lại (lý tưởng) | SWP còn lại (thực tế) | Issue Done lũy kế |", "|---|---|---|---|"] +
                                    [f"| {b['date']} | {b['ideal_swp']:g} | {b['left_swp']} | {b['done_count']} |" for b in s["burn"]])
    v["TABLE_SPRINT_OPEN"] = "\n".join(["| Issue | Phụ trách | Trạng thái | SWP | Giờ còn lại | Diễn biến (giả lập) |", "|---|---|---|---|---|---|"] +
                                       [f"| {link(r['key'])} {r['title'][:45]} | {r['owner']} | {r['end']} | {r['swp']} | {r.get('left_h', '')} | {r.get('note', '')} |"
                                        for r in s["rows"] if r["end"] != "Done"])
    v["TABLE_SPRINT_DONE"] = ", ".join(link(r["key"]) for r in s["rows"] if r["end"] == "Done")
    v["TABLE_SPRINT_LOAD"] = "\n".join(["| Vai trò | Giờ nhận | Trần |", "|---|---|---|"] +
                                       [f"| {o} | {h} | 56 |" for o, h in s["load_by_owner"].items()])
    return v
