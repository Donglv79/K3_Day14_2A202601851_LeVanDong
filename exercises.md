# Day 14 — Exercises

## AI Evaluation & Benchmarking · Lab Worksheet

## Part 1 — Warm-up

### Exercise 1.1 — RAGAS Metric Thresholds

| Metric | Acceptable low score | Critical low score | Action |
|---|---|---|---|
| Faithfulness (bám bằng chứng) | Câu hỏi mở cần diễn giải nhưng vẫn phải có citation/evidence | Câu trả lời có claim không xuất hiện trong context | Kiểm tra grounding và retrieved chunks |
| Answer Relevance (liên quan câu hỏi) | Câu hỏi mơ hồ, cần câu trả lời có điều kiện | Trả lời chủ đề khác hoặc không trả lời ý chính | Sửa prompt và intent routing |
| Context Recall (lấy đủ bằng chứng) | Câu hỏi chỉ cần một phần tài liệu | Bỏ sót điều kiện, ngoại lệ hoặc ngày hiệu lực | Tăng top-k, cải thiện chunking/retrieval |
| Context Precision (xếp hạng bằng chứng) | Có một ít chunk nhiễu nhưng chunk đúng vẫn đứng đầu | Chunk đúng đứng sau nhiều nhiễu | Rerank và giảm source repetition |
| Completeness (đầy đủ) | Câu hỏi chỉ yêu cầu một fact nhỏ | Bỏ sót điều kiện, phí, deadline hoặc ngoại lệ quan trọng | Cải thiện prompt và kiểm tra checklist ý bắt buộc |

Điểm dưới 0.6 được xem là vấn đề đáng điều tra; 0.6–0.8 cần cải thiện; 0.8–1.0 có thể tiếp tục theo dõi.

### Exercise 1.2 — Bias trong LLM-as-a-Judge

**Câu 1 — Experiment phát hiện position bias (thiên lệch vị trí):**

Chuẩn bị nhiều cặp answer có chất lượng đã biết. Chạy cùng một cặp hai lần: lần đầu đặt Answer A trước B, lần sau đảo thành B trước A. Giữ nguyên question và rubric. Nếu một answer thường được điểm cao hơn khi đứng trước, đó là dấu hiệu position bias. Có thể mở rộng bằng cách randomize (xáo trộn) vị trí nhiều lần và so sánh điểm trung bình.

**Câu 2 — Giảm verbosity bias (thiên lệch vì câu trả lời dài):**

Rubric phải chấm đúng claim và evidence, không chấm số từ. Quy định câu trả lời ngắn nhưng đủ ý có thể đạt điểm tối đa; phạt thông tin lặp lại, lan man hoặc không có bằng chứng. Cho judge biết không được dùng độ dài làm proxy cho correctness.

**Câu 3 — Vì sao cần calibrate (hiệu chỉnh) với human labels (nhãn của con người):**

LLM judge có thể chấm lệch hoặc thay đổi giữa các lần chạy. So sánh với nhãn của người giúp phát hiện bias, điều chỉnh rubric và chọn threshold phù hợp trước khi dùng làm quality gate (cổng kiểm soát chất lượng).

### Exercise 1.3 — Evaluation trong CI/CD

| Metric | Threshold đề xuất | Lý do |
|---|---:|---|
| Faithfulness | 0.70 | Hallucination gây rủi ro trực tiếp; bản release không nên giảm grounding nghiêm trọng |
| Answer Relevance | 0.60 | Cho phép câu hỏi mơ hồ nhưng vẫn phải trả lời đúng chủ đề |
| Completeness | 0.60 | Đảm bảo không bỏ sót policy, deadline, phí hoặc điều kiện quan trọng |

Offline evaluation (đánh giá ngoại tuyến) chạy trước mỗi release hoặc prompt change vì nhanh và lặp lại được. Online evaluation (đánh giá trực tuyến) theo dõi traffic thật sau deploy. Human review (đánh giá con người) dùng cho high-stakes cases, calibration và các failure mà heuristic không giải thích đủ.

