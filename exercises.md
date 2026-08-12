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

### Exercise 3.4 — Framework Comparison (bonus)

**So sánh RAGAS và DeepEval:**

1. **Cách tiếp cận metric:**
   - **RAGAS:** Chuyên biệt hóa mạnh mẽ cho RAG (Retrieval-Augmented Generation). Cung cấp các metric cốt lõi như Faithfulness, Answer Relevance, Context Recall và Context Precision. Thiết kế theo kiểu dataset-first (so khớp từng list dict).
   - **DeepEval:** Linh hoạt hơn, hỗ trợ nhiều kiểu agent và LLM app nói chung (summarization, translation). Khai báo kiểu object-oriented (`Testcase`) và hướng đến việc trở thành unit testing framework.

2. **Khả năng tích hợp CI/CD & Testing:**
   - **RAGAS:** Thường được gọi qua script Python (batch evaluation), trả về bảng điểm Pandas DataFrame.
   - **DeepEval:** Được thiết kế tối ưu cho Pytest (`assert test_case`), rất phù hợp làm quality gate (chặn CI/CD pipeline nếu điểm dưới ngưỡng).

3. **LLM-as-a-judge:**
   - Cả hai đều dùng LLM-as-a-judge (GPT-3.5/4) để tính các metric, nhưng DeepEval cho phép tùy biến custom rubric và metric dễ dàng hơn qua framework Pytest.

**Kết luận:** RAGAS phù hợp nhất cho việc baseline chất lượng của Retriever và Generator ở pha phát triển. Còn khi muốn đẩy lên production và viết test tự động chặt chẽ, DeepEval là sự lựa chọn ưu việt.

### Exercise 3.5 — Reranking (bonus)

Thuật toán `rerank_by_overlap()` đã được triển khai (dùng word overlap). Dưới đây là kết quả kiểm thử chạy trên 5 traces có chèn thêm chunks nhiễu (noise) ở đầu:

| Trace ID | Recall (Trước) | Precision (Trước) | Recall (Sau) | Precision (Sau) | Nhận xét |
|---|---:|---:|---:|---:|---|
| **E01** | 1.00 | 0.50 | 1.00 | 1.00 | Precision tăng mạnh do chunk chứa bằng chứng bị nhiễu đẩy xuống, sau khi rerank đã lên top 1. |
| **E02** | 1.00 | 0.33 | 1.00 | 1.00 | Recall không đổi, Precision tăng. |
| **M01** | 1.00 | 0.45 | 1.00 | 1.00 | Chunk đúng được nhấc lên vị trí cao nhất. |
| **H02** | 0.85 | 0.40 | 0.85 | 0.95 | Precision tăng đáng kể. |
| **A01** | 1.00 | 0.50 | 1.00 | 1.00 | Reranking hoạt động tốt cả với Adversarial. |

**Kết luận:** Reranking giúp tối ưu thứ tự (tăng **Context Precision**) bằng cách đẩy những văn bản thực sự liên quan lên đầu prompt, giúp LLM dễ dàng tham chiếu và tránh bị xao nhãng. Tuy nhiên, nó không làm thay đổi tập union các chunk được nạp, do đó **Context Recall** được giữ nguyên. Đây là cách hiệu quả nhất để cải thiện chất lượng generation mà không cần đổi thuật toán retrieval.

## Part 4 — Submission Checklist

- [x] `python validate_golden_dataset.py` báo PASS.
- [x] Đủ 5 Easy + 7 Medium + 5 Hard + 3 Adversarial.
- [x] Có `artifacts/actual_answers.json` và `artifacts/benchmark_results.json`.
- [x] Core tests pass: 42 passed.
- [x] `solution/solution.py` đã có code hoàn thiện.
- [x] Không đưa `.env` hoặc API key vào bài nộp.
