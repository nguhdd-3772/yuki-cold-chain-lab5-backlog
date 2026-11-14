#!/usr/bin/env python3
"""Đồng bộ backlog-source.yaml lên GitHub: repo public, labels, Project public + fields, issue / sub-issue.

Idempotent: ánh xạ key → issue / item lưu ở working/github-sync-state.json; chạy lại chỉ tạo phần còn thiếu
và cập nhật field Giờ / Phụ trách / Loại / Ràng buộc. SWP, Status, Iteration KHÔNG ghi ở đây (bước 4, 6).

Chạy: python3 working/scripts/sync-backlog-to-github.py setup|issues|fields
"""
import json
import subprocess
import sys
import time

from backlog_estimate_rules import LAB5, breakdown, hours, load, rule_group, walk

OWNER, REPO = "nguhdd-3772", "yuki-cold-chain-lab5-backlog"
FULL = f"{OWNER}/{REPO}"
PROJECT_TITLE = "Yuki Cold Chain WMS/TMS — Backlog P2 (LAB-5)"
STATE = LAB5 / "working" / "github-sync-state.json"
STATUSES = [("Backlog", "GRAY"), ("Ready", "BLUE"), ("In progress", "YELLOW"),
            ("In review", "PURPLE"), ("Done", "GREEN"), ("Blocked", "RED")]
SPRINTS = [("Sprint 1", "2026-11-30"), ("Sprint 2", "2026-12-14"), ("Sprint 3", "2026-12-28"),
           ("Sprint 4", "2027-01-11"), ("Sprint 5", "2027-01-25"), ("Sprint 6", "2027-02-08")]
KIND_LABEL = {"feat": "kind:feat", "gap": "kind:gap", "test": "kind:test", "clarify": "kind:clarify",
              "spike": "kind:spike", "coarse": "kind:coarse"}
LABELS = {"epic": "5319e7", "kind:feat": "1d76db", "kind:gap": "fbca04", "kind:test": "0e8a16",
          "kind:clarify": "c5def5", "kind:spike": "d93f0b", "kind:coarse": "bfdadc",
          "constraint:driver-2024": "b60205", "needs-spec": "e4e669"}


NET_ERRORS = ("can't assign requested address", "error connecting", "internet connection", "timeout", "timed out",
              "tcp ", "connection reset", "EOF", "502", "503", "504", "secondary rate")


def gh(*args, parse=True, tries=7):
    for attempt in range(tries):
        out = subprocess.run(["gh", *args], capture_output=True, text=True)
        if not out.returncode:
            return json.loads(out.stdout) if parse and out.stdout.strip() else out.stdout
        if attempt < tries - 1 and any(e in out.stderr for e in NET_ERRORS):
            time.sleep(5 * (attempt + 1))  # lỗi mạng / rate limit tạm thời: chờ rồi thử lại
            continue
        raise RuntimeError(f"gh {' '.join(args[:4])} …: {out.stderr.strip()}")


def gql(query, **vars):
    args = ["api", "graphql", "-f", f"query={query}"]
    for k, v in vars.items():
        args += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
    return gh(*args)["data"]


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {"issues": {}, "items": {}}


def save_state(st):
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1))


