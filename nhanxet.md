# Báo cáo Phân tích "Data Leakage" (Lạm phát AUC) trên các tập dữ liệu Knowledge Tracing

## 1. Bối cảnh
Trong quá trình thực nghiệm baseline cho các tập dữ liệu Knowledge Tracing (KT), hệ thống ghi nhận sự chênh lệch lớn về điểm số AUC giữa các dataset:
- **Junyi** và **ASSISTments 2012**: AUC của các mô hình Deep Learning (DKT, AKT, GKT...) cao bất thường, đạt ngưỡng **~0.96 đến 0.98**.
- **XES3G5M**: AUC nằm ở mức bình thường và thực tế, dao động khoảng **~0.83 đến 0.87**.
- Tuy nhiên, mô hình **Classical BKT** (sử dụng thuật toán EM/L-BFGS-B truyền thống) lại cho ra mức AUC hoàn toàn bình thường trên cả Junyi (~0.779) và ASSISTments 2012 (~0.668).

## 2. Kết quả Điều tra Source Code
Quá trình rà soát file tiền xử lý `src/preprocess.py` và thuật toán chia Fold `src/split_checker.py` khẳng định **không có lỗi (bug) trong pipeline**:
- Thuật toán chia tập Train/Valid/Test (`learner_based_split`) phân tách người dùng (users) một cách hoàn toàn độc lập. Tập người dùng dùng để huấn luyện và tập kiểm thử không hề có sự trùng lặp (disjoint sets).
- Các luật mapping `item_id` và `kc_id` đều được tuân thủ đúng theo chuẩn cấu trúc của từng Dataset.

## 3. Bản chất của hiện tượng lạm phát AUC (Sequence Autocorrelation)
Nguyên nhân thực sự dẫn đến mức AUC 0.98 không phải do lỗi rò rỉ dữ liệu (data leakage) giữa tập Train/Test, mà là do **đặc thù lặp lại chuỗi (sequence autocorrelation)** cực kỳ cao bên trong cấu trúc của bản thân các dataset này:

### A. Hiện tượng "Mastery Learning" trên Junyi
- Khi phân tích file parquet của Junyi, hệ thống phát hiện có tới **74.75%** số bản ghi là các trường hợp học sinh giải **đi giải lại một bài tập (cùng `item_id` và `kc_id`) nhiều lần liên tiếp**.
- Junyi Academy hoạt động dựa trên cơ chế Mastery Learning, yêu cầu học sinh phải làm đúng $N$ câu liên tiếp của cùng một dạng bài để qua môn. Điều này tạo ra một chuỗi dữ liệu dài gồm các tương tác giống hệt nhau, với cùng một kết quả trả lời đúng (correct = 1).

### B. Cơ chế "Multi-skill Mapping" trên ASSISTments 2012
- Trên tập ASSISTments 2012, một câu hỏi (problem_id) có thể liên kết với nhiều kỹ năng (skill_id) cùng lúc.
- Khi dữ liệu được bung ra (unroll), nó tạo thành các dòng liên tiếp có chung kết quả trả lời. Thống kê cho thấy có tới **47.7%** các tương tác trong ASSISTments 2012 là lặp lại kỹ năng (KC) ở ngay câu tiếp theo.

## 4. Giải thích hiệu ứng trên các mô hình
- **Deep Learning (DKT, AKT, GKT...)**: Các mô hình này có tính biểu diễn chuỗi rất mạnh. Chúng dễ dàng học được một heuristic cực kỳ đơn giản: *"Nếu câu hỏi/kỹ năng ở bước tiếp theo giống hệt bước hiện tại, chỉ việc copy nguyên xi kết quả (thường là correct=1) của bước hiện tại"*. Việc "học vẹt" này quá dễ dàng, kéo AUC lên tới 0.98.
- **Classical BKT**: Mô hình BKT truyền thống mô phỏng xác suất chuyển trạng thái kiến thức qua từng kỹ năng độc lập. Do bị giới hạn bởi các tham số trượt (Slip) và đoán (Guess), xác suất mà BKT dự đoán bị "chạm trần" (thường không vượt quá $1 - Slip$). Do đó, nó không thể đưa ra dự đoán tiệm cận 1.0 như Deep Learning, phản ánh đúng điểm số AUC thực tế là ~0.779.
- **XES3G5M**: Tập dữ liệu này đã được chuẩn hóa theo cấp độ chuỗi thực tế, không có hiện tượng lặp lại câu hỏi liên tiếp một cách máy móc, do đó AUC của các mô hình Deep Learning trả về mức thực tế ~0.83 - 0.87.

## 5. Kết luận
Mức AUC ~0.98 không phải là kết quả của một lỗi lập trình, mà nó phản ánh một điểm yếu phổ biến trong các bộ dữ liệu KT hiện nay (Sequence Autocorrelation). Đây là một minh chứng xuất sắc để đưa vào bài báo nghiên cứu (paper) nhằm thảo luận về tác động của các tương tác lặp lại (Repetitive Interactions) đối với hiệu suất của các mô hình Deep Learning trong lĩnh vực Knowledge Tracing.
