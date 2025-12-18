import os
import hashlib
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

load_dotenv()

POLICIES_DIR=Path(r"D:\Sandy\RAG-ollama\policies")
CONTENT_COL="file_content"  # 若你的欄位叫 pdf_content 就改這行

def sha256_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def main():
    if not POLICIES_DIR.exists():
        raise FileNotFoundError(f"Folder not found: {POLICIES_DIR}")

    conn=psycopg2.connect(
        host=os.getenv("PGHOST","localhost"),
        port=int(os.getenv("PGPORT","5432")),
        dbname=os.getenv("PGDATABASE","RAG_Llama"),
        user=os.getenv("PGUSER","postgres"),
        password=os.getenv("PGPASSWORD"),
    )
    cur=conn.cursor()

    sql=f'''
    INSERT INTO public."SIM_policies"(filename,sha256,{CONTENT_COL})
    VALUES (%s,%s,%s)
    ON CONFLICT (sha256) DO NOTHING
    '''

    rows=[]
    for p in POLICIES_DIR.rglob("*"):
        if p.is_file():
            b=p.read_bytes()
            rows.append((p.name,sha256_bytes(b),psycopg2.Binary(b)))

    print("Found",len(rows),"files")

    execute_batch(cur,sql,rows,page_size=50)
    conn.commit()

    cur.execute('SELECT COUNT(*) FROM public."SIM_policies";')
    print("Total rows in SIM_policies:",cur.fetchone()[0])

    cur.close()
    conn.close()

if __name__=="__main__":
    main()
