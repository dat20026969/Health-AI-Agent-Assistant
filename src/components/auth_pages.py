import streamlit as st
from auth.session_manager import QuanLyPhienDangNhap
from config.app_config import APP_ICON, APP_NAME, APP_TAGLINE, APP_DESCRIPTION
from utils.validators import validate_signup_fields
import time
import re


def hien_thi_trang_dang_nhap():
    """
    Hiển thị trang đăng nhập/đăng ký với tùy chọn chuyển đổi giữa hai form.
    """
    # KHÔNG ĐƯỢC thay đổi vị trí câu lệnh này
    if 'kieu_form' not in st.session_state:
        st.session_state['kieu_form'] = 'dang_nhap'

    kieu_form_hien_tai = st.session_state['kieu_form']

    # Ẩn hướng dẫn gửi form mặc định của Streamlit
    st.markdown("""
        <style>
            div[data-testid="InputInstructions"] > span:nth-child(1) {
                visibility: hidden;
            }
        </style>
    """, unsafe_allow_html=True)

    # Tiêu đề ứng dụng
    st.markdown(f"""
        <div style='text-align: center; padding: 2rem;'>
            <h1>{APP_ICON} {APP_NAME}</h1>
            <h3>{APP_DESCRIPTION}</h3>
            <p style='font-size:1.2em; color:#666; margin-bottom:1em;'>{APP_TAGLINE}</p>
            <h3>{'Chào mừng quay lại!' if kieu_form_hien_tai=='dang_nhap' else 'Chào mừng!'}</h3>
        </div>
    """, unsafe_allow_html=True)

    # Căn giữa form
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if kieu_form_hien_tai == 'dang_nhap':
            hien_thi_form_dang_nhap()
        else:
            hien_thi_form_dang_ky()

        st.markdown('---')
        chu_toggle = ('Chưa có tài khoản? Đăng ký' if kieu_form_hien_tai=='dang_nhap' else 'Đã có tài khoản? Đăng nhập')
        if st.button(chu_toggle, use_container_width=True, type='secondary'):
            st.session_state['kieu_form'] = 'dang_ky' if kieu_form_hien_tai=='dang_nhap' else 'dang_nhap'
            st.rerun()


def hien_thi_form_dang_nhap():
    """Hiển thị form đăng nhập."""
    with st.form('form_dang_nhap'):
        email = st.text_input('Email', key='login_email')
        mat_khau = st.text_input('Mật khẩu', type='password', key='login_password')
        if st.form_submit_button('Đăng nhập', use_container_width=True, type='primary'):
            if email and mat_khau:
                thanh_cong, ket_qua = QuanLyPhien.thuc_hien_dang_nhap(email, mat_khau)
                if thanh_cong:
                    with st.spinner('Đang đăng nhập...'):
                        placeholder = st.empty()
                        placeholder.success('Đăng nhập thành công! Chuyển hướng...')
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error(f"Đăng nhập thất bại: {ket_qua}")
            else:
                st.error('Vui lòng nhập email và mật khẩu đầy đủ.')


def hien_thi_form_dang_ky():
    """Hiển thị form đăng ký tài khoản mới."""
    with st.form('form_dang_ky'):
        ten_day_du = st.text_input('Họ và tên', key='signup_name')
        email_moi = st.text_input('Email', key='signup_email')
        mat_khau_moi = st.text_input('Mật khẩu', type='password', key='signup_password')
        xac_nhan_mk = st.text_input('Xác nhận mật khẩu', type='password', key='signup_password2')

        st.markdown('''
            Yêu cầu mật khẩu:
            - Tối thiểu 8 ký tự
            - Ít nhất 1 chữ hoa
            - Ít nhất 1 chữ thường
            - Ít nhất 1 số
        ''')

        if st.form_submit_button('Đăng ký', use_container_width=True, type='primary'):
            hop_le, thong_bao = validate_signup_fields(ten_day_du, email_moi, mat_khau_moi, xac_nhan_mk)
            if not hop_le:
                st.error(thong_bao)
                return
            with st.spinner('Đang tạo tài khoản...'):
                thanh_cong, phan_hoi = st.session_state['dich_vu_xac_thuc'].dang_ky_tai_khoan(
                    email_moi, mat_khau_moi, ten_day_du
                )
                if thanh_cong:
                    st.session_state['user'] = phan_hoi
                    st.session_state['authenticated'] = True
                    st.success('Tạo tài khoản thành công! Chuyển hướng...')
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Đăng ký thất bại: {phan_hoi}")