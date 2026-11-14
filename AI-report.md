# Báo cáo dùng AI — LAB-5

Product B · Yuki Cold Chain WMS/TMS. Công cụ: Claude Code (agent chính) cùng các skill Takumi `tkm:*`, sub-agent và GitHub CLI `gh`. PL (học viên) quyết định ở các bước ghi trong mục 2. Nhật ký chi tiết từng bước: [data/ai-usage-log.md](./data/ai-usage-log.md).

## 1. Skill và prompt theo từng việc

| Việc | Skill / công cụ | Prompt / cách giao việc (rút gọn) | Đầu ra |
|---|---|---|---|
| Đọc đề, lên plan | Agent chính + memory LAB-1…4 | "Đọc lại LAB 1–4, đọc kỹ đề LAB-5 rồi lên plan". AI trích checklist đề ra `00-lab5-brief.md` và hỏi PL 4 quyết định: phạm vi, cách ước giờ, người phụ trách, ngôn ngữ báo cáo | Plan 8 bước + bảng quyết định PL |
| Break task | Agent chính, đọc LAB-4 (G-xx, Q-xx, TECH, api-list) và WBS JSON của LAB-1 | "Mỗi issue phải có mã nguồn LAB-4 / LAB-1 (cấm bịa), mỗi task LAB-1 thuộc đúng 1 epic hoặc có lý do nằm ngoài". Viết 1 file nguồn `backlog-source.yaml`, script `check-backlog-coverage.py` kiểm độ phủ | 15 epic, 179 issue; 0 lỗi độ phủ: 36/36 gap; 12/12 câu hỏi khách có chỗ xử lý (11 issue hỏi khách, Q6 hỏi khi viết spec E13-01) |
| Ước giờ | Agent chính + module `backlog_estimate_rules.py` | Bản đầu ước giờ "code thuần". AI tự cảnh báo số đó lạc quan (42% LAB-1). PL chọn ước lại theo DoD: hệ số test / tích hợp / review theo nhóm việc, việc lá ≤ 24h | 5172h; phần chi tiết bằng 70% LAB-1, có giải thích từng epic |
| Đưa lên GitHub | `gh` + GraphQL, script `sync-backlog-to-github.py` (setup / issues / fields, chạy lại an toàn) | Tạo repo + Project public, labels, field, Iteration 6 sprint (Sprint 7–9 thêm sau), 194 issue, sub-issue 3 tầng (REST `sub_issues`), field Giờ / Phụ trách / Loại / Ràng buộc | Project 194 item, 4 view (`create-project-views.py`) |
| Chấm SWP | Skill **`tkm:estimate-swp --level medium`** + skill `tkm:confidence` | Skill tự đọc Project (chỉ query, mỗi lệnh qua bộ chặn `tool_policy.py`), chọn 157 việc lá, chia 5 lô. **5 agent chấm song song**; mỗi agent chỉ đọc brief + rubric + file lô và ghi file kết quả. Validator của skill kiểm hợp đồng → chọn 5 mẫu → PL review → hiệu chỉnh → xuất HTML | `reports/estimate-swp-…html`: 753 → 780 SWP |
| Ghi SWP lên Project | **Script riêng** `write-swp-to-project.py`, chạy sau khi skill xong | Skill chỉ được đọc nên không ghi. Script lấy payload JSON nhúng trong HTML đã validate, map `issueRef → item`, ghi field `SWP` cho 194 item (việc lá = SWP chốt, cha / epic = tổng con), có đánh dấu để chạy tiếp khi đứt mạng. Sau đó AI đọc lại Project để đối chiếu tổng | 194/194 item có SWP, tổng epic 780 = HTML |
| Quy ra giờ | Module ước giờ + đối chiếu SWP | Không nhân SWP với hệ số. Tính trung vị giờ / SWP, liệt kê issue lệch quá 2 lần để PL xử lý | estimate.md §3 |
| Báo cáo tiến độ | Agent chính, script `simulate-sprint-1-burndown.py` | AI dựng kịch bản Sprint 1 trong `sprint-1-simulation.yaml`. Script kiểm trần giờ từng người, tính burndown chỉ khi Done, vẽ SVG, đặt Iteration / Status trên Project, rồi tính dự báo năng lực tới mốc 2027-04-02 | progress-report.md + tóm tắt tiếng Nhật |
| Render tài liệu | Template md + `render-repo-markdown.py` | Mọi bảng và tổng số sinh từ nguồn. `[#92](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/92) E06-10` tự thành link `#số` | 6 file md ở gốc repo |

