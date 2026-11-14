#!/usr/bin/env python3
"""Tạo / cập nhật 4 view của GitHub Project (idempotent theo tên view).

API (createProjectV2View / updateProjectV2View) đặt được: tên, layout, filter, cột hiển thị.
Nhóm theo epic (group by Parent issue) và hiện tổng (field sum) API chưa hỗ trợ → bật tay trên web.
Chạy: python3 working/scripts/create-project-views.py
"""
import json

from importlib import import_module

sync = import_module("sync-backlog-to-github")
OWNER, gh, gql = sync.OWNER, sync.gh, sync.gql

COLS = ["Title", "Status", "Iteration", "Phụ trách (giả định)", "SWP", "Giờ ước lượng", "Loại",
        "Ràng buộc đặc thù", "Parent issue", "Sub-issues progress"]
VIEWS = [  # (tên, layout, filter, đổi tên từ view mặc định)
    ("Backlog", "TABLE_LAYOUT", "", "View 1"),
    ("Sprint 1", "BOARD_LAYOUT", 'iteration:"Sprint 1"', None),
    ("Giờ lái 2024", "TABLE_LAYOUT", "label:constraint:driver-2024", None),
    ("Lịch sprint", "ROADMAP_LAYOUT", "has:iteration", None),
]


def main():
    st = sync.load_state()
    proj = gql('query($o: String!, $n: Int!) { user(login: $o) { projectV2(number: $n) { '
               'views(first: 20) { nodes { id name } } '
               'fields(first: 50) { nodes { ... on ProjectV2FieldCommon { id name } } } } } }',
               o=OWNER, n=st["project_number"])["user"]["projectV2"]
    views = {v["name"]: v["id"] for v in proj["views"]["nodes"]}
    fid = {f["name"]: f["id"] for f in proj["fields"]["nodes"] if f}
    for name, layout, flt, rename_from in VIEWS:
        cfg = "" if layout == "ROADMAP_LAYOUT" else f", configuration: {{visibleFieldIds: {json.dumps([fid[c] for c in COLS])}}}"  # roadmap không nhận cột
        vid = views.get(name) or views.get(rename_from or "")
        if not vid:
            vid = gql(f'mutation($p: ID!, $n: String!) {{ createProjectV2View(input: {{projectId: $p, name: $n, '
                      f'layout: {layout}{cfg}}}) '
                      f'{{ projectV2View {{ id }} }} }}', p=st["project_id"], n=name)["createProjectV2View"]["projectV2View"]["id"]
        gql(f'mutation($v: ID!, $n: String!, $f: String!) {{ updateProjectV2View(input: {{viewId: $v, name: $n, '
            f'layout: {layout}, filter: $f{cfg}}}) {{ projectV2View {{ id }} }} }}',
            v=vid, n=name, f=flt)
        print("view ok:", name)


if __name__ == "__main__":
    main()
