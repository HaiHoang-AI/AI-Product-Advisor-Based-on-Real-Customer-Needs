# 🏆 Trợ lý AI So sánh & Tư vấn Sản phẩm Theo Nhu Cầu Thật của Khách Hàng
> **Vietnam Innovation Challenge 2026 — Track Năng Suất Doanh Nghiệp (Điện Máy Xanh)**  
> **Enterprise Partner**: Công Ty Cổ Phần Đầu Tư Điện Máy Xanh (Thế Giới Di Động)

---

## 🌟 1. Giới thiệu Bài toán & Giá trị Đột phá

Khi mua các sản phẩm điện máy (tủ lạnh, máy lạnh, tivi, laptop...), khách hàng phổ thông thường bị "ngợp" bởi các bảng thông số kỹ thuật khô khan (inverter, dual cooling, BTU, dB, công suất...). 

Hầu hết hệ thống chatbot hiện tại chỉ trả lời FAQ hoặc liệt kê thông số cạnh nhau mà **không hiểu hoàn cảnh sử dụng thực tế** (bao nhiêu người, phòng nắng hay không, ưu tiên độ êm hay làm lạnh nhanh).

**AI Product Comparison Advisor** giải quyết triệt để bài toán này với 5 trụ cột "Xịn Sò":
1. 🧠 **Need Understanding Canvas**: Phân tích câu nói tự nhiên tiếng Việt, trích xuất nhu cầu và hiển thị trực quan những gì AI đã hiểu.
2. 🔄 **Smart Follow-up**: Tự động hỏi ngược 1-2 câu hỏi then chốt khi thiếu dữ kiện trước khi đưa ra quyết định.
3. 📊 **Visual Trade-off Cards**: Đề xuất Top 3 sản phẩm phù hợp nhất, giải thích ưu điểm ✅ và điểm đánh đổi ⚠️ bằng ngôn ngữ bình dân dễ hiểu.
4. 🛡️ **Zero-Hallucination Guardrail**: Tuyệt đối không bịa giá, tồn kho hay quà khuyến mãi. Trích dẫn rõ nguồn gốc dữ liệu hoặc báo "chưa có thông tin".
5. 🏬 **Enterprise API Ready**: Tích hợp sẵn Price API, Stock theo khu vực địa lý, Promotion API và Review Sentiment.

---

## 🏗️ 2. Kiến trúc Hệ thống (System Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 14 / Tailwind)          │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │ Need Canvas  │  │ Product Cards    │  │ Quick Reply  │   │
│  │ (State Bar)  │  │ (Trade-off View) │  │ (Follow-up)  │   │
│  └──────────────┘  └──────────────────┘  └──────────────┘   │
└──────────────────────────────┬──────────────────────────────┘
                               │ SSE / Streaming
┌──────────────────────────────▼──────────────────────────────┐
│                    BACKEND (FastAPI / Python)                │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │             Conversation Orchestrator                 │  │
│  │  ┌───────────────┐ ┌────────────────┐ ┌────────────┐  │  │
│  │  │  Need Parser  │ │ Smart Follow-up│ │ Guardrail  │  │  │
│  │  └───────────────┘ └────────────────┘ └────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌────────────────────────┐  ┌───────────────────────────┐  │
│  │ Vector Store (Chroma)  │  │ Mock Enterprise APIs      │  │
│  │ Semantic Catalog RAG   │  │ Price | Stock | Promo     │  │
│  └────────────────────────┘  └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 3. Hướng dẫn Cài đặt & Chạy ứng dụng

### Cách 1: Chạy trực tiếp (Local Development)

#### Backend (Python 3.10+)
```bash
cd backend
# Cài đặt thư viện
pip install -r requirements.txt

# Thiết lập API Key (Gemini API)
# Tạo file .env với nội dung:
GEMINI_API_KEY="your-gemini-api-key"

# Khởi chạy Backend Server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation có thể xem tại: `http://localhost:8000/docs`