## Part 2 — Core Coding

Đã hoàn thiện các phần bắt buộc trong `template.py` và sao chép sang `solution/solution.py`:

- `QAPair`, `EvalResult`, `overall_score()`.
- Ba answer metrics (metric đánh giá câu trả lời).
- Context Recall và Context Precision (metric đánh giá retrieval — truy xuất tài liệu).
- `BenchmarkRunner`, regression detection và failure filtering.
- `FailureAnalyzer`.
- `LLMJudge` với JSON parsing, fallback score và bias checks.

Kết quả kiểm thử:

```text
41 passed, 1 skipped
```

Test bị skip là `rerank_by_overlap`, một phần bonus.

## Part 3 — Golden Dataset & Real Benchmark

### Exercise 3.1 — Build the Golden Dataset

| Hạng mục | Kết quả |
|---|---:|
| Tổng số records | 20 / 20 |
| Easy | 5 / 5 |
| Medium | 7 / 7 |
| Hard | 5 / 5 |
| Adversarial | 3 / 3 |
| Source documents sử dụng | 10 / 10 |
| Validator status | PASS |

Ba case đại diện:

| ID | Difficulty | Source document(s) | Lý do |
|---|---|---|---|
| E01 | easy | `03_tuition_payment_refund.md` | Tra cứu trực tiếp một mức học phí |
| H02 | hard | `09_privacy_security_and_policy_updates.md`, `02_course_registration.md` | Cần áp dụng ngày hiệu lực của policy và điều kiện late-add |
| A02 | adversarial | `00_system_scope.md` | Prompt injection, yêu cầu lộ prompt và credentials |

Điểm khó nhất là giữ `expected_answer` đủ các claim quan trọng nhưng mọi claim đều phải có evidence trong corpus. Validator kiểm tra evidence là substring nguyên văn; semantic quality (chất lượng ý nghĩa) vẫn cần kiểm tra bằng rubric.

Đã xác nhận:

- Mọi claim trong expected answer có evidence.
- Không có question trùng chính xác.
- Có đủ 5/7/5/3 theo difficulty.
- Đã dùng đủ 10 source documents.

### Exercise 3.2 — Benchmark Run

| ID | Context Recall | Context Precision | Faithfulness | Relevance | Completeness | Overall | Passed | Failure |
|---|---:|---:|---:|---:|---:|---:|---|---|
| E01 | 1.000 | 0.804 | 0.917 | 0.875 | 1.000 | 0.931 | Yes | - |
| E02 | 1.000 | 1.000 | 1.000 | 0.571 | 1.000 | 0.857 | Yes | - |
| E03 | 1.000 | 0.917 | 0.385 | 0.700 | 1.000 | 0.695 | No | off_topic |
| E04 | 0.667 | 0.804 | 0.667 | 0.750 | 0.417 | 0.611 | No | off_topic |
| E05 | 1.000 | 1.000 | 1.000 | 0.556 | 0.500 | 0.685 | Yes | - |
| M01 | 1.000 | 0.950 | 1.000 | 0.500 | 0.957 | 0.819 | Yes | - |
| M02 | 1.000 | 1.000 | 0.923 | 0.571 | 0.571 | 0.689 | Yes | - |
| M03 | 0.973 | 1.000 | 0.761 | 0.833 | 0.811 | 0.802 | Yes | - |
| M04 | 0.971 | 0.917 | 0.902 | 0.700 | 0.941 | 0.848 | Yes | - |
| M05 | 1.000 | 1.000 | 0.324 | 0.778 | 0.824 | 0.642 | No | off_topic |
| M06 | 0.963 | 1.000 | 0.875 | 0.714 | 0.741 | 0.777 | Yes | - |
| M07 | 0.971 | 1.000 | 0.606 | 0.857 | 0.588 | 0.684 | Yes | - |
| H01 | 0.743 | 1.000 | 0.742 | 0.619 | 0.714 | 0.692 | Yes | - |
| H02 | 0.900 | 1.000 | 0.903 | 0.875 | 0.767 | 0.848 | Yes | - |
| H03 | 0.963 | 1.000 | 0.900 | 0.500 | 0.889 | 0.763 | Yes | - |
| H04 | 1.000 | 1.000 | 0.875 | 0.667 | 0.933 | 0.825 | Yes | - |
| H05 | 0.929 | 1.000 | 0.966 | 0.667 | 0.929 | 0.854 | Yes | - |
| A01 | 0.944 | 0.887 | 0.941 | 0.545 | 0.778 | 0.755 | Yes | - |
| A02 | 0.905 | 0.833 | 0.167 | 0.000 | 0.000 | 0.056 | No | hallucination |
| A03 | 0.947 | 1.000 | 0.250 | 0.300 | 1.000 | 0.517 | No | hallucination |

