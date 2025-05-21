import streamlit as st
from st_supabase_connection import SupabaseConnection
from datetime import datetime
import time
import re

class DichVuXacThuc:
    """
    Dịch vụ xác thực người dùng:
    - Tạo kết nối Supabase
    - Đăng ký, đăng nhập, đăng xuất
    - Quản lý phiên và tin nhắn chat
    """
    def __init__(self):
        try:
            # Thiết lập kết nối Supabase
            self.ket_noi_supabase = st.connection(
                "supabase",
                type=SupabaseConnection,
                ttl=None,
                url=st.secrets["SUPABASE_URL"],
                key=st.secrets["SUPABASE_KEY"],
                client_options={
                    "timeout": 30,  # Giới hạn 30 giây
                    "retries": 3    # Tối đa 3 lần thử
                }
            )
        except Exception as e:
            st.error(f"Không thể khởi tạo dịch vụ: {e}")
            raise e
        
        # Kiểm tra token nếu đã tồn tại trong session
        if 'token_xac_thuc' in st.session_state:
            if not self.kiem_tra_token():
                self.dang_xuat()

    def kiem_tra_email(self, email):
        """Xác thực định dạng email."""
        bieu_thuc = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(bieu_thuc, email))

    def kiem_tra_dang_ky(self, email):
        """Kiểm tra xem email đã được đăng ký hay chưa."""
        try:
            phan_hoi_db = self.ket_noi_supabase.table('users')\
                .select('id')\
                .eq('email', email)\
                .execute()
            return len(phan_hoi_db.data) > 0
        except Exception:
            return False

    def dang_ky_tai_khoan(self, email, mat_khau, ten_nguoi_dung):
        """Đăng ký người dùng mới."""
        try:
            phan_hoi_xac_thuc = self.ket_noi_supabase.client.auth.sign_up({
                "email": email,
                "password": mat_khau,
                "options": {"data": {"name": ten_nguoi_dung}}
            })
            if not phan_hoi_xac_thuc.user:
                return False, "Tạo tài khoản không thành công"

            thong_tin_nguoi = {
                'id': phan_hoi_xac_thuc.user.id,
                'email': email,
                'name': ten_nguoi_dung,
                'created_at': datetime.now().isoformat()
            }
            # Lưu thông tin vào bảng users
            self.ket_noi_supabase.table('users').insert(thong_tin_nguoi).execute()
            return True, thong_tin_nguoi
        except Exception as e:
            loi = str(e).lower()
            if 'duplicate' in loi or 'already registered' in loi:
                return False, "Email này đã tồn tại"
            return False, f"Đăng ký thất bại: {e}"

    def dang_nhap_tai_khoan(self, email, mat_khau):
        """Thực hiện đăng nhập bằng email và mật khẩu."""
        try:
            # Xóa session cũ nếu có
            self.dang_xuat()
            phan_hoi_xac_thuc = self.ket_noi_supabase.client.auth.sign_in_with_password({
                "email": email,
                "password": mat_khau
            })
            if phan_hoi_xac_thuc and phan_hoi_xac_thuc.user:
                thong_tin_nguoi = self.lay_thong_tin_nguoi(phand_hoi_xac_thuc.user.id)
                if not thong_tin_nguoi:
                    return False, "Không tìm thấy người dùng"
                # Lưu phiên hiện tại
                st.session_state.token_xac_thuc = phan_hoi_xac_thuc.session.access_token
                st.session_state.user = thong_tin_nguoi
                return True, thong_tin_nguoi
            return False, "Đăng nhập không hợp lệ"
        except Exception as e:
            return False, str(e)

    def dang_xuat(self):
        """Đăng xuất và xóa session hiện tại."""
        try:
            self.ket_noi_supabase.client.auth.sign_out()
            from auth.session_manager import QuanLyPhien
            QuanLyPhien.xoa_trang_thai_phien()
            return True, None
        except Exception as e:
            return False, str(e)

    def lay_nguoi_hien_tai(self):
        """Lấy thông tin token người dùng đang đăng nhập."""
        try:
            return self.ket_noi_supabase.client.auth.get_user()
        except Exception:
            return None

    def tao_phien_chat(self, nguoi_id, tieu_de=None):
        """Tạo một phiên chat mới cho người dùng."""
        try:
            now = datetime.now()
            tieu_de_mac_dinh = now.strftime('%d-%m-%Y | %H:%M:%S')
            du_lieu_phien = {
                'user_id': nguoi_id,
                'title': tieu_de or tieu_de_mac_dinh,
                'created_at': now.isoformat()
            }
            phan_hoi_db = self.ket_noi_supabase.table('chat_sessions').insert(du_lieu_phien).execute()
            return True, phan_hoi_db.data[0] if phan_hoi_db.data else None
        except Exception as e:
            return False, str(e)

    def lay_cac_phien(self, nguoi_id):
        """Trả về danh sách các phiên chat theo thứ tự mới nhất."""
        try:
            phan_hoi_db = self.ket_noi_supabase.table('chat_sessions')\
                .select('*')\
                .eq('user_id', nguoi_id)\
                .order('created_at', desc=True)\
                .execute()
            return True, phan_hoi_db.data
        except Exception as e:
            st.error(f"Lỗi tải phiên: {e}")
            return False, []

    def luu_nhan(self, phien_id, noi_dung, vai_tro='user'):
        """Lưu nội dung tin nhắn vào cơ sở dữ liệu."""
        try:
            du_lieu_nhan = {
                'session_id': phien_id,
                'content': noi_dung,
                'role': vai_tro,
                'created_at': datetime.now().isoformat()
            }
            phan_hoi_db = self.ket_noi_supabase.table('chat_messages').insert(du_lieu_nhan).execute()
            return True, phan_hoi_db.data[0] if phan_hoi_db.data else None
        except Exception as e:
            return False, str(e)

    def lay_cac_nhan(self, phien_id):
        """Lấy mọi tin nhắn trong phiên, sắp xếp theo thời gian."""
        try:
            phan_hoi_db = self.ket_noi_supabase.table('chat_messages')\
                .select('*')\
                .eq('session_id', phien_id)\
                .order('created_at')\
                .execute()
            return True, phan_hoi_db.data
        except Exception as e:
            return False, str(e)

    def xoa_phien(self, phien_id):
        """Xóa một phiên và tất cả tin nhắn liên quan."""
        try:
            # Xóa tin nhắn trước
            self.ket_noi_supabase.table('chat_messages')\
                .delete()\
                .eq('session_id', phien_id)\
                .execute()
            # Xóa phiên chính
            self.ket_noi_supabase.table('chat_sessions')\
                .delete()\
                .eq('id', phien_id)\
                .execute()
            return True, None
        except Exception as e:
            st.error(f"Xóa phiên thất bại: {e}")
            return False, str(e)

    def kiem_tra_token(self):
        """Xác thực token phiên hiện tại."""
        try:
            phien_hien_tai = self.ket_noi_supabase.client.auth.get_session()
            if not phien_hien_tai or not phien_hien_tai.access_token:
                return None
            if phien_hien_tai.access_token != st.session_state.get('token_xac_thuc'):
                return None
            thong_tin = self.ket_noi_supabase.client.auth.get_user()
            if not thong_tin or not thong_tin.user:
                return None
            return self.lay_thong_tin_nguoi(thong_tin.user.id)
        except Exception:
            return None

    def lay_thong_tin_nguoi(self, nguoi_id):
        """Truy vấn và trả về thông tin chi tiết người dùng từ bảng users."""
        try:
            phan_hoi_db = self.ket_noi_supabase.table('users')\
                .select('*')\
                .eq('id', nguoi_id)\
                .single()\
                .execute()
            return phan_hoi_db.data if phan_hoi_db else None
        except Exception:
            return None
