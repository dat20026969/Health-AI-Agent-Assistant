import streamlit as st
from datetime import datetime, timedelta
from config.app_config import SESSION_TIMEOUT_MINUTES

class QuanLyPhienDangNhap:
    @staticmethod
    def bat_dau_phien():
        """Khởi động hoặc xác minh phiên làm việc hiện tại."""
        # Nếu là phiên duyệt mới, xóa toàn bộ trạng thái session cũ
        if 'phien_da_khoi_tao' not in st.session_state:
            QuanLyPhienDangNhap.xoa_du_lieu_phien()
            st.session_state.phien_da_khoi_tao = True
        
        # Khởi tạo dịch vụ xác thực nếu chưa tồn tại
        if 'dich_vu_xac_thuc' not in st.session_state:
            from auth.auth_service import DichVuXacThuc
            st.session_state.dich_vu_xac_thuc = DichVuXacThuc()
        
        # Kiểm tra thời gian không hoạt động để tự động đăng xuất nếu quá hạn
        if 'thoi_diem_hoat_dong_cuoi' in st.session_state:
            thoi_gian_khong_hoat_dong = datetime.now() - st.session_state.thoi_diem_hoat_dong_cuoi
            if thoi_gian_khong_hoat_dong > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                QuanLyPhienDangNhap.xoa_du_lieu_phien()
                st.error("Phiên đã hết hạn. Vui lòng đăng nhập lại.")
                st.rerun()
        
        # Cập nhật thời gian hoạt động mới nhất
        st.session_state.thoi_diem_hoat_dong_cuoi = datetime.now()
        
        # Kiểm tra tính hợp lệ của token xác thực và dữ liệu người dùng
        if 'user' in st.session_state:
            du_lieu_nguoi_dung = st.session_state.dich_vu_xac_thuc.ktra_token_phien()
            if not du_lieu_nguoi_dung:
                QuanLyPhienDangNhap.xoa_du_lieu_phien()
                st.error("Phiên không hợp lệ. Vui lòng đăng nhập lại.")
                st.rerun()

    @staticmethod
    def xoa_du_lieu_phien():
        """Xóa toàn bộ dữ liệu liên quan đến phiên làm việc."""
        cac_khoa_giu_lai = ['phien_da_khoi_tao']
        for khoa in list(st.session_state.keys()):
            if khoa not in cac_khoa_giu_lai:
                del st.session_state[khoa]

    @staticmethod
    def da_duoc_xac_thuc():
        """Xác minh người dùng đã đăng nhập hay chưa."""
        return bool(st.session_state.get('user'))
    
    @staticmethod
    def tao_phien_moi():
        """Khởi tạo một phiên chat mới."""
        if not QuanLyPhienDangNhap.da_duoc_xac_thuc():
            return False, "Chưa đăng nhập"
        return st.session_state.dich_vu_xac_thuc.tao_phien_chat(
            st.session_state.user['id']
        )
    
    @staticmethod
    def lay_cac_phien_chat():
        """Lấy tất cả các phiên chat của người dùng đang đăng nhập."""
        if not QuanLyPhienDangNhap.da_duoc_xac_thuc():
            return False, []
        return st.session_state.dich_vu_xac_thuc.lay_cac_phien(
            st.session_state.user['id']
        )
    
    @staticmethod
    def xoa_phien_chat(phien_id):
        """Xóa một phiên chat cụ thể."""
        if not QuanLyPhienDangNhap.da_duoc_xac_thuc():
            return False, "Chưa đăng nhập"
        return st.session_state.dich_vu_xac_thuc.xoa_phien(phien_id)
    
    @staticmethod
    def thuc_hien_dang_xuat():
        """Thực hiện đăng xuất người dùng và dọn dẹp session."""
        if 'dich_vu_xac_thuc' in st.session_state:
            st.session_state.dich_vu_xac_thuc.dang_xuat()
        QuanLyPhienDangNhap.xoa_du_lieu_phien()
    
    @staticmethod
    def thuc_hien_dang_nhap(email, mat_khau):
        """Xử lý đăng nhập bằng email và mật khẩu."""
        if 'dich_vu_xac_thuc' not in st.session_state:
            from auth.auth_service import DichVuXacThuc
            st.session_state.dich_vu_xac_thuc = DichVuXacThuc()
        return st.session_state.dich_vu_xac_thuc.dang_nhap_tai_khoan(email, mat_khau)
