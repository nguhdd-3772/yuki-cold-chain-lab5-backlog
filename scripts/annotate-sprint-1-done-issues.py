#!/usr/bin/env python3
"""Đóng vòng DoD cho issue Done của Sprint 1 giả lập: tick tiêu chí nghiệm thu + 1 comment kết quả.

Nguồn: working/sprint-1-simulation.yaml (done_day, note). Idempotent: state['annotated'][key].
Chạy: python3 working/scripts/annotate-sprint-1-done-issues.py
"""
from importlib import import_module

import yaml

from backlog_estimate_rules import LAB5

sync = import_module("sync-backlog-to-github")
SIM = yaml.safe_load((LAB5 / "working" / "sprint-1-simulation.yaml").read_text())
DEFAULT = {"clarify": "Khách trả lời theo phương án mặc định ghi trong issue; đã ghi vào Q&A list, PREMISE / spec không đổi.",
           "other": "Code + unit test + review xong theo DoD, CI xanh."}


def main():
    st = sync.load_state()
    done = st.setdefault("annotated", {})
    items = [x for x in SIM["items"] if x["end"] == "Done"]
    for x in items:
        key = x["key"]
        if done.get(key):
            continue
        num = str(st["issues"][key]["number"])
        body = sync.gh("issue", "view", num, "-R", sync.FULL, "--json", "body")["body"]
        sync.gh("issue", "edit", num, "-R", sync.FULL, "--body", body.replace("- [ ]", "- [x]"), parse=False)
        kind = "clarify" if "[Hỏi khách]" in sync.gh("issue", "view", num, "-R", sync.FULL, "--json", "title")["title"] else "other"
        day = SIM["workdays"][x["done_day"] - 1]
        note = x.get("note") or DEFAULT[kind]
        sync.gh("issue", "comment", num, "-R", sync.FULL, "--body",
                f"**Sprint 1 (giả lập cho LAB-5)** — Done ngày {day}.\n\n{note}", parse=False)
        done[key] = True
        sync.save_state(st)
        print(f"{len(done)}/{len(items)} {key}", flush=True)
    print("annotate ok:", len(items))


if __name__ == "__main__":
    main()
