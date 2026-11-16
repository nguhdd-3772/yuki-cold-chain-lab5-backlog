# Yuki Cold Chain WMS/TMS — Backlog, ước lượng và báo cáo tiến độ (LAB-5)

| Dự án | Mã học viên | Đề |
|---|---|---|
| Yuki Cold Chain WMS/TMS (hệ thống kho lạnh và vận tải, khách hư cấu) | B123772 | Product B — LAB-5: break thiết kế LAB-4 thành backlog trên GitHub Project, ước lượng SWP + giờ, báo cáo tiến độ 1 sprint giả lập |

> Toàn bộ nội dung do học viên tự viết cho khoá học. Khách hàng, dữ liệu và tình huống đều là giả lập. Repo không chép RFP, không có dữ liệu thật, dữ liệu cá nhân hay khoá bí mật.

## 1. Tổng quan

| Mục | Nội dung |
|---|---|
| Break từ | Bộ spec **LAB-4, bản nộp 2026-11-11**: 10 spec màn hình, 6 TECH, 35 API, 11 ADR, gap G-01 … G-36, câu hỏi khách Q1 … Q12 |
| PREMISE có đổi không | **Có.** 6 chỗ sửa spec (S1–S6), 7 giả định (A1–A7), 7 hướng đã chốt. Các chỗ đổi đều phát hiện khi break. Đáng chú ý nhất: S1 (gợi ý chèn nghỉ, LAB-1 đã báo giá nhưng LAB-4 bỏ rơi) và S5 (49 màn hình chưa có spec thành issue thô). Xem [PREMISE.md](./PREMISE.md) |
| Backlog | **15 epic · 179 issue / sub-issue** (157 việc lá, trong đó 43 issue thô chưa có spec) · **780 SWP · 5172h (646,5 MD)** |
| Ràng buộc đặc thù | Giới hạn giờ lái xe tải từ 2024 (改善基準告示) tách thành epic riêng [#74](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/74) E06, nhãn `constraint:driver-2024` |
| Sprint giả lập | **Sprint 1** (2026-11-30 → 2026-12-11): cam kết 110 SWP, xong 82 SWP (75%), xem [progress-report.md](./progress-report.md) |

## 2. Link

| Mục | Link |
|---|---|
| Repo | [https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog) |
| GitHub Project | [https://github.com/users/nguhdd-3772/projects/1](https://github.com/users/nguhdd-3772/projects/1), có 4 view: Backlog · Sprint 1 · Giờ lái 2024 · Lịch sprint |
| Báo cáo HTML chấm SWP | File: [reports/estimate-swp-yuki-cold-chain-backlog-p2-20261114.html](./reports/estimate-swp-yuki-cold-chain-backlog-p2-20261114.html) · xem trực tuyến: [GitHub Pages](https://nguhdd-3772.github.io/yuki-cold-chain-lab5-backlog/reports/estimate-swp-yuki-cold-chain-backlog-p2-20261114.html) |
| Kiểm tra truy cập công khai | Repo, Project và trang Pages đã mở thử bằng **cửa sổ ẩn danh** (không đăng nhập), xem được đầy đủ — 2026-11-14. Kiểm thêm bằng request không đăng nhập: cả 4 link trả HTTP 200. |

## 3. Cấu trúc repo

| File / thư mục | Nội dung |
|---|---|
| `README.md` | File này: tổng quan, link, cấu trúc, Spec → epic |
| `PREMISE.md` | Spec thêm / bỏ / sửa so với LAB-4, giả định bổ sung, hướng đã chốt |
| `task-breakdown.md` | Nguyên tắc chia task + DoD, Spec → issue, ràng buộc giờ lái 2024, chỗ hở LAB-4 phát hiện khi break |
| `estimate.md` | Issue mẫu đã review SWP, cách quy ra giờ, tổng theo epic, so với LAB-1 |
| `progress-report.md` | Báo cáo Sprint 1 giả lập (có tóm tắt tiếng Nhật cho khách): trạng thái, burndown, rủi ro trễ |
| `AI-report.md` | Skill / prompt đã dùng, bước người review, vấn đề phát hiện, điểm cần cải thiện |
| `reports/` | Báo cáo HTML của skill chấm SWP + biểu đồ burndown (SVG) |
| `scripts/` | Bản copy các script đã dùng: sinh issue / field, tạo view, ghi SWP, giả lập sprint, render md. Chạy trong thư mục làm việc gốc của học viên (cần WBS LAB-1); để trong repo cho người đọc audit cách ra số |
| `data/` | File nguồn duy nhất của backlog (`backlog-source.yaml`), kịch bản Sprint 1 (`sprint-1-simulation.yaml`), nhật ký dùng AI theo từng bước (`ai-usage-log.md`) |
| `index.html` | Trang mở đầu của GitHub Pages, trỏ tới báo cáo HTML |
| `.gitignore` | Bỏ qua file tạm (`__pycache__`, `.DS_Store`) |

## 4. Spec → epic

| Spec (LAB-4 / PREMISE) | Epic | Ghi chú |
|---|---|---|
| S-RC-02_SPEC (入荷検品) | [#22](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/22) E02 — Nhập hàng và kiểm hàng |  |
| RECV_INSPECT_TECH · API-RC-02 | [#1](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/1) E01 — Nền tảng chung, [#22](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/22) E02 — Nhập hàng và kiểm hàng |  |
| S-IV-04_SPEC (品質ステータス) | [#35](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/35) E03 — Tồn kho và trạng thái chất lượng |  |
| S-OD-04_SPEC (引当実行・結果) | [#42](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/42) E04 — Phân bổ và quy tắc hạn dùng |  |
| ALLOC_RUN_TECH · API-OD-04 | [#42](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/42) E04 — Phân bổ và quy tắc hạn dùng |  |
| S-RT-01_SPEC (配車計画ボード) | [#57](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/57) E05 — Lập tuyến |  |
| S-RT-02-03_SPEC (改善基準チェック結果・ルート版履歴) | [#57](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/57) E05 — Lập tuyến, [#74](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/74) E06 — Ràng buộc giờ lái xe tải 2024 | Ràng buộc đặc thù: giờ lái 2024 |
| ROUTE_CHECK_TECH · API-RT-02 | [#57](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/57) E05 — Lập tuyến, [#74](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/74) E06 — Ràng buộc giờ lái xe tải 2024 | Ràng buộc đặc thù: giờ lái 2024 |
| S-DR-03_SPEC (納品・POD登録) | [#101](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/101) E07 — Giao hàng và POD |  |
| POD_COMPLETE_TECH · API-DR-02 | [#101](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/101) E07 — Giao hàng và POD |  |
| S-TP-02-03_SPEC (アラーム対応キュー・再測定) | [#118](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/118) E08 — Nhiệt độ và HACCP |  |
| S-TP-04_SPEC (逸脱ケース) | [#118](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/118) E08 — Nhiệt độ và HACCP |  |
| TEMP_IMPORT_TECH · API-TP-02 | [#1](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/1) E01 — Nền tảng chung, [#118](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/118) E08 — Nhiệt độ và HACCP |  |
| S-TR-01_SPEC (トレース検索) | [#132](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/132) E09 — Truy xuất nguồn gốc |  |
| S-CM-03_SPEC (承認待ち一覧・承認) | [#140](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/140) E10 — Duyệt bởi người thứ hai |  |
| APPROVAL_DECIDE_TECH · API-CM-03 | [#140](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/140) E10 — Duyệt bởi người thứ hai |  |
| _common: api-conventions · error-codes · common-spec | [#1](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/1) E01 — Nền tảng chung |  |
| _common: api-list (35 API) | [#1](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/1) E01 — Nền tảng chung |  |
| _common: YUKI_DESIGN (kiến trúc, NFR) | [#101](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/101) E07 — Giao hàng và POD, [#132](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/132) E09 — Truy xuất nguồn gốc |  |
| ADR-001 … ADR-011 | [#1](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/1) E01 — Nền tảng chung, [#22](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/22) E02 — Nhập hàng và kiểm hàng, [#42](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/42) E04 — Phân bổ và quy tắc hạn dùng, [#57](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/57) E05 — Lập tuyến, [#74](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/74) E06 — Ràng buộc giờ lái xe tải 2024, [#101](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/101) E07 — Giao hàng và POD, [#118](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/118) E08 — Nhiệt độ và HACCP, [#140](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/140) E10 — Duyệt bởi người thứ hai, [#148](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/148) E11 — Màn hình và xử lý nền LAB-1 chưa có spec LAB-4, [#167](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/167) E13 — Liên kết ERP và chuyển đổi dữ liệu F12 / F13, [#174](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/174) E14 — Hạ tầng và nền tảng chưa có spec |  |
| Database design: 5 file YUKI_*_DB + _er-overview | [#22](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/22) E02 — Nhập hàng và kiểm hàng, [#35](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/35) E03 — Tồn kho và trạng thái chất lượng, [#42](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/42) E04 — Phân bổ và quy tắc hạn dùng, [#57](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/57) E05 — Lập tuyến, [#74](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/74) E06 — Ràng buộc giờ lái xe tải 2024, [#118](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/118) E08 — Nhiệt độ và HACCP |  |
| Gap G-01 … G-36 | [#1](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/1) E01 — Nền tảng chung, [#22](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/22) E02 — Nhập hàng và kiểm hàng, [#35](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/35) E03 — Tồn kho và trạng thái chất lượng, [#42](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/42) E04 — Phân bổ và quy tắc hạn dùng, [#57](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/57) E05 — Lập tuyến, [#74](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/74) E06 — Ràng buộc giờ lái xe tải 2024, [#101](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/101) E07 — Giao hàng và POD, [#118](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/118) E08 — Nhiệt độ và HACCP, [#132](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/132) E09 — Truy xuất nguồn gốc, [#140](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/140) E10 — Duyệt bởi người thứ hai, [#167](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/167) E13 — Liên kết ERP và chuyển đổi dữ liệu F12 / F13 |  |
| Câu hỏi khách Q1 … Q12 | [#1](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/1) E01 — Nền tảng chung, [#22](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/22) E02 — Nhập hàng và kiểm hàng, [#42](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/42) E04 — Phân bổ và quy tắc hạn dùng, [#57](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/57) E05 — Lập tuyến, [#74](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/74) E06 — Ràng buộc giờ lái xe tải 2024, [#101](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/101) E07 — Giao hàng và POD, [#140](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/140) E10 — Duyệt bởi người thứ hai, [#167](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/167) E13 — Liên kết ERP và chuyển đổi dữ liệu F12 / F13 |  |
| PREMISE S1 (gợi ý chèn nghỉ) | [#74](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/74) E06 | Ràng buộc đặc thù: giờ lái 2024 |
| PREMISE S2 (truy xuất lô con) | [#132](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/132) E09 |  |
| PREMISE S5 (49 màn hình chưa spec → issue thô) | [#148](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/148) E11, [#159](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/159) E12, [#167](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/167) E13, [#174](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/174) E14, [#184](https://github.com/nguhdd-3772/yuki-cold-chain-lab5-backlog/issues/184) E15 |  |
