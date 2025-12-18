# pages_ui/ask_page.py
import streamlit as st
from config import FAQ
from components.settings_dialog import render_settings_button

def _set_faq_and_jump(q:str):
    st.session_state.page="提問"
    st.session_state.pending_question=q
    st.session_state.auto_ask=True

def _clear_chat_callback():
    # ✅ 用 callback 避免 StreamlitAPIException（不要在 widget 之後直接改 key）
    st.session_state.history=[]
    st.session_state.last_hits=[]
    st.session_state.q_input=""
    st.session_state.pending_question=""
    st.session_state.auto_ask=False

def _ask_flow(question:str,retrieve_fn,build_prompt_fn,chat_fn,collection):
    q=(question or "").strip()
    if not q:
        return

    notice=st.info("🔎 檢索中…")  # 不要全畫面空白，只顯示字樣
    hits=retrieve_fn(q,collection,embed_model=st.session_state.embed_model,top_k=int(st.session_state.top_k))
    st.session_state.last_hits=hits

    notice.info("🧠 生成中…")
    system,user=build_prompt_fn(q,hits)

    try:
        ans=chat_fn(system,user,model=st.session_state.llm_model,temperature=float(st.session_state.temperature)).strip()
    except Exception as e:
        ans=f"⚠️ 模型無法回覆：{e}"

    notice.empty()

    if not ans:
        ans="⚠️ 模型回覆是空白。請確認 Ollama 服務有在跑，且已下載模型。"

    st.session_state.history.append({"q":q,"a":ans,"hits":hits})

def render_ask_page(retrieve_fn,build_prompt_fn,chat_fn,collection,get_db_status_fn):
    # 上方留幾行空間（你說不要太貼頂）
    st.write("")
    st.write("")

    # 若是從常用問題跳過來：先切到提問頁，再開始回答
    if st.session_state.get("auto_ask",False) and st.session_state.get("pending_question",""):
        pq=st.session_state.pending_question
        st.session_state.q_input=pq
        _ask_flow(pq,retrieve_fn,build_prompt_fn,chat_fn,collection)
        st.session_state.auto_ask=False
        st.session_state.pending_question=""
        st.rerun()

    left,right=st.columns([1.25,1],gap="large")

    with left:
        st.subheader("輸入你的問題")
        st.text_area(" ",height=110,placeholder="例如：病假需要證明嗎？",key="q_input")

        c1,c2=st.columns(2)
        with c1:
            if st.button("送出",type="primary",use_container_width=True,disabled=not st.session_state.q_input.strip()):
                _ask_flow(st.session_state.q_input,retrieve_fn,build_prompt_fn,chat_fn,collection)
                st.rerun()
        with c2:
            st.button("清空對話",use_container_width=True,on_click=_clear_chat_callback)

        st.subheader("回答")
        if not st.session_state.history:
            st.caption("尚未提問。")
        else:
            st.write(st.session_state.history[-1]["a"])

    with right:
        st.subheader("常用問題")
        cat=st.selectbox("分類",list(FAQ.keys()))
        for item in FAQ[cat]:
            st.button(item,use_container_width=True,on_click=_set_faq_and_jump,args=(item,))

    st.write("")
    st.markdown('<div class="glass">',unsafe_allow_html=True)
    st.subheader("引用內容")
    hits=st.session_state.last_hits or []
    if not hits:
        st.caption("尚未提問或沒有找到可用內容。")
    else:
        st.success(f"已找到 {len(hits)} 段內容")
        for i,h in enumerate(hits,start=1):
            src=(h.meta or {}).get("source","unknown")
            page=(h.meta or {}).get("page",None)
            title=f"[{i}] {src}"+(f"（第{page}頁）" if page else "")
            with st.expander(title,expanded=(i==1)):
                st.code((h.text or "")[:3500])
    st.markdown("</div>",unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="glass">',unsafe_allow_html=True)
    st.subheader("歷史問題")
    with st.expander("點我展開/收合"):
        if not st.session_state.history:
            st.caption("目前沒有歷史提問。")
        else:
            for idx,qa in enumerate(reversed(st.session_state.history),start=1):
                st.markdown(f"**Q{idx}:** {qa['q']}")
                st.write(qa["a"])
                st.divider()
    st.markdown("</div>",unsafe_allow_html=True)

    st.write("")
    # ✅ 設定按鈕放到最下面左側（提問頁底部）
    render_settings_button(button_key="settings_btn_ask")
