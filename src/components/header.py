import streamlit as st


def hien_thi_tieu_de():
    """Hiển thị phần header chào người dùng ở góc trên bên phải."""
    # Nếu đã đăng nhập, lấy tên hoặc email để chào
    if st.session_state.get('user'):
        ten_hien_thi = st.session_state.user.get('name') or st.session_state.user.get('email', '')
        st.markdown(f"""
            <div style='
                text-align: right;
                padding: 1rem;
                color: #64B5F6;
                font-size: 1.1em;
            '>
                👋 Xin chào, {ten_hien_thi}
            </div>
        """, unsafe_allow_html=True)

