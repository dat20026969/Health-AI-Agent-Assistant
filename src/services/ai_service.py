import streamlit as st
from agents.analysis_agent import AgentPhanTich

def khoi_tao_trang_thai_phan_tich():
    """Khởi tạo đối tượng phân tích trong session state nếu chưa tồn tại."""
    if 'tac_nghiep_phan_tich' not in st.session_state:
        st.session_state.tac_nghiep_phan_tich = AgentPhanTich()

def kiem_tra_han_muc():
    """Kiểm tra xem người dùng còn hạn mức phân tích hàng ngày hay không."""
    # Đảm bảo agent phân tích đã được khởi tạo
    khoi_tao_trang_thai_phan_tich()
    return st.session_state.tac_nghiep_phan_tich.kiem_tra_gioi_han()

def sinh_phan_tich(du_lieu, thong_diep, chi_kiem_tra=False, ma_phien=None):
    """
    Sinh phân tích báo cáo nếu trong hạn mức.

    Args:
        du_lieu: dict chứa dữ liệu báo cáo
        thong_diep: prompt gốc gửi cho mô hình
        chi_kiem_tra: nếu True chỉ kiểm tra hạn mức, không sinh phân tích
        ma_phien: tùy chọn, ID phiên để lấy lịch sử chat (hiện chưa dùng)
    """
    # Đảm bảo agent phân tích đã được khởi tạo
    khoi_tao_trang_thai_phan_tich()

    # Nếu chỉ cần kiểm tra hạn mức
    if chi_kiem_tra:
        return st.session_state.tac_nghiep_phan_tich.kiem_tra_gioi_han()

    # (Nếu muốn, có thể lấy lịch sử chat dựa trên ma_phien ở đây)

    # Thực hiện phân tích báo cáo
    return st.session_state.tac_nghiep_phan_tich.phan_tich_bao_cao(
        du_lieu,
        thong_diep,
        chi_kiem_tra=False
    )
