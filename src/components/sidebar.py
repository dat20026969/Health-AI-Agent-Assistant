import streamlit as st
from auth.session_manager import QuanLyPhienDangNhap
from components.footer import hien_thi_chan_trang
from config.app_config import ANALYSIS_DAILY_LIMIT


def hien_thi_thanh_chu_ngoi():
    """Hiển thị sidebar quản lý các phiên chat và giới hạn phân tích hàng ngày."""
    with st.sidebar:
        st.title("💬 Phiên Chat")
        
        # Nút tạo phiên phân tích mới
        if st.button("+ Phiên Phân Tích Mới", use_container_width=True):
            if st.session_state.user and 'id' in st.session_state.user:
                thanh_cong, phien_moi = QuanLyPhien.tao_phien_moi()
                if thanh_cong:
                    st.session_state.current_session = phien_moi
                    st.rerun()
                else:
                    st.error("Tạo phiên thất bại")
            else:
                st.error("Vui lòng đăng nhập lại")
                QuanLyPhien.thuc_hien_dang_xuat()
                st.rerun()

        # Hiển thị bộ đếm phân tích hàng ngày
        if 'luot_phan_tich' not in st.session_state:
            st.session_state.luot_phan_tich = 0
        con_lai = ANALYSIS_DAILY_LIMIT - st.session_state.luot_phan_tich
        st.markdown(f"""
            <div style='
                padding:0.5rem;
                border-radius:0.5rem;
                background:rgba(100,181,246,0.1);
                margin:0.5rem 0;
                text-align:center;
                font-size:0.9em;
            '>
                <p style='margin:0; color:#666;'>Giới hạn Phân Tích Hàng Ngày</p>
                <p style='
                    margin:0.2rem 0 0 0;
                    color:{"#1976D2" if con_lai>3 else "#FF4B4B"};
                    font-weight:500;
                '>
                    {con_lai}/{ANALYSIS_DAILY_LIMIT} còn lại
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        hien_thi_danh_sach_phien()
        
        st.markdown("---")
        # Nút đăng xuất
        if st.button("Đăng xuất", use_container_width=True):
            QuanLyPhien.thuc_hien_dang_xuat()
            st.rerun()
        
        # Chân trang trong sidebar
        hien_thi_chan_trang(in_sidebar=True)


def hien_thi_danh_sach_phien():
    """Lấy và hiển thị danh sách các phiên chat trước đó của người dùng."""
    if st.session_state.user and 'id' in st.session_state.user:
        thanh_cong, cac_phien = QuanLyPhien.lay_cac_phien_chat()
        if thanh_cong:
            if cac_phien:
                st.subheader("Các Phiên Trước")
                ve_danh_sach_phien(cac_phien)
            else:
                st.info("Chưa có phiên trước đó")


def ve_danh_sach_phien(cac_phien):
    """Render container cho từng phiên trong danh sách."""
    # Lưu trạng thái xác nhận xóa
    if 'xac_nhan_xoa' not in st.session_state:
        st.session_state.xac_nhan_xoa = None
    
    for phien in cac_phien:
        ve_phien_item(phien)


def ve_phien_item(phien):
    """Hiển thị một item phiên với tiêu đề và nút xóa."""
    if not phien or not isinstance(phien, dict) or 'id' not in phien:
        return
    phien_id = phien['id']
    phien_hien_tai = st.session_state.get('current_session', {})
    hien_tai_id = phien_hien_tai.get('id') if isinstance(phien_hien_tai, dict) else None
    
    with st.container():
        cot_tieu_de, cot_xoa = st.columns([4,1])
        # Nút chọn phiên
        with cot_tieu_de:
            if st.button(f"📝 {phien['title']}", key=f"phien_{phien_id}", use_container_width=True):
                st.session_state.current_session = phien
                st.rerun()
        # Nút xóa phiên
        with cot_xoa:
            if st.button("🗑️", key=f"xoa_{phien_id}", help="Xóa phiên này"):                
                if st.session_state.xac_nhan_xoa == phien_id:
                    st.session_state.xac_nhan_xoa = None
                else:
                    st.session_state.xac_nhan_xoa = phien_id
                st.rerun()
        
        # Hiện cảnh báo xác nhận xóa
        if st.session_state.xac_nhan_xoa == phien_id:
            st.warning("Xác nhận xóa phiên này?")
            nut_co, nut_khong = st.columns(2)
            with nut_co:
                if st.button("Có", key=f"xac_nhan_co_{phien_id}", type="primary", use_container_width=True):
                    xu_ly_xac_nhan_xoa(phien_id, hien_tai_id)
            with nut_khong:
                if st.button("Không", key=f"xac_nhan_khong_{phien_id}", use_container_width=True):
                    st.session_state.xac_nhan_xoa = None
                    st.rerun()


def xu_ly_xac_nhan_xoa(phien_id, hien_tai_id):
    """Xử lý xóa phiên sau khi người dùng xác nhận."""
    if not phien_id:
        st.error("Phiên không hợp lệ")
        return
    thanh_cong, loi = QuanLyPhien.xoa_phien_chat(phien_id)
    if thanh_cong:
        st.session_state.xac_nhan_xoa = None
        # Nếu đang xem phiên vừa xóa thì clear
        if hien_tai_id and hien_tai_id == phien_id:
            st.session_state.current_session = None
        st.rerun()
    else:
        st.error(f"Xóa thất bại: {loi}")
