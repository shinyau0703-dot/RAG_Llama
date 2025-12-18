# styles.py

APP_CSS=r"""
<style>
/* ===== 全站背景：動態漸層 ===== */
.stApp{
  background: radial-gradient(1200px 600px at 10% 10%, rgba(255,0,150,0.20), transparent 60%),
              radial-gradient(1000px 500px at 90% 20%, rgba(0,200,255,0.18), transparent 60%),
              radial-gradient(900px 500px at 30% 90%, rgba(160,255,0,0.12), transparent 60%),
              linear-gradient(120deg, #0b1020 0%, #0b1328 40%, #0a0f1f 100%);
  animation: bgShift 10s ease-in-out infinite alternate;
}
@keyframes bgShift{
  from{ filter: hue-rotate(0deg); }
  to  { filter: hue-rotate(18deg); }
}

/* ===== 內容容器稍微更緊湊 ===== */
.block-container{padding-top:1.1rem;}

/* ===== Sidebar 固定窄寬 + 好看一點 ===== */
section[data-testid="stSidebar"]{width:260px !important;}
section[data-testid="stSidebar"]>div{width:260px !important;}
section[data-testid="stSidebar"] .stMarkdown{color:#e9ecff;}
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
  border-right: 1px solid rgba(255,255,255,0.10);
  backdrop-filter: blur(12px);
}
button[kind="headerNoPadding"]{display:none !important;}

/* ===== 標題霓虹效果 ===== */
.rag-title{
  font-size: 28px;
  font-weight: 800;
  letter-spacing: .5px;
  background: linear-gradient(90deg, #7cf7ff, #ff5fd7, #b6ff6a);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 0 0 18px rgba(255,95,215,0.20);
  animation: neonPulse 2.2s ease-in-out infinite;
  margin-bottom: 4px;
}
@keyframes neonPulse{
  0%,100%{ filter: drop-shadow(0 0 10px rgba(124,247,255,.15)); }
  50%    { filter: drop-shadow(0 0 18px rgba(255,95,215,.18)); }
}

/* ===== 卡片/區塊玻璃霧面 ===== */
.glass{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 16px;
  padding: 14px 14px;
  backdrop-filter: blur(10px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.25);
}

/* ===== 按鈕 hover 更酷 ===== */
.stButton>button{
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.16) !important;
  transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
}
.stButton>button:hover{
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.25);
  border-color: rgba(255,255,255,0.28) !important;
}

/* expander 也做一點霧面感 */
div[data-testid="stExpander"]{
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 14px;
}

/* 小字提示更柔和 */
small, .stCaption{ color: rgba(233,236,255,0.70) !important; }
</style>
"""