## 2. Review đầu ra AI

| Bước | Ai review | Vấn đề phát hiện | Xử lý |
|---|---|---|---|
| Plan | PL | AI phát hiện skill SWP chỉ đọc, không ghi Project | Thêm bước script ghi SWP riêng |
| Ước giờ | AI tự cảnh báo, PL quyết | Bản đầu chỉ bằng 42% LAB-1: thiếu công test, tích hợp, review | PL chọn ước lại theo DoD. Thêm quy tắc hệ số, tách 3 issue > 24h |
| PREMISE | AI tự kiểm bằng script | **AI tính nhẩm sai 3 con số giờ** (44h → 38h, ≈59h → 42h, 4h → 7h) | Quy tắc mới: số trong md chỉ lấy từ script |
| Đồng bộ GitHub | AI đếm lại item thật trên Project | Lỗi mạng bị `\| tail` che exit code: script báo xong nhưng mới 169/194 | Thêm thử lại khi lỗi mạng, đánh dấu item đã ghi, in tiến độ |
| Năng lực công cụ | PL hỏi lại | AI khẳng định sai "gh chưa tạo được view" dựa trên hiểu biết cũ | Kiểm schema GraphQL thật, tạo được view; chỉ nhóm / tổng là phải bật tay |
| Chấm SWP | Validator của skill → **PL review 5 mẫu** | Worker trả `splitReason: ""` thay vì null; 11 issue hỏi khách + 1 spike bị xếp Unknown nhưng độ tin cậy medium; quy tắc lan truyền từ issue thô kéo theo 2 màn hình chi tiết | Chuẩn hoá theo hợp đồng (điểm không đổi), ghi caveat trong HTML và estimate.md. PL nâng 2 / 5 mẫu |
| Đối chiếu SWP ↔ giờ | AI liệt kê, PL quyết | Màn hình: giờ cao hơn SWP một cách có hệ thống; E07-01 giờ có thể thiếu | Giữ giờ màn hình (có lý do). E07-01 thành rủi ro R8 |
| Báo cáo tiến độ | AI tự soát + script | Kịch bản làm lộ 2 lỗi lập kế hoạch có thật: E06-04 phụ thuộc E01-05a trong cùng sprint; toàn bộ E06 dồn cho BE-2 | Ghi vào phần giải thích burndown và rủi ro R3 |
| Tài liệu cuối | Agent review độc lập (vai PL khó tính, không xem kết luận của agent chính) | 25 điểm (5 nặng). Số liệu md = Project = YAML đều khớp. Lỗi nằm ở: placeholder chưa điền; câu "đã kiểm HTTP 200" viết khi repo còn rỗng; tóm tắt tiếng Nhật giấu chuyện thiếu năng lực và nói quá ("入荷検品完了", "スパイク完了"); công viết spec 49 màn hình không có ngân sách; dự báo năng lực tính TL / BrSE 100% và chưa trừ ngày nghỉ; kịch bản sprint mâu thuẫn A1; issue Done chưa tick tiêu chí; mã lỗi M_RT_05 trùng nghĩa; bỏ 29 API mà không ghi PREMISE | Sửa 22/25: tóm tắt JA nêu thẳng "余裕がありません", dùng số issue thay SWP, chuyển xuống phụ lục; PREMISE S3 đổi sang M_RT_21, thêm S7 (29 API), S5 ghi ngân sách spec 48 MD; dự báo theo nhân sự P2 LAB-1 (9,4 người) trừ Tết / 1/1, có 2 kịch bản; tick tiêu chí + comment 27 issue Done; kịch bản E06-03 khớp A1. Mã học viên đã điền, đã mở ẩn danh OK. Còn lại; Sprint 7–9 thêm sau; script trong repo không tự chạy được (đã ghi ở README) |

