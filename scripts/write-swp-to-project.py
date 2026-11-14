#!/usr/bin/env python3
"""Ghi SWP đã review (từ báo cáo HTML của tkm:estimate-swp) lên field `SWP` của GitHub Project.

Nguồn duy nhất: payload JSON nhúng trong reports/estimate-swp-*.html (đã validate + calibrate).
Việc lá = finalSWP; issue cha / epic = tổng con (finalSWP của container do skill cộng sẵn).
Idempotent: state['swp_done'][key] = giá trị đã ghi; chạy lại chỉ ghi phần thiếu / khác.
Chạy: python3 working/scripts/write-swp-to-project.py <đường dẫn report.html>
"""
import json
import re
import sys
from importlib import import_module

sync = import_module("sync-backlog-to-github")


def payload_from_report(path):
    html = open(path, encoding="utf-8").read()
    m = re.search(r'<script[^>]*application/json[^>]*>(.*?)</script>', html, re.S)
    return json.loads(m.group(1))


def main(report):
    p = payload_from_report(report)
    st = sync.load_state()
    num_to_key = {v["number"]: k for k, v in st["issues"].items()}
    swp = {}
    for row in p["issues"] + p["parents"]:
        val = row.get("finalSWP")
        if val is None:
            sys.exit(f"thiếu SWP: {row['issueRef']} ({row.get('aggregationStatus')})")
        swp[num_to_key[int(row["issueRef"].rsplit("#", 1)[1])]] = val
    missing = set(st["items"]) - set(swp)
    if missing:
        sys.exit(f"item chưa có SWP: {sorted(missing)}")

    fid = next(f["id"] for f in sync.gh("project", "field-list", str(st["project_number"]), "--owner", sync.OWNER,
                                         "--format", "json", "--limit", "50")["fields"] if f["name"] == "SWP")
    done = st.setdefault("swp_done", {})
    for i, (key, val) in enumerate(sorted(swp.items()), 1):
        if done.get(key) == val:
            continue
        sync.gh("project", "item-edit", "--id", st["items"][key], "--project-id", st["project_id"],
                "--field-id", fid, "--number", str(val), "--format", "json")
        done[key] = val
        sync.save_state(st)
        print(f"{i}/{len(swp)} {key}={val}", flush=True)
    epics = {k: v for k, v in swp.items() if re.fullmatch(r"E\d\d", k)}
    print("swp ok:", len(swp), "items · tổng epic =", sum(epics.values()))


if __name__ == "__main__":
    main(sys.argv[1])
