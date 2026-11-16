# Ước lượng — SWP (đã review) và giờ

Product B · Yuki Cold Chain WMS/TMS · Project: [https://github.com/users/nguhdd-3772/projects/1](https://github.com/users/nguhdd-3772/projects/1)

Mỗi issue có hai con số: **giờ ước lượng**, dùng để lập kế hoạch và so với LAB-1, và **SWP** (Standard Work Point) để đối chiếu. Cả hai đã ghi vào field `Giờ ước lượng` và `SWP` trên Project cho đủ 179 issue và 15 epic. Issue cha và epic lấy tổng của con. Tổng toàn bộ backlog: **5172h (646,5 MD)** và **780 SWP**. Trong 780 SWP, chỉ **465 SWP** của phần chi tiết E01–E10 dùng để đo velocity. Phần còn lại là SWP của issue thô E11–E15, chỉ để tham khảo cho tới khi issue được tách (§3).

## 1. Báo cáo HTML của skill chấm SWP

- File trong repo: [reports/estimate-swp-yuki-cold-chain-backlog-p2-20261114.html](./reports/estimate-swp-yuki-cold-chain-backlog-p2-20261114.html)
- Xem trực tuyến (GitHub Pages): [https://nguhdd-3772.github.io/yuki-cold-chain-lab5-backlog/reports/estimate-swp-yuki-cold-chain-backlog-p2-20261114.html](https://nguhdd-3772.github.io/yuki-cold-chain-lab5-backlog/reports/estimate-swp-yuki-cold-chain-backlog-p2-20261114.html)
- Skill `tkm:estimate-swp`, mức xử lý `medium`, chạy ngày 2026-11-14. Skill đọc thẳng Project, chấm 157 việc lá (5 lô, mỗi lô một agent độc lập), cộng dồn lên 37 issue cha / epic, chọn 5 issue mẫu cho PL review rồi hiệu chỉnh. Tổng SWP việc lá: **753 → 780** sau review.
- Trước khi gửi issue cho skill, dòng "Giờ ước lượng" đã bị xoá khỏi nội dung issue. Nhờ vậy SWP chấm độc lập với giờ và dùng để đối chiếu được.
- Skill chỉ **đọc** Project, không ghi. SWP sau review được ghi lên field `SWP` bằng một script riêng (`scripts/write-swp-to-project.py`, xem AI-report.md). Script này đọc payload đã kiểm trong file HTML, không nhập số tay.

## 2. Issue mẫu skill chọn để PL kiểm

Skill chọn theo quy tắc cố định: nhỏ nhất, trung vị, lớn nhất, lệch xa trung vị, độ tin cậy thấp nhất. PL review từng issue qua 2 vòng: chọn mức khó (rất dễ 1–2 · dễ 3–5 · vừa 6–12 · khó 13–25 · rất khó 26+), rồi chọn điểm cụ thể. Số giờ hiện kèm để PL đối chiếu.

Cột Scope × Complexity là **tra bảng**, không phải phép nhân. Scope chọn trong {1, 2, 3, 5, 8, 13}, Complexity trong {0, 1, 2, 3, 5, 8}, rồi tra ma trận cố định của skill: SWP = Scope × hệ số của bậc Complexity (×1 … ×5), làm tròn. Ví dụ 3 × 2 → 3 × 1,5 → 5 (làm tròn từ 4,5).

| Issue | Vì sao skill chọn | Skill chấm (Scope × Complexity → SWP) | Bạn chốt | Lý do |
|---|---|---|---|---|
| [#11](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/11) E01-03a [Hỏi khách] Q10 — giữ phân quyền × dải nhiệt trong P1 hay lù | nhỏ nhất | 1 × 0 → **1** | 1 × 0 → **1** | Giữ: chỉ hỏi 1 câu và ghi vào Q&A list, không có code |
| [#24](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/24) E02-01a Hàm Postgres confirm_receiving_line() trong 1 transaction +  | trung vị | 3 × 2 → **5** | 5 × 2 → **8** | Nâng lên mức vừa: phần khó là transaction + mã không trùng khi nhiều request song song; skill chỉ tính 1 hàm DB + 1 API |
| [#156](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/156) E11-08 Vận hành tuyến và POD: sự cố, lịch trình tài xế, sự kiện tuy | lớn nhất | 8 × 3 → **16** | 13 × 2 → **20** | Nâng: nhóm màn hình vận hành tuyến / POD có đồng bộ offline, rộng hơn skill chấm |
| [#153](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/153) E11-05 Tồn kho: cất hàng, di chuyển, vùng nhiệt tạm, kiểm kê, tra c | lệch xa trung vị | 8 × 2 → **12** | 8 × 2 → **12** | Giữ: nhiều màn hình nhưng chuyển trạng thái tồn kho là mẫu quen; giờ thật nằm ở cột giờ (MD LAB-1) |
| [#100](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/100) E06-13 Màn hình S-MS-08 bộ quy tắc giờ lái (phiên bản) — chưa có sp | độ tin cậy thấp nhất | 2 × 1 → **3** | 2 × 1 → **3** | Giữ: 1 màn hình, dùng lại khung chính sách E01-05; độ tin cậy thấp vì chưa có spec |

PL chọn "áp cho issue tương tự", nên skill dịch đúng số bậc cho các issue **cùng nhóm**: cùng discipline, cùng loại việc, cùng dấu hiệu phạm vi và độ khó, so khớp chính xác chứ không theo độ giống tiêu đề. Có 9 issue đổi theo cách này:

| Issue | SWP skill → sau hiệu chỉnh | Theo quy tắc |
|---|---|---|
| [#130](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/130) E08-08b Form chuyển bước điều tra → khắc phục → quyết định → đó | 5 → 6 | cal-002 |
| [#137](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/137) E09-03b Cây quan hệ xuôi / ngược + đánh dấu điểm đứt chuỗi | 5 → 6 | cal-002 |
| [#149](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/149) E11-01 Chung: trang chủ theo vai trò, người dùng và phân quyền | 8 → 10 | cal-002 |
| [#151](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/151) E11-03 Master chính sách nhiệt độ / HACCP và đề xuất thay đổi  | 8 → 10 | cal-002 |
| [#152](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/152) E11-04 Nhập hàng: lịch hẹn xe nhập, kết quả nhập và duyệt chên | 8 → 10 | cal-002 |
| [#154](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/154) E11-06 Đơn hàng: danh sách, nhập / sửa, nhập CSV, sổ lịch sử g | 12 → 16 | cal-002 |
| [#155](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/155) E11-07 Xuất kho: nhiệm vụ lấy hàng, quét lấy hàng, xếp xe và 出 | 8 → 10 | cal-002 |
| [#157](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/157) E11-09 Nhiệt độ / HACCP: nhập CSV, diễn biến nhiệt, vệ sinh, h | 12 → 16 | cal-002 |
| [#158](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/158) E11-10 Thu hồi: case thu hồi, đối soát số lượng, thông báo thu | 8 → 10 | cal-002 |

Quy tắc `cal-001` (nhóm DB / sửa lỗi / xuyên tầng / song song) không khớp issue nào khác, nên chỉ đổi đúng E02-01a. Quy tắc `cal-002` (UI / tính năng / xuyên tầng / có trạng thái) kéo theo 7 issue thô E11 và 2 màn hình chi tiết ([#130](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/130) E08-08b, [#137](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/137) E09-03b: 5 → 6). Hai màn hình này giữ điểm sau hiệu chỉnh. Lý do: cùng nhóm với E11-08 theo luật so khớp của skill, và đều là màn hình nhiều bước trạng thái (điều tra → khắc phục → đóng; cây xuôi / ngược có điểm đứt). Sửa tay ngoài skill sẽ làm hỏng audit trong HTML. Tác dụng phụ "lan từ issue thô sang issue chi tiết" được ghi ở AI-report.md để lần sau chấm issue thô ở lượt riêng.

## 3. Cách quy ra giờ

| Mục | Nội dung |
|---|---|
| Cách chọn | **Ước giờ trực tiếp cho từng việc lá theo định nghĩa xong (DoD)**, không lấy SWP nhân hệ số. SWP chỉ để đối chiếu và tìm chỗ lệch |
| Vì sao | (1) Chưa có velocity thật của đội để quy SWP ra giờ; nhân với một hệ số tự đặt thì giờ chỉ là SWP đổi đơn vị. (2) Giờ phải so được với MD của LAB-1. (3) SWP gom vài ý vào một bậc (1, 2, 3, 5, 8…), không đủ mịn cho issue 4–24h |
| Quy tắc | `giờ = ceil(giờ code × (1 + Σ hệ số))`, hệ số theo nhóm việc: BE có tích hợp `test 0,40 + tích hợp 0,20 + review 0,15` · BE thuần `test 0,40 + review 0,15` · FE có API `test 0,20 + tích hợp 0,30 + review 0,15` · FE thuần `test 0,20 + review 0,15` · issue test `chạy lại sau sửa 0,25` · hỏi khách / spike: không cộng. Việc lá ≤ 24h, quá thì tách. Issue thô: giờ = MD LAB-1 × 8. Issue cha = tổng con |
| Áp dụng nhất quán | Quy tắc nằm trong `backlog-source.yaml` (`meta.estimate_rule`), một module duy nhất tính giờ cho mọi bảng và mọi issue (`backlog_estimate_rules.py`). Mỗi issue trên GitHub ghi rõ cách ra giờ, ví dụ `14h = code 8 + test 3,2 + tích hợp 1,6 + review 1,2`. Có ghi đè thì bắt buộc kèm lý do (`override_why`). Script kiểm độ phủ báo lỗi nếu việc lá > 24h |
| Đối chiếu SWP ↔ giờ | Trung vị phần chi tiết: **2,8 giờ / SWP**. Issue thô là **11,0 giờ / SWP**, vì một issue thô gom cả nhóm màn hình mà SWP chỉ chấm theo dải bậc. Nên **không dùng SWP issue thô để dự báo** trước khi tách. Các issue lệch quá 2 lần trung vị (bỏ câu hỏi khách, vì SWP nhỏ nhất là 1): |

| Issue | Loại | Giờ | SWP | Giờ / SWP | Xử lý |
|---|---|---|---|---|---|
| [#8](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/8) E01-02b Loại vai trò DEMO khỏi build production | gap | 4 | 3 | 1.3 | Lệch nhỏ, việc theo mẫu lặp lại (sinh ma trận quyền / bỏ vai trò DEMO): giữ giờ |
| [#9](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/9) E01-02c Test ma trận 11 vai trò × trang × API sinh từ role | test | 8 | 6 | 1.3 | Lệch nhỏ, việc theo mẫu lặp lại (sinh ma trận quyền / bỏ vai trò DEMO): giữ giờ |
| [#29](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/29) E02-02a Form kiểm dòng nhập + validation theo spec | feat | 20 | 3 | 6.7 | Giữ giờ: skill coi 1 màn hình là phạm vi nhỏ, chưa tính tích hợp FE–API (+30%) và các trạng thái lỗi M_xx |
| [#31](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/31) E02-02c Hiển thị kết quả HELD / cách ly và thông báo M_RC | feat | 7 | 1 | 7.0 | Giữ giờ: skill coi 1 màn hình là phạm vi nhỏ, chưa tính tích hợp FE–API (+30%) và các trạng thái lỗi M_xx |
| [#53](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/53) E04-05 Màn hình S-OD-04 引当実行・結果 | feat | 24 | 4 | 6.0 | Giữ giờ: skill coi 1 màn hình là phạm vi nhỏ, chưa tính tích hợp FE–API (+30%) và các trạng thái lỗi M_xx |
| [#63](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/63) E05-03a Interface adapter + bản travel_times cho test | gap | 11 | 1 | 11.0 | Giữ giờ: interface + bộ travel_times giả cho test lập tuyến; dùng chung cho 4 issue E05/E06 |
| [#94](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/94) E06-11a Dòng thời gian + tô khoảng vi phạm ERROR / WARN | feat | 20 | 3 | 6.7 | Giữ giờ: skill coi 1 màn hình là phạm vi nhỏ, chưa tính tích hợp FE–API (+30%) và các trạng thái lỗi M_xx |
| [#102](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/102) E07-01 Transaction complete_delivery(): POD + sổ giao + t | feat | 14 | 10 | 1.4 | Giờ có thể thiếu: 4 thao tác ghi trong 1 transaction (so với E02-01a 18h). Ước lại khi lập kế hoạch sprint có E07 |

Kết luận đối chiếu: giờ ước cho màn hình cao hơn SWP một cách có hệ thống. Lý do là skill tính một màn hình là phạm vi nhỏ, còn quy tắc giờ cộng 30% tích hợp FE–API. PL giữ giờ. Ba issue có giờ thấp hơn SWP là E01-02b, E01-02c, E07-01. Hai issue E01-02 lệch nhỏ (1,3 giờ / SWP) và là việc lặp lại theo mẫu, nên giữ. **E07-01** lệch rõ nhất (4 thao tác ghi trong một transaction), ghi thành rủi ro R8 để ước lại trước khi kéo vào sprint (progress-report.md §4).

## 4. Tổng theo epic

| Epic | Số issue (việc lá) | Tổng SWP | Tổng giờ | MD | Ghi chú |
|---|---|---|---|---|---|
| [#1](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/1) E01 Nền tảng chung — mã lỗi, phân quyền, audit, chín | 20 (16) | 61 | 177 | 22.1 |  |
| [#22](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/22) E02 Nhập hàng và kiểm hàng (入荷検品) | 12 (10) | 31 | 109 | 13.6 |  |
| [#35](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/35) E03 Tồn kho và trạng thái chất lượng (品質ステータス) | 6 (5) | 16 | 64 | 8.0 |  |
| [#42](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/42) E04 Phân bổ và quy tắc hạn dùng (消費期限 / 1/3 / 日付逆転 / | 14 (12) | 51 | 163 | 20.4 | Quy tắc phân bổ đã có code + 10 unit test ở prototype LAB-2 |
| [#57](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/57) E05 Lập tuyến — bảng tuyến, thao tác tuyến, bản đồ,  | 16 (13) | 51 | 166 | 20.8 |  |
| [#74](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/74) E06 Ràng buộc giờ lái xe tải 2024 (改善基準告示) — tách ri | 26 (22) | 83 | 279 | 34.9 | Ràng buộc đặc thù; gồm spike + 2 câu hỏi khách |
| [#101](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/101) E07 Giao hàng và POD (納品・POD登録) | 16 (14) | 68 | 176 | 22.0 |  |
| [#118](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/118) E08 Nhiệt độ và HACCP (ロガー取込・アラーム・逸脱) | 13 (11) | 47 | 144 | 18.0 | Quy tắc nhiệt độ đã có code ở prototype LAB-2 |
| [#132](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/132) E09 Truy xuất nguồn gốc (トレース検索) | 7 (6) | 33 | 89 | 11.1 |  |
| [#140](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/140) E10 Duyệt bởi người thứ hai (二者承認) | 7 (6) | 24 | 69 | 8.6 |  |
| [#148](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/148) E11 Màn hình và xử lý nền LAB-1 chưa có spec LAB-4 ( | 10 (10) | 124 | 1768 | 221.0 | Issue thô: SWP chưa có nghĩa đến khi tách |
| [#159](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/159) E12 Báo cáo và kiểm toán F10 (issue thô) | 7 (7) | 36 | 560 | 70.0 | Issue thô: giờ = MD LAB-1 × 8 |
| [#167](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/167) E13 Liên kết ERP và chuyển đổi dữ liệu F12 / F13 (is | 6 (6) | 46 | 432 | 54.0 | Issue thô: giờ = MD LAB-1 × 8 |
| [#174](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/174) E14 Hạ tầng và nền tảng chưa có spec (SSO, thiết bị, | 9 (9) | 54 | 440 | 55.0 | Issue thô: giờ = MD LAB-1 × 8 |
| [#184](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/184) E15 Kiểm thử hệ thống P2 (issue thô) | 10 (10) | 55 | 536 | 67.0 | Issue thô: giờ = MD LAB-1 × 8 |
| **Tổng** | **179 (157)** | **780** | **5172** | **646.5** | |

Số issue tính cả issue cha. Trong ngoặc là số việc lá, tức số issue được chấm SWP trực tiếp. Phần chi tiết E01–E10 có **465 SWP**.

## 5. So với LAB-1

LAB-1 ước cả dự án là **1.424 MD**. Backlog LAB-5 thay **722 MD** trong số đó. Phần còn lại không chia thành issue sản phẩm (xem các dòng "Ngoài backlog").

(*) Lý do chung: LAB-1 làm tròn lên MD theo từng vai trò của mỗi task + buffer 15%; LAB-5 ước giờ từng việc lá đã có spec, buffer để ở dự phòng M.*.

| Phần | LAB-1 | LAB-5 | Chênh | Vì sao |
|---|---|---|---|---|
| [#1](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/1) E01 | 29 MD | 22.1 MD | -6.9 MD | Chung (*). LAB-4 gộp mã lỗi / phân quyền / audit thành quy ước chung; thêm khung chính sách có phiên bản; phân quyền × dải nhiệt 4 sub-issue E01-03 theo PREMISE S6 |
| [#22](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/22) E02 | 17 MD | 13.6 MD | -3.4 MD | Chung (*). Prototype LAB-2 đã có màn hình kiểm nhập + quy tắc nhiệt độ nhập (96 dòng); LAB-5 sửa theo gap |
| [#35](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/35) E03 | 10 MD | 8.0 MD | -2.0 MD | Chung (*). Phạm vi rõ sau S-IV-04: 1 bảng chuyển trạng thái + 1 màn hình |
| [#42](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/42) E04 | 41 MD | 20.4 MD | -20.6 MD | Prototype đã có allocation-rules-engine (117 dòng) + 10 unit test; LAB-1 tính QA 11 MD, LAB-5 còn 2 issue test (30h) |
| [#57](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/57) E05 | 26 MD | 20.8 MD | -5.2 MD | Chung (*). Adapter bản đồ tách thành interface + bản giả cho test, nhà cung cấp thật 1 issue; thêm publish song song → 409 (E05-06, +7h) theo PREMISE S3 |
| [#74](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/74) E06 | 34 MD | 34.9 MD | +0.9 MD | Cao hơn: thêm 4 ngưỡng kỳ (G-31), gợi ý chèn nghỉ (PREMISE S1), spike luật, seed nhiều ngày; prototype chỉ kiểm theo ngày |
| [#101](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/101) E07 | 28 MD | 22.0 MD | -6.0 MD | Chung (*). POD offline tách 4 sub-issue; bằng chứng theo hợp đồng chờ Q1 |
| [#118](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/118) E08 | 38 MD | 18.0 MD | -20.0 MD | Prototype đã có quy tắc nhiệt độ + nhập CSV logger; LAB-5 sửa định nghĩa duration_min / SLA (gap) và làm case sai lệch |
| [#132](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/132) E09 | 19 MD | 11.1 MD | -7.9 MD | Prototype đã có màn hình + API truy xuất; LAB-5 làm lại bộ máy xuôi / ngược, hiệu năng, lô con (PREMISE S2) |
| [#140](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/140) E10 | 13 MD | 8.6 MD | -4.4 MD | Chung (*). Khung duyệt dùng chung cho 6 loại, chỉ cấu hình ma trận người duyệt |
| **Chi tiết E01–E10** | **255 MD** | **179,5 MD** | **−75,5 MD (70%)** | Thấp hơn chủ yếu ở E04 / E08 / E09, nơi prototype LAB-2 đã có code và test. Phần chênh còn lại vẫn nằm trong dự phòng M.* của LAB-1, chưa trả lại khách |
| Issue thô E11–E15 | 467 MD | 467 MD | 0 | Chưa có spec, giữ nguyên MD LAB-1 (PREMISE S5) |
| Ngoài backlog: Thiết kế cơ bản P1 | 136 MD | — | — | giai đoạn P1 (2026-10-05 → 11-27) đã kết thúc, kết quả là bộ spec LAB-4 (10 màn hình ★, kiến trúc, DB, API); thiết kế 49 màn hình còn lại nằm trong phần design 48 MD của issue thô (PREMISE S5) |
| Ngoài backlog: Onboarding, họp tuần, demo, steering | 51 MD | — | — | overhead quản lý, theo dõi ngoài backlog sản phẩm |
| Ngoài backlog: Hỗ trợ UAT, sửa lỗi UAT, gói nghiệm thu | 31 MD | — | — | thuộc P3, lập backlog khi vào P3 |
| Ngoài backlog: Diễn tập chuyển đổi, cutover, đào tạo | 125 MD | — | — | thuộc P3/P4 |
| Ngoài backlog: PM/BrSE/TL overhead và dự phòng 20% | 359 MD | — | — | không chia thành issue; dự phòng dùng khi Q chưa trả lời làm phình issue |
| **Tổng phần backlog thay thế** | **722 MD** | **646,5 MD** | **−75,5 MD** | Chưa đề xuất giảm giá với khách: phần chi tiết mới chiếm 28% giờ backlog (179,5 / 646,5 MD); chờ thêm 2–3 sprint velocity thật |

Thay đổi so với LAB-4 có ảnh hưởng tới giờ:

- [PREMISE S1](./PREMISE.md): thêm [#92](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/92) E06-10 (+14h).
- PREMISE S2: thêm [#138](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/138) E09-05 (+11h).
- PREMISE S3: thêm [#71](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/71) E05-06 (+7h).
- PREMISE S6: phân quyền × dải nhiệt nằm ở [#11](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/11) E01-03a / [#12](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/12) E01-03b / [#13](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/13) E01-03d / [#14](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/14) E01-03c.

Toàn bộ các thay đổi trên đều đã nằm trong số giờ của bảng.
