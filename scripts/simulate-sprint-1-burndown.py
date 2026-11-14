#!/usr/bin/env python3
"""Sprint 1 giả lập: tính burndown (SWP + giờ), vẽ SVG, xuất summary; --apply ghi Iteration / Status lên Project.

Nguồn: working/sprint-1-simulation.yaml + backlog-source.yaml (giờ) + github-sync-state.json (SWP đã review).
Ra:    yuki-cold-chain-lab5-backlog/reports/sprint-1-burndown.svg, working/sprint-1-summary.json
Chạy:  python3 working/scripts/simulate-sprint-1-burndown.py [--apply]
"""
import json
import sys
from collections import defaultdict
from importlib import import_module

import yaml

from backlog_estimate_rules import LAB5, hours, load, walk

SIM = yaml.safe_load((LAB5 / "working" / "sprint-1-simulation.yaml").read_text())
SVG = LAB5 / "yuki-cold-chain-lab5-backlog" / "reports" / "sprint-1-burndown.svg"
SUMMARY = LAB5 / "working" / "sprint-1-summary.json"
CAP_PER_PERSON = 56


def build():
    src, lab1 = load()
    st = json.loads((LAB5 / "working" / "github-sync-state.json").read_text())
    idx = {it["key"]: it for ep in src["epics"] for it, _ in walk(ep["issues"])}
    rows = []
    for x in SIM["items"]:
        it = idx[x["key"]]
        assert not it.get("subs"), f"{x['key']} là issue cha — sprint chỉ nhận việc lá"
        rows.append(x | {"title": it["title"], "owner": it["owner"], "h": hours(it, src, lab1),
                         "swp": st["swp_done"][x["key"]], "constraint": "DRIVER-2024" in it.get("refs", []) or x["key"].startswith("E06")})
    load_by_owner = defaultdict(int)
    for r in rows:
        load_by_owner[r["owner"]] += r["h"]
    over = {o: h for o, h in load_by_owner.items() if h > CAP_PER_PERSON}
    assert not over, f"vượt trần {CAP_PER_PERSON}h: {over}"

    n = len(SIM["workdays"])
    tot_swp, tot_h = sum(r["swp"] for r in rows), sum(r["h"] for r in rows)
    burn = []
    for d in range(n + 1):  # d = 0: đầu sprint
        done = [r for r in rows if r["end"] == "Done" and r["done_day"] <= d]
        burn.append({"day": d, "date": "đầu sprint" if d == 0 else str(SIM["workdays"][d - 1]),
                     "ideal_swp": round(tot_swp * (1 - d / n), 1), "left_swp": tot_swp - sum(r["swp"] for r in done),
                     "done_count": len(done)})
    status = defaultdict(lambda: {"count": 0, "swp": 0, "h": 0, "keys": []})
    for r in rows:
        s = status[r["end"]]
        s["count"] += 1; s["swp"] += r["swp"]; s["h"] += r["h"]; s["keys"].append(r["key"])
    return {"iteration": SIM["iteration"], "start": str(SIM["start"]), "end": str(SIM["end_date"]), "goal": SIM["goal"],
            "capacity_note": SIM["capacity_note"], "total_swp": tot_swp, "total_h": tot_h,
            "left_h_end": sum(r["h"] if r["end"] != "Done" and "left_h" not in r else r.get("left_h", 0) for r in rows),
            "load_by_owner": dict(sorted(load_by_owner.items())), "status": dict(status), "burn": burn, "rows": rows}


