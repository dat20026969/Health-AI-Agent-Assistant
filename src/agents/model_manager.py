import groq
import streamlit as st
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)

class CapBacMoHinh(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    FALLBACK = "fallback"

class QuanLyMoHinh:
    """
    Quản lý chọn cấp mô hình AI, xử lý dự phòng và giới hạn tần suất yêu cầu.
    Sử dụng cách tiếp cận agent để điều phối mô hình.
    """
    # Định nghĩa cấu hình cho mỗi cấp mô hình
    CAU_HINH_MO_HINH = {
        CapBacMoHinh.PRIMARY:   {"provider": "groq", "model": "meta-llama/llama-4-maverick-17b-128e-instruct", "max_tokens": 2000, "temperature": 0.7},
        CapBacMoHinh.SECONDARY: {"provider": "groq", "model": "llama-3.3-70b-versatile",                  "max_tokens": 2000, "temperature": 0.7},
        CapBacMoHinh.TERTIARY:  {"provider": "groq", "model": "llama-3.1-8b-instant",                    "max_tokens": 2000, "temperature": 0.7},
        CapBacMoHinh.FALLBACK:  {"provider": "groq", "model": "llama3-70b-8192",                        "max_tokens": 2000, "temperature": 0.7}
    }

    def __init__(self):
        self.doi_tac = {}
        self._khoi_tao_doi_tac()

    def _khoi_tao_doi_tac(self):
        """Khởi tạo client API cho mỗi provider."""
        try:
            self.doi_tac['groq'] = groq.Groq(api_key=st.secrets['GROQ_API_KEY'])
        except Exception as e:
            logger.error(f"Khởi tạo client Groq thất bại: {e}")

    def tao_phan_tich(self, du_lieu, thong_diep_he_thong, so_lan_thu=0):
        """
        Sinh phân tích bằng mô hình ưu tiên, tự chuyển cấp khi thất bại.
        Thực hiện logic lựa chọn cấp mô hình dựa trên số lần thử.
        """
        # Nếu đã thử quá 3 lần, kết thúc
        if so_lan_thu > 3:
            return {"success": False, "error": "Tất cả cấp mô hình đều thất bại"}

        # Xác định cấp mô hình theo thứ tự thử
        if so_lan_thu == 0:
            cap = CapBacMoHinh.PRIMARY
        elif so_lan_thu == 1:
            cap = CapBacMoHinh.SECONDARY
        elif so_lan_thu == 2:
            cap = CapBacMoHinh.TERTIARY
        else:
            cap = CapBacMoHinh.FALLBACK

        cfg = self.CAU_HINH_MO_HINH[cap]
        ncc = cfg['provider']
        ma_mo_hinh = cfg['model']

        # Nếu không có client tương ứng, thử cấp tiếp theo
        if ncc not in self.doi_tac:
            logger.error(f"Không tìm thấy client cho provider: {ncc}")
            return self.tao_phan_tich(du_lieu, thong_diep_he_thong, so_lan_thu + 1)

        try:
            client = self.doi_tac[ncc]
            logger.info(f"Sử dụng {ncc} - mô hình {ma_mo_hinh}")

            if ncc == 'groq':
                phan_hoi = client.chat.completions.create(
                    model=ma_mo_hinh,
                    messages=[
                        {"role": "system", "content": thong_diep_he_thong},
                        {"role": "user",   "content": str(du_lieu)}
                    ],
                    temperature=cfg['temperature'],
                    max_tokens=cfg['max_tokens']
                )
                return {"success": True, "content": phan_hoi.choices[0].message.content, "model_used": f"{ncc}/{ma_mo_hinh}"}

        except Exception as e:
            loi = str(e).lower()
            logger.warning(f"Mô hình {ma_mo_hinh} lỗi: {loi}")

            # Nếu lỗi liên quan giới hạn hoặc quota, chờ rồi thử lại
            if 'rate limit' in loi or 'quota' in loi:
                time.sleep(2)
            return self.tao_phan_tich(du_lieu, thong_diep_he_thong, so_lan_thu + 1)

        # Nếu không thành công sau cùng
        return {"success": False, "error": "Không thể phân tích với bất kỳ mô hình nào"}
