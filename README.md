
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
```

## 執行(本機)
```text
cd D:\Sandy\RAG_Llama
.\.venv\Scripts\python.exe -m streamlit run app.py
```


## 執行(Docker)
每次要開始用 Docker（RAG_Llama）怎麼做
1) 打開 PowerShell，進到 compose 資料夾
```text
cd D:\Sandy\RAG_Llama\deploy\docker
```
2) 啟動（背景執行）
```text
docker compose up -d
```
3) 確認有跑起來
```text
docker compose ps
```
(看到狀態是 Up 就 OK)

4) 開你的系統

通常 Streamlit 是：

http://localhost:8501

要停止（不用了）

同一個資料夾下：
```text
docker compose down
```


