import streamlit as st
from auth.session_manager import QuanLyPhienDangNhap
from components.auth_pages import hien_thi_trang_dang_nhap
from components.sidebar import hien_thi_thanh_chu_ngoi
from components.analysis_form import hien_thi_bieu_mau_phan_tich
from components.footer import hien_thi_chan_trang
from config.app_config import APP_NAME, APP_TAGLINE, APP_DESCRIPTION, APP_ICON

# Dòng Streamlit phải được gọi đầu tiên
st.set_page_config(
    page_title="Trợ lý sức khỏe cho bạn",
    page_icon="🩺",
    layout="wide"
)

# Khởi tạo trạng thái phiên đăng nhập
QuanLyPhienDangNhap.khoi_tao_phien()

# Ẩn tất cả các phần tử liên quan đến form mặc định của Streamlit
st.markdown("""
    <style>
        /* Ẩn chú thích hướng dẫn nhập liệu */
        div[data-testid="InputInstructions"] > span:nth-child(1) {
            visibility: hidden;
        }
    </style>
""", unsafe_allow_html=True)

def hien_thi_man_chao():
    """Hiển thị màn hình chào ban đầu khi chưa có phiên làm việc."""
    st.markdown(
        f"""
        <div style='text-align: center; padding: 50px;'>
            <h1>{APP_ICON} {APP_NAME}</h1>
            <h3>{APP_DESCRIPTION}</h3>
            <p style='font-size: 1.2em; color: #666;'>{APP_TAGLINE}</p>
            <p>Bắt đầu bằng cách tạo phiên phân tích mới</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    cot1, cot2, cot3 = st.columns([2, 3, 2])
    with cot2:
        if st.button("➕ Tạo Phiên Phân Tích Mới", use_container_width=True, type="primary"):
            thanh_cong, phien_moi = QuanLyPhienDangNhap.tao_phien_phan_tich()
            if thanh_cong:
                st.session_state.phien_hien_tai = phien_moi
                st.rerun()
            else:
                st.error("Không thể tạo phiên mới")

def hien_thi_lich_su_tro_chuyen():
    """Hiển thị lại lịch sử tin nhắn trong phiên hiện tại."""
    thanh_cong, tin_nhan = st.session_state.auth_service.get_session_messages(
        st.session_state.phien_hien_tai['id']
    )
    
    if thanh_cong:
        for tin in tin_nhan:
            if tin['role'] == 'user':
                st.info(tin['content'])
            else:
                st.success(tin['content'])

def chao_nguoi_dung():
    """Hiển thị lời chào người dùng dựa trên thông tin đăng nhập."""
    if st.session_state.user:
        ten_hien_thi = st.session_state.user.get('name') or st.session_state.user.get('email', '')
        st.markdown(f"""
            <div style='text-align: right; padding: 1rem; color: #64B5F6; font-size: 1.1em;'>
                👋 Xin chào, {ten_hien_thi}
            </div>
        """, unsafe_allow_html=True)

def ung_dung_chinh():
    """Hàm chính để chạy toàn bộ ứng dụng."""
    QuanLyPhienDangNhap.khoi_tao_phien()

    if not QuanLyPhienDangNhap.da_dang_nhap():
        hien_thi_trang_dang_nhap()
        hien_thi_chan_trang()
        return

    # Hiển thị lời chào
    chao_nguoi_dung()

    # Hiển thị sidebar chức năng
    hien_thi_thanh_ben()

    # Vùng nội dung chính
    if st.session_state.get('phien_hien_tai'):
        st.title(f"📊 {st.session_state.phien_hien_tai['title']}")
        hien_thi_lich_su_tro_chuyen()
        hien_thi_bieu_mau_phan_tich()
    else:
        hien_thi_man_chao()

if __name__ == "__main__":
    ung_dung_chinh()