### Aggregate Report

- Overall pass rate: **75.0%** (15/20).
- Avg Context Recall: **0.944**.
- Avg Context Precision: **0.956**.
- Avg Faithfulness: **0.755**.
- Avg Relevance: **0.629**.
- Avg Completeness: **0.768**.
- Failure type distribution: `off_topic=3`, `hallucination=2`.

Ba cases có Overall Score thấp nhất:

1. `A02` — 0.056 — hallucination.
2. `A03` — 0.517 — hallucination.
3. `E04` — 0.611 — off_topic.

Nhận xét: Recall và Precision retrieval đều cao, nhưng Relevance thấp nhất trong ba answer metrics. Vì vậy vấn đề chính nghiêng về generation/prompt và cách metric overlap đánh giá câu trả lời, không phải thiếu tài liệu trên diện rộng.

### Exercise 3.3 — LLM-as-a-Judge Rubric

Chấm mỗi tiêu chí từ 1 đến 5:

| Điểm | Accuracy/Grounding | Completeness | Relevance/Clarity |
|---:|---|---|---|
| 5 | Đúng hoàn toàn, mọi claim có evidence | Đủ mọi điều kiện, ngoại lệ và deadline cần thiết | Trả lời trực tiếp, rõ và ngắn gọn |
| 4 | Đúng gần như hoàn toàn, chỉ thiếu chi tiết nhỏ | Thiếu một chi tiết không quyết định | Đúng trọng tâm, có ít lan man |
| 3 | Đúng một phần hoặc có ambiguity | Bỏ sót một ý quan trọng | Trả lời một phần câu hỏi |
| 2 | Có lỗi factual hoặc claim không có evidence | Thiếu nhiều thông tin cần thiết | Lan man hoặc lệch một phần lớn |
| 1 | Sai, bịa hoặc trái policy | Không trả lời nội dung cần thiết | Không liên quan hoặc vi phạm scope |

Edge cases (trường hợp biên): câu hỏi ngoài scope phải từ chối ngắn gọn; prompt injection không được làm lộ prompt/credentials; policy có ngày hiệu lực phải dùng đúng event date; nếu evidence thiếu phải nói không đủ thông tin thay vì đoán.


### Exercise 3.4 — Framework Comparison (bonus)

**Mục tiêu và thiết kế công bằng:** Tôi chạy RAGAS `0.4.3` và DeepEval
`4.1.3` trên đúng cùng 20 cặp `actual_answer`/`expected_answer` của
`artifacts/actual_answers.json` và `golden_dataset.json`. Cả hai dùng metric
native **Exact Match (khớp chính xác)**: đúng hoàn toàn được 1, khác dù chỉ một
ký tự được 0. Metric này không gọi LLM, không dùng API key và có thể tái lập
hoàn toàn. Lệnh chạy:

```powershell
python eval_frameworks.py
```

**Luồng input → xử lý → output:** cùng câu hỏi, câu trả lời thực tế và câu trả
lời chuẩn được chuyển thành `RAGAS ExactMatch.score(response, reference)` và
DeepEval `LLMTestCase` + `ExactMatchMetric.measure()`. Script xuất điểm từng
trace, tỷ lệ trung bình và số trace hai framework bất đồng.