# ─────────────────────────── setup ───────────────────────────
def setup(st):
    try:
        gh("repo", "view", FULL, "--json", "name")
    except RuntimeError:
        gh("repo", "create", FULL, "--public", "--description",
           "LAB-5 Product B (giả lập): backlog, ước lượng, báo cáo tiến độ cho hệ thống kho lạnh hư cấu Yuki", parse=False)
    existing = {l["name"] for l in gh("label", "list", "-R", FULL, "--json", "name", "--limit", "100")}
    for name, color in LABELS.items():
        if name not in existing:
            gh("label", "create", name, "-R", FULL, "--color", color, parse=False)

    if "project_id" not in st:
        p = gh("project", "create", "--owner", OWNER, "--title", PROJECT_TITLE, "--format", "json")
        st.update(project_id=p["id"], project_number=p["number"], project_url=p["url"])
        save_state(st)
    num = str(st["project_number"])
    gh("project", "edit", num, "--owner", OWNER, "--visibility", "PUBLIC", "--format", "json")
    gh("project", "link", num, "--owner", OWNER, "--repo", FULL, parse=False)

    fields = {f["name"]: f for f in gh("project", "field-list", num, "--owner", OWNER, "--format", "json", "--limit", "50")["fields"]}
    meta = load()[0]["meta"]
    wanted = {"Phụ trách (giả định)": ("SINGLE_SELECT", meta["owners"]),
              "Loại": ("SINGLE_SELECT", ["epic", "feat", "gap", "test", "clarify", "spike", "coarse"]),
              "Ràng buộc đặc thù": ("SINGLE_SELECT", ["Giờ lái 2024"]),
              "SWP": ("NUMBER", None), "Giờ ước lượng": ("NUMBER", None)}
    for name, (dtype, opts) in wanted.items():
        if name not in fields:
            args = ["project", "field-create", num, "--owner", OWNER, "--name", name, "--data-type", dtype, "--format", "json"]
            if opts:
                args += ["--single-select-options", ",".join(opts)]
            gh(*args)

    status = fields["Status"]
    if [o["name"] for o in status.get("options", [])] != [s for s, _ in STATUSES]:
        opts = ", ".join(f'{{name: "{n}", color: {c}, description: ""}}' for n, c in STATUSES)
        gql(f'mutation($id: ID!) {{ updateProjectV2Field(input: {{fieldId: $id, singleSelectOptions: [{opts}]}}) '
            f'{{ projectV2Field {{ ... on ProjectV2SingleSelectField {{ id }} }} }} }}', id=status["id"])

    if "Iteration" not in fields:
        its = ", ".join(f'{{title: "{t}", startDate: "{d}", duration: 14}}' for t, d in SPRINTS)
        gql(f'mutation($p: ID!) {{ createProjectV2Field(input: {{projectId: $p, dataType: ITERATION, name: "Iteration", '
            f'iterationConfiguration: {{startDate: "{SPRINTS[0][1]}", duration: 14, iterations: [{its}]}}}}) '
            f'{{ projectV2Field {{ ... on ProjectV2IterationField {{ id }} }} }} }}', p=st["project_id"])
    print("setup ok:", st["project_url"])


# ─────────────────────────── issues ───────────────────────────
def body(it, src, lab1, epic, parent):
    lines = [f"**Mã backlog:** `{it['key']}` · **Epic:** {epic['key']} — {epic['title']}"]
    if parent:
        lines.append(f"**Issue cha:** `{parent['key']}`")
    if it.get("desc"):
        lines += ["", it["desc"]]
    if it.get("ac"):
        lines += ["", "**Tiêu chí nghiệm thu**", *[f"- [ ] {a}" for a in it["ac"]]]
    if it.get("subs"):
        lines += ["", "**Sub-issue**", *[f"- `{s['key']}` {s['title']}" for s in it["subs"]]]
    lines += ["", f"**Nguồn (LAB-4 / LAB-1):** {', '.join(it.get('refs', []))}"]
    if it.get("lab1"):
        lines.append(f"**Task LAB-1 thay thế:** {', '.join(it['lab1'])}")
    h = hours(it, src, lab1)
    if it.get("subs"):
        lines.append(f"**Giờ ước lượng:** {h}h (tổng sub-issue)")
    elif it["kind"] == "coarse":
        lines += [f"**Giờ ước lượng:** {h}h = MD LAB-1 × 8 (chưa có spec, chưa tách)",
                  "**Điều kiện vào sprint:** có spec BM-51 và đã tách thành issue ≤ 24h"]
    else:
        parts = breakdown(it, src["meta"]["estimate_rule"])
        lines.append(f"**Giờ ước lượng:** {h}h = " + " + ".join(f"{k} {v:g}" for k, v in parts.items() if v) +
                     f" (nhóm `{rule_group(it)}`, làm tròn lên)")
    lines.append(f"**Phụ trách (giả định):** {it.get('owner', '—')}")
    return "\n".join(lines)


def epic_body(ep, src, lab1):
    h = sum(hours(i, src, lab1) for i in ep["issues"])
    lines = [f"**Epic `{ep['key']}`** · Giờ ước lượng: {h}h ({h / 8:.1f} MD)", "",
             f"**Nguồn LAB-4:** {', '.join(ep.get('refs', []))}"]
    if ep.get("lab1"):
        lines.append(f"**Task LAB-1 thay thế:** {', '.join(ep['lab1'])}")
    if ep.get("constraint"):
        lines += ["", "> Ràng buộc đặc thù của đề: giới hạn giờ lái xe tải từ 2024 (改善基準告示). Tách riêng khỏi epic lập tuyến E05."]
    if ep.get("coarse"):
        lines += ["", "> Issue thô: chưa có spec LAB-4, giờ giữ nguyên MD LAB-1 × 8. Không kéo vào sprint trước khi có spec."]
    lines += ["", "**Issue**", *[f"- `{i['key']}` {i['title']}" for i in ep["issues"]]]
    return "\n".join(lines)


