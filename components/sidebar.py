# components/sidebar.py
import streamlit as st

def render_sidebar(title:str)->None:
    with st.sidebar:
        st.markdown(f'<div class="rag-title">{title}</div>',unsafe_allow_html=True)

        def nav(label:str):
            active=(st.session_state.page==label)
            btn_type="primary" if active else "secondary"
            if st.button(label,use_container_width=True,type=btn_type):
                st.session_state.page=label
                st.rerun()

        # 只要兩個選項
        nav("提問")
        nav("資料庫")