#### Frontend (Next.js 14)
```bash
cd frontend
# Cài đặt packages
npm install

# Khởi chạy Frontend UI
npm run dev
```
Truy cập giao diện tại: `http://localhost:3000`

---

### Cách 2: Chạy bằng Docker Compose (Khuyên dùng cho Demo)

```bash
# Khởi động toàn bộ Backend + Frontend chỉ với 1 câu lệnh:
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## 🧪 4. Kịch bản Demo Ấn tượng (Demo Scenarios)

### Kịch bản 1: Tư vấn hoàn chỉnh với Trade-off
- **Khách hỏi**: *"Em muốn mua tủ lạnh cho gia đình 4 người, ngân sách dưới 15 triệu, ưu tiên tiết kiệm điện."*
- **Hành vi AI**: 
  - Need Summary nhận diện: `Tủ lạnh`, `Ngân sách < 15.000.000đ`, `4 người`, `Tiết kiệm điện`.
  - Tự động gợi ý câu hỏi phụ: *"Anh/chị thích kiểu ngăn đá trên hay ngăn đá dưới ạ?"*
  - Xuất ra Top 3 sản phẩm kèm thẻ Trade-off (VD: Samsung Inverter vs Toshiba vs Panasonic).

### Kịch bản 2: Hỏi thiếu thông tin (Smart Follow-up)
- **Khách hỏi**: *"Mua máy lạnh cho em với"*
- **Hành vi AI**: AI không trả lời chung chung hoặc liệt kê máy lạnh bừa bãi. AI lập tức hỏi:
  - 1. Diện tích phòng khoảng bao nhiêu m²?
  - 2. Phòng ngủ hay phòng khách (ảnh hưởng độ ồn)?
  - 3. Có bị nắng hướng Tây chiếu trực tiếp không?

### Kịch bản 3: Guardrail chống bịa đặt (Anti-Hallucination)
- **Khách hỏi**: *"Tủ lạnh này có được tặng máy xay sinh tố ở Đà Nẵng không?"*
- **Hành vi AI**: Truy vấn Promotion API & Stock API theo khu vực Đà Nẵng. Nếu không có quà tặng trong dữ liệu, AI trả lời minh bạch: *"Dạ theo dữ liệu hiện tại sản phẩm này chưa có chương trình tặng máy xay sinh tố tại Đà Nẵng ạ."*

---

## 📁 5. Cấu trúc Thư mục Dự án

```
.
├── backend/                  # FastAPI Core Application
│   ├── api/                  # Route handlers & endpoints
│   ├── core/                 # AI Engine (Parser, Follow-up, Ranker, Guardrail, Orchestrator)
│   ├── data/                 # Data Pipeline, Embeddings, Mock APIs
│   ├── models/               # Pydantic Schemas
│   ├── config.py             # Settings & Environment variables
│   ├── Dockerfile            # Backend Dockerfile
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Next.js 14 Web Application
│   ├── src/app/              # App router & pages
│   ├── src/components/chat/  # ChatPanel, ProductCard, Tradeoff, NeedSummary
│   ├── Dockerfile            # Frontend Dockerfile
│   └── package.json
├── docs/                     # Tài liệu thiết kế & Lộ trình Pilot
│   ├── architecture.md       # Thiết kế kiến trúc chi tiết
│   └── pilot_roadmap.md      # Lộ trình thử nghiệm 12 tuần tại Điện Máy Xanh
├── tests/                    # Bộ kiểm thử tự động (Unit & Scenarios)
│   ├── test_data_pipeline.py
│   ├── test_guardrail.py
│   └── scenarios/
├── docker-compose.yml        # Multi-container orchestration
└── README.md
```

---

## ⚖️ 6. Giấy phép & Bản quyền
Dự án được xây dựng phục vụ cuộc thi Vietnam Innovation Challenge 2026 và tuân thủ các quy định bảo mật dữ liệu mẫu của Công ty Cổ phần Đầu tư Điện Máy Xanh.