def svg(s):
    W, H, L, B, T, R = 640, 340, 56, 48, 36, 24
    n, top = len(s["burn"]) - 1, s["total_swp"]
    x = lambda d: L + d * (W - L - R) / n
    y = lambda v: T + (1 - v / top) * (H - T - B)
    pts = lambda key: " ".join(f"{x(b['day']):.1f},{y(b[key]):.1f}" for b in s["burn"])
    grid = "".join(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#e5e7eb"/>'
                   f'<text x="{L - 8}" y="{y(v) + 4:.1f}" text-anchor="end" font-size="11" fill="#6b7280">{v}</text>'
                   for v in range(0, top + 1, max(1, top // 5)))
    ticks = "".join(f'<text x="{x(b["day"]):.1f}" y="{H - B + 18}" text-anchor="middle" font-size="11" fill="#6b7280">'
                    f'{"0" if b["day"] == 0 else b["date"][8:] + "/" + b["date"][5:7]}</text>' for b in s["burn"])
    dots = "".join(f'<circle cx="{x(b["day"]):.1f}" cy="{y(b["left_swp"]):.1f}" r="3" fill="#2563eb"/>' for b in s["burn"])
    last = s["burn"][-1]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="sans-serif">
<rect width="{W}" height="{H}" fill="#ffffff"/>
<text x="{L}" y="20" font-size="14" font-weight="bold" fill="#111827">{s["iteration"]} (giả lập) — SWP còn lại · {s["start"]} → {s["end"]}</text>
{grid}{ticks}
<polyline points="{pts("ideal_swp")}" fill="none" stroke="#9ca3af" stroke-width="2" stroke-dasharray="6 4"/>
<polyline points="{pts("left_swp")}" fill="none" stroke="#2563eb" stroke-width="2.5"/>{dots}
<text x="{x(n) - 4:.1f}" y="{y(last["left_swp"]) + 20:.1f}" text-anchor="end" font-size="12" fill="#2563eb">còn {last["left_swp"]} SWP</text>
<rect x="{W - 214}" y="30" width="190" height="40" fill="#ffffff" stroke="#e5e7eb"/>
<line x1="{W - 204}" x2="{W - 180}" y1="44" y2="44" stroke="#9ca3af" stroke-width="2" stroke-dasharray="6 4"/>
<text x="{W - 174}" y="48" font-size="11" fill="#374151">Lý tưởng</text>
<line x1="{W - 204}" x2="{W - 180}" y1="60" y2="60" stroke="#2563eb" stroke-width="2.5"/>
<text x="{W - 174}" y="64" font-size="11" fill="#374151">Thực tế (tính khi Done)</text>
<text x="{(L + W - R) / 2:.0f}" y="{H - 8}" text-anchor="middle" font-size="11" fill="#6b7280">Ngày làm việc</text>
</svg>
'''


def apply(s):
    sync = import_module("sync-backlog-to-github")
    st = sync.load_state()
    flds = {f["name"]: f for f in sync.gh("project", "field-list", str(st["project_number"]), "--owner", sync.OWNER,
                                          "--format", "json", "--limit", "50")["fields"]}
    it_field = sync.gql('query($id: ID!) { node(id: $id) { ... on ProjectV2IterationField { id configuration { iterations { id title } } } } }',
                        id=flds["Iteration"]["id"])["node"]
    sprint = next(i["id"] for i in it_field["configuration"]["iterations"] if i["title"] == s["iteration"])
    opt = {o["name"]: o["id"] for o in flds["Status"]["options"]}
    done = st.setdefault("sprint_done", {})
    for r in s["rows"]:
        if done.get(r["key"]) == r["end"]:
            continue
        item = st["items"][r["key"]]
        sync.gh("project", "item-edit", "--id", item, "--project-id", st["project_id"], "--field-id", flds["Iteration"]["id"],
                "--iteration-id", sprint, "--format", "json")
        sync.gh("project", "item-edit", "--id", item, "--project-id", st["project_id"], "--field-id", flds["Status"]["id"],
                "--single-select-option-id", opt[r["end"]], "--format", "json")
        if r["end"] == "Done":
            sync.gh("issue", "close", str(st["issues"][r["key"]]["number"]), "-R", sync.FULL, "--reason", "completed", parse=False)
        done[r["key"]] = r["end"]
        st["status_set_by_sprint"] = True
        sync.save_state(st)
        print(f"{len(done)}/{len(s['rows'])} {r['key']} → {r['end']}", flush=True)
    print("sprint ok:", len(s["rows"]), "items")


if __name__ == "__main__":
    s = build()
    SVG.parent.mkdir(exist_ok=True)
    SVG.write_text(svg(s))
    SUMMARY.write_text(json.dumps(s, ensure_ascii=False, indent=1, default=str))
    print("items", len(s["rows"]), "SWP", s["total_swp"], "h", s["total_h"], "| load", s["load_by_owner"])
    print({k: (v["count"], v["swp"]) for k, v in s["status"].items()}, "| cuối:", s["burn"][-1])
    if "--apply" in sys.argv:
        apply(s)
