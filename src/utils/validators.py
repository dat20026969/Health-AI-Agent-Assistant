import re
from config.app_config import KICH_THUOC_TEP_TOI_DA_MB

def kiem_tra_mat_khau(mat_khau):
    """Kiểm tra mật khẩu có đáp ứng yêu cầu bảo mật không."""
    if len(mat_khau) < 8:
        return False, "Mật khẩu phải có ít nhất 8 ký tự"
    if not any(c.isupper() for c in mat_khau):
        return False, "Mật khẩu phải chứa ít nhất 1 chữ hoa"
    if not any(c.islower() for c in mat_khau):
        return False, "Mật khẩu phải chứa ít nhất 1 chữ thường"
    if not any(c.isdigit() for c in mat_khau):
        return False, "Mật khẩu phải chứa ít nhất 1 chữ số"
    return True, None

def kiem_tra_email(email):
    """Kiểm tra định dạng email có hợp lệ không."""
    bieu_thuc = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(bieu_thuc, email))

def kiem_tra_dang_ky(ten, email, mat_khau, xac_nhan_mk):
    """Kiểm tra tất cả trường khi đăng ký tài khoản."""
    if not all([ten, email, mat_khau, xac_nhan_mk]):
        return False, "Vui lòng điền đầy đủ thông tin"
    if not kiem_tra_email(email):
        return False, "Vui lòng nhập email hợp lệ"
    if mat_khau != xac_nhan_mk:
        return False, "Mật khẩu và xác nhận mật khẩu không khớp"
    hop_le, loi = kiem_tra_mat_khau(mat_khau)
    if not hop_le:
        return False, loi
    return True, None

def kiem_tra_file_pdf(file):
    """Kiểm tra file upload có phải PDF và không vượt kích thước không."""
    if not file:
        return False, "Chưa tải lên file nào"
    dung_luong_mb = file.size / (1024 * 1024)
    if dung_luong_mb > KICH_THUOC_TEP_TOI_DA_MB:
        return False, f"Dung lượng ({dung_luong_mb:.1f}MB) vượt quá giới hạn {KICH_THUOC_TEP_TOI_DA_MB}MB"
    if file.type != 'application/pdf':
        return False, "Loại file không hợp lệ. Vui lòng tải lên file PDF"
    return True, None

def kiem_tra_noi_dung_pdf(text):
    """Kiểm tra nội dung trích xuất từ PDF có phải báo cáo y tế không."""
    # Một số từ khóa thường gặp trong báo cáo y tế
    tu_khoa_y_te = [
        'blood', 'test', 'report', 'laboratory', 'lab', 'patient', 'specimen',
        'reference range', 'analysis', 'results', 'medical', 'diagnostic',
        'hemoglobin', 'wbc', 'rbc', 'platelet', 'glucose', 'creatinine'
    ]
    # Độ dài tối thiểu để xem là có nội dung
    if len(text.strip()) < 50:
        return False, "Nội dung trích xuất quá ngắn. Vui lòng tải lên báo cáo hợp lệ."
    lower_text = text.lower()
    dem_khoa = sum(1 for tk in tu_khoa_y_te if tk in lower_text)
    if dem_khoa < 3:
        return False, "File tải lên không giống báo cáo y tế. Vui lòng kiểm tra lại."
    return True, None
