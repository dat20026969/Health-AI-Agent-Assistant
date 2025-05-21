# 🩺 AI Agent hiểu biết về sức khỏe

AI Agent phân tích báo cáo máu và cung cấp thông tin chi tiết về sức khỏe.
Python mới nhất
Streamlit 
Tài khoản Supabase
Groq API key
PDFPlumber
Python-magic-bin (Windows)

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
