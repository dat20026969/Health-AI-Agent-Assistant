import pdfplumber
import streamlit as st
from config.app_config import SO_TRANG_PDF_TOI_DA
from utils.validators import validate_pdf_file, validate_pdf_content

def trich_text_tu_pdf(tep_pdf):
    """
    Trích xuất và kiểm tra hợp lệ nội dung từ file PDF.
    Trả về chuỗi văn bản hoặc thông báo lỗi.
    """
    try:
        # Kiểm tra file đầu vào
        hop_le, loi = validate_pdf_file(tep_pdf)
        if not hop_le:
            return loi

        van_ban = ""
        with pdfplumber.open(tep_pdf) as pdf:
            # Giới hạn số trang tối đa
            if len(pdf.pages) > SO_TRANG_PDF_TOI_DA:
                return f"PDF vượt quá giới hạn {SO_TRANG_PDF_TOI_DA} trang"

            # Lặp qua từng trang để trích text
            for trang in pdf.pages:
                doan = trang.extract_text()
                if not doan:
                    return "Không thể trích text từ PDF. Vui lòng kiểm tra xem có phải file quét (scan) không."
                van_ban += doan + "\n"
        
        # Kiểm tra nội dung đã trích
        hop_le, loi = validate_pdf_content(van_ban)
        if not hop_le:
            return loi

        return van_ban

    except Exception as e:
        return f"Lỗi khi trích xuất text từ PDF: {e}"
