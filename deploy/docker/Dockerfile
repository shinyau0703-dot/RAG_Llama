FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 系統套件（pypdf 常用不到額外依賴；這裡只裝最基本）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# 先裝 requirements（利用 Docker layer cache）
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 再複製程式碼
COPY . /app

EXPOSE 8501

# Streamlit 常用設定：對外監聽、關閉 CORS（內網/自用通常 OK）
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