**Tự đánh giá báo cáo tiến độ do AI tổng hợp: có tô hồng hay bỏ sót không (P2-11, P2-13)**

- *Chống tô hồng:* burndown chỉ trừ SWP khi issue Done, không tính phần trăm làm dở. Dự báo đặt cạnh nhau năng lực theo nhân sự LAB-1 và nhịp thật của Sprint 1 (228h Done, 30% năng lực). Muốn kịp mốc 2027-04-02 thì từ Sprint 2 phải đạt ≥ 89% năng lực. Báo cáo ghi thẳng "mốc chưa an toàn" thay vì "đúng tiến độ 75%". Bản đầu, tóm tắt tiếng Nhật vẫn tô hồng (giấu chuyện thiếu năng lực, nói "完了" quá mức). Review độc lập bắt được lỗi này, và nó đã được sửa trước khi nộp.
- *Chống bỏ sót:* trạng thái và con số trong báo cáo được script đọc lại từ Project sau khi ghi, gồm 35 item và 110 SWP. Việc chờ khách tách riêng thành Blocked chứ không gộp vào "đang làm".
- *Giới hạn còn lại:* kịch bản sprint do AI dựng nên không có dữ liệu "trễ thật" để kiểm velocity. Tóm tắt tiếng Nhật do AI viết và chưa có người bản ngữ soát.

**Quality gate trước khi gửi (P2-12):** AI đạt khi script kiểm độ phủ báo 0 lỗi, validator SWP pass, số đọc lại từ Project khớp md, và review độc lập không còn lỗi nặng. Người đạt khi PL đã chốt 5 mẫu SWP và rủi ro R1–R8 có người phụ trách cùng ngày. Thiếu một trong hai thì chưa gửi báo cáo cho khách.

## 3. Điểm đặc biệt

| Loại | Nội dung |
|---|---|
| Hiệu quả | Một file nguồn YAML → issue, field, bảng md, link `#số`. Sửa một chỗ thì render lại hết, không lệch số giữa md và Project. 5 agent chấm SWP song song mất khoảng 5 phút cho 157 issue. Toàn bộ script chạy lại an toàn khi mạng chập chờn |
| Hiệu quả | Skill SWP chọn mẫu theo luật cố định, nên PL chỉ trả lời 10 câu thay vì soát 157 issue. Xoá dòng giờ trước khi chấm giúp SWP thành phép đối chiếu độc lập thật |
| Chưa tốt | **Thời gian:** ghi field lên GitHub chậm (194 item × 4–5 lệnh), mạng đứt làm mất gần gấp đôi. Nên gom bằng GraphQL batch. **Token:** đọc LAB-4 nhiều lần qua các phiên; nên tóm tắt LAB-4 thành 1 file chỉ mục sớm hơn |
| Chưa tốt | SWP không phù hợp với issue thô: một issue gom 6–9 màn hình vẫn bị chấm theo bậc của một issue (11 giờ / SWP so với 2,8). Lan truyền "cùng nhóm" từ issue thô sang màn hình chi tiết là tác dụng phụ. Lần sau nên chấm issue thô ở một lượt riêng hoặc tách trước khi chấm |
| Chưa tốt | AI vẫn mắc lỗi khẳng định chắc chắn mà không kiểm (view GitHub, tính nhẩm). Cách chữa hiệu quả nhất là bắt mọi con số đi qua script và kiểm schema / API thật trước khi nói "không làm được" |
| Chưa có ý tưởng | Chưa có cách tự động đo độ chính xác của SWP khi chưa có dữ liệu sprint thật. Cần 2–3 sprint thật để hiệu chỉnh giờ / SWP |
