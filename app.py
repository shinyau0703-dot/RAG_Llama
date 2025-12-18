# app.py
import streamlit as st
from config import APP_TITLE,DB_DIR,KB_DIR,UPLOAD_DIR,COLLECTION_NAME
from styles import APP_CSS

from components.sidebar import render_sidebar
from components.settings_dialog import render_settings_dialog

from pages_ui.ask_page import render_ask_page
from pages_ui.db_page import render_db_page

from rag import (
    get_client,
    get_collection,
    ingest_uploaded_pdfs,
    retrieve,
    build_prompt,
    chat_llm,
    clear_all,
    get_db_status,
)

st.set_page_config(page_title=APP_TITLE,layout="wide")

# CSS
st.markdown(APP_CSS,unsafe_allow_html=True)

# 需要的資料夾
UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
DB_DIR.mkdir(parents=True,exist_ok=True)

# session state init
st.session_state.setdefault("page","提問")
st.session_state.setdefault("history",[])
st.session_state.setdefault("last_hits",[])
st.session_state.setdefault("pending_question","")
st.session_state.setdefault("auto_ask",False)
st.session_state.setdefault("q_input","")
st.session_state.setdefault("show_settings",False)

# settings defaults（避免沒設定就被 pages 使用）
st.session_state.setdefault("llm_model","llama3.1")
st.session_state.setdefault("embed_model","nomic-embed-text")
st.session_state.setdefault("top_k",6)
st.session_state.setdefault("chunk_size",800)
st.session_state.setdefault("overlap",120)
st.session_state.setdefault("temperature",0.2)

# DB
client=get_client(str(DB_DIR))
collection=get_collection(client,COLLECTION_NAME)

# Sidebar
render_sidebar(APP_TITLE)

# Settings dialog（點按鈕才會出現）
render_settings_dialog()

# Router
if st.session_state.page=="資料庫":
    render_db_page(
        ingest_uploaded_pdfs_fn=ingest_uploaded_pdfs,
        clear_all_fn=clear_all,
        get_db_status_fn=get_db_status,
        collection=collection,
        upload_dir=str(UPLOAD_DIR),
    )
else:
    render_ask_page(
        retrieve_fn=retrieve,
        build_prompt_fn=build_prompt,
        chat_fn=chat_llm,
        collection=collection,
        get_db_status_fn=get_db_status,
    )
