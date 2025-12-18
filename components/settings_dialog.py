# components/settings_dialog.py
import streamlit as st
from config import (
    DEFAULT_LLM_MODEL,DEFAULT_EMBED_MODEL,DEFAULT_TOP_K,
    DEFAULT_CHUNK_SIZE,DEFAULT_OVERLAP,DEFAULT_TEMPERATURE
)

def _init_settings_state():
    st.session_state.setdefault("llm_model",DEFAULT_LLM_MODEL)
    st.session_state.setdefault("embed_model",DEFAULT_EMBED_MODEL)
    st.session_state.setdefault("top_k",DEFAULT_TOP_K)
    st.session_state.setdefault("chunk_size",DEFAULT_CHUNK_SIZE)
    st.session_state.setdefault("overlap",DEFAULT_OVERLAP)
    st.session_state.setdefault("temperature",DEFAULT_TEMPERATURE)

def open_settings():
    st.session_state.show_settings=True

def render_settings_button(button_key:str):
    _init_settings_state()
    # 放在頁面最下面左側：你在 page 裡面呼叫它就好
    if st.button("⚙️ 設定參數",key=button_key,use_container_width=False):
        st.session_state.show_settings=True
        st.rerun()

def render_settings_dialog():
    _init_settings_state()
    if not st.session_state.get("show_settings",False):
        return

    @st.dialog("設定參數")
    def _dlg():
        llm=st.text_input("LLM 模型",value=st.session_state.llm_model)
        emb=st.text_input("Embedding 模型",value=st.session_state.embed_model)

        c1,c2=st.columns(2)
        with c1:
            top_k=st.number_input("Top-k",min_value=1,max_value=20,value=int(st.session_state.top_k))
            chunk_size=st.number_input("Chunk size",min_value=200,max_value=2000,value=int(st.session_state.chunk_size),step=50)
        with c2:
            overlap=st.number_input("Overlap",min_value=0,max_value=600,value=int(st.session_state.overlap),step=10)
            temperature=st.slider("Temperature",0.0,1.0,float(st.session_state.temperature),step=0.05)

        st.write("")

        b1,b2=st.columns([1,1])
        with b1:
            if st.button("💾 儲存",type="primary",use_container_width=True):
                st.session_state.llm_model=llm.strip() or DEFAULT_LLM_MODEL
                st.session_state.embed_model=emb.strip() or DEFAULT_EMBED_MODEL
                st.session_state.top_k=int(top_k)
                st.session_state.chunk_size=int(chunk_size)
                st.session_state.overlap=int(overlap)
                st.session_state.temperature=float(temperature)
                st.session_state.show_settings=False
                st.success("已儲存")
                st.rerun()
        with b2:
            if st.button("取消",use_container_width=True):
                st.session_state.show_settings=False
                st.rerun()

    _dlg()
