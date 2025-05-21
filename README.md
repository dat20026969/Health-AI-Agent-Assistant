# 🩺 AI Agent hiểu biết về sức khỏe

AI Agent phân tích báo cáo máu và cung cấp thông tin chi tiết về sức khỏe.

Cài những thư viện cần thiết trong requirements.txt trước bằng cách:
pip install -r requirements.txt

Cài đặt môi trường trong .streamlit/secrets.toml
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"
GROQ_API_KEY = "your-groq-api-key"

Ứng dụng này yêu cầu các bảng sau trong cơ sở dữ liệu, ở đây mình sẽ dùng Supabase (trong file ảnh varus.png)



Khởi chạy (đang điều chỉnh thêm)
cd đường dẫn đến thư mục có main
sau đó streamlit run main.py

Cấu trúc dự án
hia/
├── requirements.txt
├── README.md
├── src/
│ ├── main.py # Điểm vào ứng dụng
│ ├── auth/ # Các mô-đun liên quan đến xác thực
│ │ ├── auth_service.py # Tích hợp xác thực Supabase
│ │ └── session_manager.py # Quản lý phiên
│ ├── components/ # Thành phần UI
│ │ ├── analysis_form.py # Biểu mẫu phân tích báo cáo
│ │ ├── auth_pages.py # Trang đăng nhập/đăng ký
│ │ ├── footer.py # Thành phần chân trang
│ │ └── sidebar.py # Điều hướng thanh bên
│ ├── config/ # Tệp cấu hình
│ │ ├── app_config.py # Cài đặt ứng dụng
│ │ └── prompts.py # Lời nhắc AI
│ ├── services/ # Tích hợp dịch vụ
│ │ └── ai_service.py # Tích hợp dịch vụ AI
│ ├── agents/ # Thành phần kiến ​​trúc dựa trên tác nhân
│ │ ├── agent_manager.py # Quản lý tác nhân
│ │ └── model_fallback.py # Logic dự phòng mô hình
│ └── utils/ # Tiện ích chức năng
│ ├── validators.py # Xác thực đầu vào
│ └── pdf_extractor.py # Xử lý PDF