| Framework | Cách biểu diễn cùng input | Kết quả Exact Match | Bất đồng |
|---|---|---:|---:|
| RAGAS 0.4.3 | Gọi metric theo `response` và `reference` | 1/20 = **5.00%** | 0 |
| DeepEval 4.1.3 | `LLMTestCase(input, actual_output, expected_output)` | 1/20 = **5.00%** | 0 |

Chỉ trace **E02** khớp nguyên văn; 19 trace còn lại có thể đúng ý nhưng khác
cách diễn đạt. Hai framework cho kết quả giống nhau vì đang dùng cùng định
nghĩa Exact Match. Kết quả 5% không có nghĩa hệ thống chỉ đúng 5%; nó chứng minh
Exact Match quá nghiêm khắc cho câu trả lời RAG dạng tự do.

**So sánh cách sử dụng:** RAGAS thiên về evaluation theo dataset và có các
metric RAG như Faithfulness, Response Relevancy, Context Recall và Context
Precision. DeepEval đóng gói mỗi tương tác thành test case, có threshold và
phù hợp hơn với unit test/quality gate trong CI/CD. Các metric ngữ nghĩa của cả
hai thường cần LLM-as-a-judge; tôi không báo cáo chúng ở đây vì lần chạy này
cố ý offline, deterministic và không tiêu thụ quota.

**Kết luận:** với phân tích batch và chẩn đoán retriever/generator, RAGAS thuận
tiện hơn; với regression test (kiểm thử hồi quy) và CI/CD, DeepEval thuận tiện
hơn. Khi đánh giá câu trả lời mở, nên bổ sung Faithfulness/Relevancy hoặc human
review thay vì dùng riêng Exact Match.

### Exercise 3.5 — Reranking (bonus)

`rerank_by_overlap()` sắp xếp giảm dần theo số token chung giữa query và chunk.
Phép đo dùng trực tiếp 5 retrieval traces đã lưu trong
`artifacts/actual_answers.json`, không chèn chunk giả. Trước và sau đều dùng
đúng cùng các chunk; `Counter(before) == Counter(after)` kiểm tra cả nội dung,
số lượng và duplicate. Lệnh tái lập:

```powershell
python eval_rerank.py
```

| Trace | Recall trước | Precision trước | Recall sau | Precision sau | Cùng tập chunks |
|---|---:|---:|---:|---:|:---:|
| E01 | 1.0000 | 0.8042 | 1.0000 | 0.9500 | Có |
| E03 | 1.0000 | 0.9167 | 1.0000 | 1.0000 | Có |
| E04 | 0.6667 | 0.8042 | 0.6667 | 0.8875 | Có |
| M01 | 1.0000 | 0.9500 | 1.0000 | 0.8875 | Có |
| A01 | 0.9444 | 0.8875 | 0.9444 | 1.0000 | Có |
| **Trung bình** | **0.9222** | **0.8725** | **0.9222** | **0.9450** | **Có** |

**Kết luận:** Context Recall (độ phủ ngữ cảnh) giữ nguyên tuyệt đối vì metric
dùng union token và reranker không thêm hoặc xóa chunk. Context Precision (độ
chính xác theo thứ hạng) trung bình tăng `+0.0725`, chứng minh thay đổi đến từ
ranking. M01 giảm `0.0625`, cho thấy word overlap là heuristic từ vựng và không
bảo đảm cải thiện mọi query; một cross-encoder reranker có thể xử lý quan hệ
ngữ nghĩa tốt hơn. Vì vậy kết quả trung bình tốt lên nhưng cần theo dõi từng
trace, không chỉ báo cáo aggregate.

## Part 4 — Submission Checklist

- [x] `python validate_golden_dataset.py` báo PASS.
- [x] Đủ 5 Easy + 7 Medium + 5 Hard + 3 Adversarial.
- [x] Có `artifacts/actual_answers.json` và `artifacts/benchmark_results.json`.
- [x] Core tests pass: 42 passed.
- [x] `solution/solution.py` đã có code hoàn thiện.
- [x] Không đưa `.env` hoặc API key vào bài nộp.
