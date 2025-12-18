# pages_ui/db_page.py
import streamlit as st
from components.settings_dialog import render_settings_button

def render_db_page(ingest_uploaded_pdfs_fn,clear_all_fn,get_db_status_fn,collection,upload_dir:str):
    st.write("")
    st.write("")

    st.markdown("## 資料庫")

    status=get_db_status_fn(collection)
    st.markdown(
        f'<div class="glass">📦 已匯入文件數：<b>{status["unique_sources"]}</b>　｜　🧩 內容段數：<b>{status["total_chunks"]}</b></div>',
        unsafe_allow_html=True,
    )
    st.write("")

    st.markdown('<div class="glass">',unsafe_allow_html=True)
    st.subheader("上傳 PDF")
    up_files=st.file_uploader(" ",type=["pdf"],accept_multiple_files=True)

    c1,c2=st.columns([1,1])
    with c1:
        if st.button("匯入到資料庫",type="primary",use_container_width=True,disabled=not up_files):
            notice=st.info("📥 匯入中…")
            scanned,added,skipped,notes=ingest_uploaded_pdfs_fn(
                uploaded_files=up_files,
                upload_dir=upload_dir,
                collection=collection,
                embed_model=st.session_state.embed_model,
                chunk_size=int(st.session_state.chunk_size),
                overlap=int(st.session_state.overlap),
            )
            notice.empty()
            st.success(f"完成：處理 {scanned} 份 PDF，新增/更新 {added} 段內容。")
            if skipped>0:
                st.warning(f"有 {skipped} 份 PDF 抽不到文字或匯入失敗（可能需要 OCR）。")
                with st.expander("查看原因"):
                    for n in notes:
                        st.write("• "+n)
            st.rerun()

    with c2:
        if st.button("清空資料庫",use_container_width=True):
            clear_all_fn(collection)
            st.success("已清空。")
            st.rerun()

    st.markdown("</div>",unsafe_allow_html=True)

    st.write("")
    render_settings_button(button_key="settings_btn_db")
