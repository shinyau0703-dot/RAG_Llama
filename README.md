
## 專案架構
```text
RAG_Llama/
├─ __pycache__/
├─ .venv/
├─ components/
│  ├─ __pycache__/
│  ├─ settings_dialog.py
│  └─ sidebar.py
├─ KnowledgeBase/
│  ├─ policies/
│  └─ uploads/
├─ pages_ui/
│  ├─ __pycache__/
│  ├─ __init__.py
│  ├─ ask_page.py
│  └─ db_page.py
├─ deploy/docker/
│  ├─ .dockerignore
│  ├─ docker-compose.yaml
│  └─ Dockerfile
├─ uploads/
├─ .env
├─ .gitignore
├─ app.py
├─ config.py
├─ rag.py
├─ README.md
├─ requirements.txt
├─ styles.py
└─ upload_pdf.py

## 執行
cd D:\Sandy\RAG_Llama
.\.venv\Scripts\python.exe -m streamlit run app.py