from datetime import datetime, timedelta
import streamlit as st
from agents.model_manager import ModelManager

class AgentPhanTich:
    """
    Tác nhân quản lý việc phân tích báo cáo, giới hạn tần suất,
    và áp dụng học ngữ cảnh từ các phân tích trước đó.
    """
    
    def __init__(self):
        self.quan_ly_mo_hinh = ModelManager()
        self._khoi_tao_trang_thai()
        
    def _khoi_tao_trang_thai(self):
        """Khởi tạo các biến lưu trạng thái liên quan đến phân tích trong session."""
        if 'luot_phan_tich' not in st.session_state:
            st.session_state.luot_phan_tich = 0
        if 'thoi_diem_phan_tich_cuoi' not in st.session_state:
            st.session_state.thoi_diem_phan_tich_cuoi = datetime.now()
        if 'gioi_han_hang_ngay' not in st.session_state:
            st.session_state.gioi_han_hang_ngay = 15
        if 'thong_ke_mo_hinh' not in st.session_state:
            st.session_state.thong_ke_mo_hinh = {}
        if 'co_so_kien_thuc' not in st.session_state:
            st.session_state.co_so_kien_thuc = {}
            
    def kiem_tra_gioi_han(self):
        """Kiểm tra xem người dùng đã đạt giới hạn phân tích theo ngày chưa."""
        # Tính khoảng thời gian còn đến khi reset
        thoi_gian_con_lai = timedelta(days=1) - (datetime.now() - st.session_state.thoi_diem_phan_tich_cuoi)
        gio, phut = divmod(thoi_gian_con_lai.seconds, 3600)
        phut, _ = divmod(phut, 60)
        
        # Nếu quá 24h, reset bộ đếm
        if thoi_gian_con_lai.days < 0:
            st.session_state.luot_phan_tich = 0
            st.session_state.thoi_diem_phan_tich_cuoi = datetime.now()
            return True, None
        
        # Nếu đã vượt ngưỡng
        if st.session_state.luot_phan_tich >= st.session_state.gioi_han_hang_ngay:
            thong_bao = f"Đã đạt giới hạn {st.session_state.gioi_han_hang_ngay} lần/ngày. Reset sau {gio}h {phut}m"
            return False, thong_bao
        return True, None

    def phan_tich_bao_cao(self, du_lieu, thong_diep_he_thong, chi_kiem_tra=False, lich_su_chat=None):
        """
        Thực hiện phân tích dữ liệu báo cáo với học ngữ cảnh.

        Args:
            du_lieu: Dữ liệu báo cáo
            thong_diep_he_thong: Thông điệp gốc cho mô hình
            chi_kiem_tra: Nếu True, chỉ kiểm tra giới hạn, không trả kết quả
            lich_su_chat: Lịch sử trao đổi trong session (nếu có)
        """
        cho_phep, loi = self.kiem_tra_gioi_han()
        if not cho_phep:
            return {"success": False, "error": loi}
        if chi_kiem_tra:
            return cho_phep, loi
        
        # Xử lý tiền dữ liệu
        du_lieu_xuly = self._tien_xu_ly_du_lieu(du_lieu)
        
        # Xây dựng lời nhắc nâng cao nếu có lịch sử chat
        loi_nhan = (self.xay_dung_loi_nhan_nang_cao(thong_diep_he_thong, du_lieu_xuly, lich_su_chat)
                    if lich_su_chat else thong_diep_he_thong)
        
        # Gọi mô hình để sinh phân tích
        ket_qua = self.quan_ly_mo_hinh.generate_analysis(du_lieu_xuly, loi_nhan)
        
        if ket_qua.get("success"):
            self.cap_nhat_thong_ke(ket_qua)
            self.cap_nhat_co_so_kien_thuc(du_lieu_xuly, ket_qua.get("content"))
        return ket_qua
    
    def cap_nhat_thong_ke(self, ket_qua):
        """Cập nhật số lần phân tích và thống kê mô hình đã dùng."""
        st.session_state.luot_phan_tich += 1
        st.session_state.thoi_diem_phan_tich_cuoi = datetime.now()
        mo_hinh = ket_qua.get("model_used", "unknown")
        st.session_state.thong_ke_mo_hinh[mo_hinh] = st.session_state.thong_ke_mo_hinh.get(mo_hinh, 0) + 1
    
    def cap_nhat_co_so_kien_thuc(self, du_lieu, phan_tich):
        """
        Lưu trữ các chỉ số y tế chính và trích đoạn phân tích tương ứng
        để phục vụ học ngữ cảnh sau này.
        """
        if not isinstance(du_lieu, dict) or 'report' not in du_lieu:
            return
        van_ban = du_lieu['report'].lower()
        ho_so = f"{du_lieu.get('age','unknown')}-{du_lieu.get('gender','unknown')}"
        chi_so_ds = ["hemoglobin","glucose","cholesterol","triglycerides",
                     "hdl","ldl","wbc","rbc","platelet","creatinine"]
        for chi_so in chi_so_ds:
            if chi_so in van_ban and chi_so in phan_tich.lower():
                st.session_state.co_so_kien_thuc.setdefault(chi_so, {}).setdefault(ho_so, [])
                dong = [l for l in phan_tich.split('\n') if chi_so in l.lower()]
                if dong:
                    if len(st.session_state.co_so_kien_thuc[chi_so][ho_so]) >= 3:
                        st.session_state.co_so_kien_thuc[chi_so][ho_so].pop(0)
                    st.session_state.co_so_kien_thuc[chi_so][ho_so].append(dong[0])
    
    def xay_dung_loi_nhan_nang_cao(self, thong_diep, du_lieu, lich_su_chat):
        """
        Ghép ngữ cảnh từ cơ sở kiến thức và lịch sử session vào lời nhắc.
        """
        noi_dung = thong_diep
        # Thêm ngữ cảnh từ kiến thức trước
        if isinstance(du_lieu, dict) and 'report' in du_lieu:
            nguon = self.lay_nguon_co_so(du_lieu)
            if nguon:
                noi_dung += "\n\n## Học ngữ cảnh trước đó\n" + nguon
        # Thêm ngữ cảnh từ lịch sử chat
        if lich_su_chat:
            lich = self.lay_lich_su_phien(lich_su_chat)
            if lich:
                noi_dung += "\n\n## Lịch sử session\n" + lich
        return noi_dung
    
    def lay_nguon_co_so(self, du_lieu):
        """Trích các mục liên quan từ cơ sở kiến thức."""
        if not st.session_state.co_so_kien_thuc:
            return ""
        van_ban = du_lieu.get('report','').lower()
        ho_so = f"{du_lieu.get('age','unknown')}-{du_lieu.get('gender','unknown')}"
        ket_qua = []
        for chi_so, profiles in st.session_state.co_so_kien_thuc.items():
            if chi_so in van_ban:
                if ho_so in profiles:
                    ket_qua += [f"- {chi_so} (hồ sơ tương tự): {insight}" for insight in profiles[ho_so]]
                for prof, insights in profiles.items():
                    if prof != ho_so:
                        ket_qua += [f"- {chi_so} (hồ sơ khác): {insight}" for insight in insights]
        return "\n".join(ket_qua[:5])
    
    def lay_lich_su_phien(self, lich_su_chat):
        """Lấy tối đa hai lượt trao đổi cuối từ lịch sử session."""
        if not lich_su_chat or len(lich_su_chat) < 2:
            return ""
        ket_qua = []
        for i in range(len(lich_su_chat)-1, 0, -2):
            if lich_su_chat[i-1]['role']=='user' and lich_su_chat[i]['role']=='assistant':
                user_msg = lich_su_chat[i-1]['content']
                ai_msg = lich_su_chat[i]['content']
                if len(user_msg)>200: user_msg=user_msg[:197]+"..."
                if len(ai_msg)>200: ai_msg=ai_msg[:197]+"..."
                ket_qua.append(f"Người dùng: {user_msg}\nTrợ lý: {ai_msg}")
                if len(ket_qua)==2: break
        return "\n\n".join(reversed(ket_qua))
