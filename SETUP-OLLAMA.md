# Lab 11 với Ollama trên Jetson

Ollama: `http://192.168.1.246:11434`; OpenAI-compatible API: `/v1`.
Model: `lfm3:1.7b` (Q4_K_M, khoảng 1.1 GB).

## Chạy trên Windows

```powershell
.\.venv\Scripts\python.exe scripts/check_ollama.py
# Kiểm tra thêm Red Advance và NeMo (gọi Gemini, cần key):
.\.venv\Scripts\python.exe scripts/check_ollama.py --advance
# Chạy từng checkpoint khi bạn sẵn sàng:
.\.venv\Scripts\python.exe src/main.py --part 2
.\.venv\Scripts\python.exe src/main.py --part 3
.\.venv\Scripts\python.exe src/main.py --part 4
```

File `.env` local đã được cấu hình:

```dotenv
BLUE_TEAM_PROVIDER=ollama
RED_TEAM_PROVIDER=gemini
OLLAMA_BASE_URL=http://192.168.1.246:11434/v1
LAB_OLLAMA_MODEL=lfm3:1.7b
OLLAMA_API_KEY=ollama
OLLAMA_TIMEOUT_SECONDS=180
NEMO_GUARDRAILS_NO_USAGE_STATS=1
GOOGLE_API_KEY=
GOOGLE_GENAI_USE_VERTEXAI=0
GEMINI_MODEL=gemini-3.5-flash
```

Dùng `LAB_OLLAMA_MODEL` để tránh xung đột biến hệ thống `OLLAMA_MODEL` trên máy này.
Key `ollama` chỉ là giá trị cho SDK local, không phải cloud secret.
Red và Red Advance dùng Gemini; NeMo self-check dùng cùng model/key Gemini.
Điền `GOOGLE_API_KEY` trong `.env`, hoặc nhập key khi chạy CP4; key nhập tại
terminal được ẩn và chỉ giữ trong môi trường của tiến trình đó.
CP2 không cần key; CP3 chỉ dùng Blue trên Jetson. Không cần nhập key Red khi chạy CP2/CP3.

## Implementation CP2–CP4

Các TODO bắt buộc đã được implement, nhưng **chưa chạy lab hoặc test sau thay đổi**.
Chưa sinh artifact kết quả mới.

- CP2: chuẩn hóa Unicode/tiếng Việt, lọc injection/topic, che secret/PII trước khi trả lời.
- CP3: sliding window theo user, audit đã che dữ liệu nhạy cảm, metrics/alerts,
  plugin order và egress kiểm tra chính xác hostname/HTTPS. Audit và monitoring
  là observer bên ngoài runner, cập nhật sau từng request, không gọi thêm model.
- CP3 ghi `framework`, provider/model thật và các quyết định callback vào JSON.
  Bài thử burst kiểm tra riêng stage rate limiter (10 lượt qua, 5 lượt chặn với
  cấu hình mặc định), không gọi LLM; phạm vi này ghi rõ trong kết quả.
  Egress chỉ kiểm tra policy, không gửi dữ liệu hay thực hiện giao dịch ngân hàng.
- CP4: năm prompt nháp có giả thuyết giải thích từng kỹ thuật. Kịch bản nhiều lượt
  giữ session trong từng cuộc tấn công và lưu transcript để xem lại. Bạn nên đọc,
  điều chỉnh các prompt và giải thích được chúng theo `RULES.md`.
- Lỗi API được ghi riêng; không coi lỗi kết nối hoặc quota là kết quả phòng thủ thành công.
- LLM-as-Judge cho Blue đã có implementation tùy chọn, mặc định tắt trong pipeline.
  Các module tham khảo `hitl/`, `testing/` và NeMo tùy chọn cho Blue không nằm
  trong phần CP2–CP4 bắt buộc này. NeMo của Red Advance vẫn giữ nguyên các lớp bảo vệ.

Các lệnh sau để bạn tự chạy, chưa được thực thi trong lần implement này:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/smoke tests/public tests/unit -q
.\.venv\Scripts\python.exe src/main.py --part 2
.\.venv\Scripts\python.exe src/main.py --part 3
.\.venv\Scripts\python.exe src/main.py --part 4
# Khi đã có kết quả CP3/CP4, kiểm tra lại và sinh báo cáo tự động:
.\.venv\Scripts\python.exe -m pytest tests/smoke tests/public tests/unit -q
.\.venv\Scripts\python.exe scripts/grade.py --submission-dir . --out outputs/grade_report.json
```

`tests/unit` thay LLM bằng fake và ghi vào thư mục tạm; không gọi dịch vụ thật.
Các file `outputs/*.json` và báo cáo chỉ được sinh khi bạn chủ động chạy lab/grader.

## Chuyển về cấu hình chấm bài

Chế độ Ollama dành cho thực hành local. Đề gốc yêu cầu Blue dùng OpenRouter
`liquid/lfm-3-1.7b:free`, Red dùng OpenAI hoặc Gemini. Để chạy theo đề,
đặt `BLUE_TEAM_PROVIDER=openrouter`, `RED_TEAM_PROVIDER=openai` hoặc `gemini`,
và điền API key/model tương ứng theo `.env.example`.
Không commit `.env`. Đọc code và tự chạy các checkpoint trước khi nộp.

## Tham khảo

- Model: https://registry.ollama.com/library/lfm3:1.7b
- API tương thích OpenAI: https://docs.ollama.com/api/openai-compatibility
