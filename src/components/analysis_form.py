import streamlit as st
from services.ai_service import generate_analysis
from config.prompts import SPECIALIST_PROMPTS
from utils.pdf_extractor import extract_text_from_pdf
from config.sample_data import SAMPLE_REPORT
from config.app_config import MAX_UPLOAD_SIZE_MB


def hien_thi_bieu_mau_phan_tich():
    # Khởi tạo nguồn báo cáo cho phiên mới
    if 'current_session' in st.session_state and 'nguon_bao_cao' not in st.session_state:
        st.session_state.nguon_bao_cao = "Tải PDF lên"
    
    nguon = st.radio(
        "Chọn nguồn báo cáo",
        ["Tải PDF lên", "Sử dụng mẫu PDF"],
        index=0 if st.session_state.get('nguon_bao_cao') == "Tải PDF lên" else 1,
        horizontal=True,
        key='nguon_bao_cao'
    )

    noi_dung_pdf = lay_noi_dung_bao_cao(nguon)
    
    # Nếu có nội dung báo cáo, hiển thị form nhập thông tin bệnh nhân
    if noi_dung_pdf:
        hien_thi_bieu_mau_benh_nhan(noi_dung_pdf)


def lay_noi_dung_bao_cao(nguon_bao_cao):
    if nguon_bao_cao == "Tải PDF lên":
        tep_tai_len = st.file_uploader(
            f"Tải lên báo cáo máu (Tối đa {MAX_UPLOAD_SIZE_MB}MB)",
            type=['pdf'],
            help=f"Dung lượng tối đa {MAX_UPLOAD_SIZE_MB}MB. Chỉ hỗ trợ file PDF chứa báo cáo y tế."
        )
        if tep_tai_len:
            # Kiểm tra dung lượng trước khi trích xuất
            dung_luong_mb = tep_tai_len.size / (1024 * 1024)
            if dung_luong_mb > MAX_UPLOAD_SIZE_MB:
                st.error(f"Dung lượng ({dung_luong_mb:.1f}MB) vượt quá giới hạn {MAX_UPLOAD_SIZE_MB}MB.")
                return None
            
            if tep_tai_len.type != 'application/pdf':
                st.error("Vui lòng tải lên file PDF hợp lệ.")
                return None
            
            text = extract_text_from_pdf(tep_tai_len)
            # Nếu trả về lỗi từ extractor
            if isinstance(text, str) and (
                text.startswith(("File size exceeds", "Invalid file type", "Error validating")) or
                text.startswith("The uploaded file") or
                "error" in text.lower()
            ):
                st.error(text)
                return None
            
            with st.expander("Xem báo cáo đã trích xuất"):
                st.text(text)
            return text
    else:
        with st.expander("Xem báo cáo mẫu"):
            st.text(SAMPLE_REPORT)
        return SAMPLE_REPORT
    return None


def hien_thi_bieu_mau_benh_nhan(noi_dung_pdf):
    with st.form("phan_tich_form"):
        ten_bn = st.text_input("Tên bệnh nhân")
        cot1, cot2 = st.columns(2)
        with cot1:
            tuoi = st.number_input("Tuổi", min_value=0, max_value=120)
        with cot2:
            gioi_tinh = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"])
        
        if st.form_submit_button("Phân tích báo cáo"):
            xu_ly_gui_bieu_mau(ten_bn, tuoi, gioi_tinh, noi_dung_pdf)


def xu_ly_gui_bieu_mau(ten_bn, tuoi, gioi_tinh, noi_dung):
    # Kiểm tra nhập liệu
    if not all([ten_bn, tuoi, gioi_tinh]):
        st.error("Vui lòng điền đầy đủ thông tin.")
        return

    # Kiểm tra giới hạn phân tích trước khi hiển thị spinner
    cho_phep, thong_bao = generate_analysis(None, None, check_only=True)
    if not cho_phep:
        st.error(thong_bao)
        st.stop()
        return

    with st.spinner("Đang phân tích báo cáo..."):
        # Lưu tin nhắn user
        st.session_state.dich_vu_xac_thuc.luu_nhan(
            st.session_state.current_session['id'],
            f"Phân tích báo cáo cho bệnh nhân: {ten_bn}"
        )
        
        # Gọi sinh phân tích từ service
        ket_qua = generate_analysis(
            {"patient_name": ten_bn, "age": tuoi, "gender": gioi_tinh, "report": noi_dung},
            SPECIALIST_PROMPTS["comprehensive_analyst"]
        )
        
        if ket_qua["success"]:
            noi_dung_pt = ket_qua["content"]
            # Thêm thông tin mô hình nếu có
            if "model_used" in ket_qua:
                noi_dung_pt += f"\n\n*Phân tích sử dụng {ket_qua['model_used']}*"
            # Lưu phản hồi từ assistant
            st.session_state.dich_vu_xac_thuc.luu_nhan(
                st.session_state.current_session['id'],
                noi_dung_pt,
                role='assistant'
            )
            st.rerun()
        else:
            st.error(ket_qua["error"])
            st.stop()
