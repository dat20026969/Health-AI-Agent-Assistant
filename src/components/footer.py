import streamlit as st
import requests
import time
from config.app_config import PRIMARY_COLOR, SECONDARY_COLOR


def lay_luot_star_tren_github():
    """Lấy số sao của repo trên GitHub."""
    try:
        ket_qua = requests.get("https://api.github.com/repos/harshhh28/hia")
        if ket_qua.status_code == 200:
            return ket_qua.json().get("stargazers_count")
        return None
    except:
        return None


def hien_thi_chan_trang(o_thanh_cong=False):
    """Hiển thị chân trang, có thể ở thanh bên."""
    # Cache kết quả star GitHub 1 giờ
    @st.cache_data(ttl=3600)
    def lay_star_cache():
        return lay_luot_star_tren_github()

    so_star = lay_star_cache()

    # Định nghĩa style cơ bản
    style_co_ban = f"""
        text-align: center;
        padding: 0.75rem;
        background: linear-gradient(to right, 
            rgba(25,118,210,0.03),
            rgba(100,181,246,0.05),
            rgba(25,118,210,0.03)
        );
        border-top: 1px solid rgba(100,181,246,0.15);
        margin-top: {'0' if o_thanh_cong else '2rem'};
        {'width:100%' if not o_thanh_cong else ''};
        box-shadow: 0 -2px 10px rgba(100,181,246,0.05);
    """

    st.markdown(
        f"""
        <div style='{style_co_ban}'>
            <p style='
                font-family:"Source Sans Pro",sans-serif;
                color:#64B5F6;
                font-size:0.75rem;
                letter-spacing:0.02em;
                margin:0;
                opacity:0.95;
                display:flex;
                flex-direction:column;
                align-items:center;
                justify-content:center;
                gap:8px;
            '>
                <!-- Đoạn liên kết đến GitHub -->
                <span style="
                    display:flex;
                    align-items:center;
                    gap:4px;
                    padding:2px 8px;
                    border-radius:4px;
                    background:rgba(100,181,246,0.05);
                    transition:all 0.2s ease;
                ">
                    <a href='https://github.com/harshhh28/hia' target='_blank' style='
                           color:#64B5F6;
                           text-decoration:none;
                           font-weight:500;
                           display:inline-flex;
                           align-items:center;
                           gap:4px;
                       '
                       onmouseover="this.style.color='{PRIMARY_COLOR}'; this.style.textDecoration='underline'"
                       onmouseout="this.style.color='#1976D2'; this.style.textDecoration='none'">
                        <span>Contribute to HIA</span>
                        <!-- Biểu tượng GitHub -->
                        <svg height='12' width='12' viewBox='0 0 16 16' fill='#64B5F6'>
                            <path d='M8 0C3.58 0...'></path>
                        </svg>
                        {f'<span style="margin-left:4px; display:inline-flex; align-items:center; gap:4px; color:#64B5F6;">
                            <svg height="12" width="12" viewBox="0 0 16 16" fill="#64B5F6">
                                <path d="M8 .25a.75.75 0 01..."/>
                            </svg>
                            {so_star}
                        </span>' if so_star is not None else ''}
                    </a>
                </span>
                <!-- Liên kết tác giả -->
                <span style="
                    display:flex;
                    align-items:center;
                    gap:4px;
                    color:#1976D2;
                    transition:all 0.2s ease;
                ">
                    <a href='https://harshgajjar.vercel.app' target='_blank' style='
                           color:#1976D2;
                           text-decoration:none;
                           font-weight:500;
                           display:inline-flex;
                           align-items:center;
                           gap:4px;
                       '
                       onmouseover="this.style.color='{PRIMARY_COLOR}'; this.style.textDecoration='underline'"
                       onmouseout="this.style.color='#1976D2'; this.style.textDecoration='none'">
                       Created by Harsh Gajjar
                    </a>
                </span>
            </p>
        </div>
        """, unsafe_allow_html=True
    )