def create_issue(st, key, title, text, labels):
    if key in st["issues"]:
        return st["issues"][key]
    url = gh("issue", "create", "-R", FULL, "--title", title, "--body", text,
             *sum((["--label", l] for l in labels), []), parse=False).strip()
    num = int(url.rsplit("/", 1)[1])
    info = gh("api", f"repos/{FULL}/issues/{num}")
    st["issues"][key] = {"number": num, "id": info["id"], "node_id": info["node_id"], "url": url}
    save_state(st)
    time.sleep(1.2)  # tránh secondary rate limit khi tạo nội dung
    return st["issues"][key]


def link_sub(st, parent_key, child_key):
    links = st.setdefault("sub_links", [])
    if [parent_key, child_key] in links:
        return
    p, c = st["issues"][parent_key], st["issues"][child_key]
    gh("api", "-X", "POST", f"repos/{FULL}/issues/{p['number']}/sub_issues", "-F", f"sub_issue_id={c['id']}")
    links.append([parent_key, child_key])
    save_state(st)


def issues(st):
    src, lab1 = load()
    for ep in src["epics"]:
        labels = ["epic"] + (["constraint:driver-2024"] if ep.get("constraint") else [])
        create_issue(st, ep["key"], f"[{ep['key']}] {ep['title']}", epic_body(ep, src, lab1), labels)
        for it, parent in walk(ep["issues"]):
            labels = [KIND_LABEL[it["kind"]]]
            if ep.get("constraint") or "DRIVER-2024" in it.get("refs", []):
                labels.append("constraint:driver-2024")
            if it["kind"] == "coarse":
                labels.append("needs-spec")
            create_issue(st, it["key"], f"[{it['key']}] {it['title']}", body(it, src, lab1, ep, parent), labels)
            link_sub(st, parent["key"] if parent else ep["key"], it["key"])
        print(ep["key"], "ok")


# ─────────────────────────── fields ───────────────────────────
def fields(st):
    src, lab1 = load()
    num = str(st["project_number"])
    flds = {f["name"]: f for f in gh("project", "field-list", num, "--owner", OWNER, "--format", "json", "--limit", "50")["fields"]}
    opt = lambda f, name: next(o["id"] for o in flds[f]["options"] if o["name"] == name)

    def set_field(item, fname, **val):
        args = ["project", "item-edit", "--id", item, "--project-id", st["project_id"], "--field-id", flds[fname]["id"]]
        args += ["--number", str(val["number"])] if "number" in val else ["--single-select-option-id", val["option"]]
        gh(*args, "--format", "json")

    rows = []
    for ep in src["epics"]:
        rows.append((ep["key"], "epic", None, sum(hours(i, src, lab1) for i in ep["issues"]), ep.get("constraint")))
        for it, _ in walk(ep["issues"]):
            drv = ep.get("constraint") or "DRIVER-2024" in it.get("refs", [])
            rows.append((it["key"], it["kind"], it.get("owner"), hours(it, src, lab1), drv))
    for key, kind, owner, h, drv in rows:
        if key not in st["items"]:
            st["items"][key] = gh("project", "item-add", num, "--owner", OWNER, "--url", st["issues"][key]["url"], "--format", "json")["id"]
            save_state(st)
        done = st.setdefault("fields_done", {})
        if done.get(key) == h:
            continue
        item = st["items"][key]
        set_field(item, "Giờ ước lượng", number=h)
        set_field(item, "Loại", option=opt("Loại", kind))
        if owner:
            set_field(item, "Phụ trách (giả định)", option=opt("Phụ trách (giả định)", owner))
        if drv:
            set_field(item, "Ràng buộc đặc thù", option=opt("Ràng buộc đặc thù", "Giờ lái 2024"))
        if not st.get("status_set_by_sprint"):
            set_field(item, "Status", option=opt("Status", "Backlog"))
        done[key] = h
        save_state(st)
        print(f"{len(done)}/{len(rows)} {key}", flush=True)
    print("fields ok:", len(rows), "items")


if __name__ == "__main__":
    st = load_state()
    {"setup": setup, "issues": issues, "fields": fields}[sys.argv[1]](st)
