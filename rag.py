# rag.py
import os
import re
import uuid
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

import chromadb
from pypdf import PdfReader
import ollama


@dataclass
class Hit:
    text:str
    meta:Dict
    distance:float


def _sha256_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def _normalize_text(s:str)->str:
    s=(s or "").replace("\r\n","\n").replace("\r","\n")
    s=re.sub(r"[ \t]+"," ",s)
    s=re.sub(r"\n{3,}","\n\n",s)
    return s.strip()


def _extract_pdf_pages(pdf_path:str)->List[Tuple[int,str]]:
    reader=PdfReader(pdf_path)
    out=[]
    for i,page in enumerate(reader.pages,start=1):
        t=page.extract_text() or ""
        t=_normalize_text(t)
        if t:
            out.append((i,t))
    return out


def _smart_chunk(text:str,chunk_size:int=800,overlap:int=120)->List[str]:
    text=_normalize_text(text)
    if not text:
        return []

    seps=["\n\n","\n",". ","。","！","？"," "]
    chunks=[]

    def split_rec(s:str,sep_idx:int)->None:
        if len(s)<=chunk_size:
            chunks.append(s.strip())
            return
        if sep_idx>=len(seps):
            chunks.append(s[:chunk_size].strip())
            rest=s[chunk_size:]
            if rest.strip():
                split_rec(rest,sep_idx)
            return

        sep=seps[sep_idx]
        parts=s.split(sep)
        buf=""
        for p in parts:
            candidate=(buf+(sep if buf else "")+p).strip()
            if len(candidate)<=chunk_size:
                buf=candidate
            else:
                if buf:
                    split_rec(buf,sep_idx+1)
                buf=p.strip()
        if buf:
            split_rec(buf,sep_idx+1)

    split_rec(text,0)
    chunks=[c for c in chunks if c]

    if overlap>0 and len(chunks)>1:
        out=[]
        prev=""
        for c in chunks:
            if prev:
                tail=prev[-overlap:]
                out.append((tail+"\n"+c).strip())
            else:
                out.append(c)
            prev=c
        return out
    return chunks


def _embed(text:str,embed_model:str)->List[float]:
    r=ollama.embeddings(model=embed_model,prompt=text)
    return r["embedding"]


def get_client(db_dir:str)->chromadb.PersistentClient:
    os.makedirs(db_dir,exist_ok=True)
    return chromadb.PersistentClient(path=db_dir)


def get_collection(client:chromadb.PersistentClient,name:str):
    return client.get_or_create_collection(name=name)


def clear_all(collection)->None:
    try:
        ids=collection.get(include=[])["ids"]
        if ids:
            collection.delete(ids=ids)
    except Exception:
        pass


def get_db_status(collection)->Dict:
    try:
        meta=collection.get(include=["metadatas"])
        metas=meta.get("metadatas",[]) or []
        sources=set()
        for m in metas:
            if isinstance(m,dict):
                sources.add(m.get("source","unknown"))
        return {"unique_sources":len(sources),"total_chunks":len(metas)}
    except Exception:
        return {"unique_sources":0,"total_chunks":0}


def _delete_by_source(collection,source:str)->None:
    try:
        collection.delete(where={"source":source})
    except Exception:
        # 有些版本 where delete 可能不支援
        pass


def ingest_pdf_path(
    pdf_path:str,
    collection,
    embed_model:str,
    chunk_size:int,
    overlap:int,
    root_dir:str,
)->Tuple[int,int,Optional[str]]:
    """
    return: (scanned_pages, added_chunks, note_if_failed)
    """
    try:
        # 來源用相對路徑：uploads/xxx.pdf
        source=os.path.relpath(pdf_path,root_dir).replace("\\","/")
        _delete_by_source(collection,source)

        b=open(pdf_path,"rb").read()
        file_hash=_sha256_bytes(b)

        pages=_extract_pdf_pages(pdf_path)
        if not pages:
            return (0,0,f"{source}：抽不到文字（可能是掃描檔，需要 OCR）")

        docs=[]
        metas=[]
        ids=[]
        embs=[]

        chunk_count=0
        for page_no,page_text in pages:
            chunks=_smart_chunk(page_text,chunk_size=chunk_size,overlap=overlap)
            for idx,c in enumerate(chunks,start=1):
                c=c.strip()
                if not c:
                    continue
                chunk_count+=1
                # 用 file_hash+page+idx 做穩定 ID：同檔重匯不會一直累積
                stable_id=f"{file_hash}:{page_no}:{idx}"
                ids.append(stable_id)
                docs.append(c)
                metas.append({"source":source,"page":page_no,"chunk":idx,"file_hash":file_hash})
                embs.append(_embed(c,embed_model))

        if not ids:
            return (len(pages),0,f"{source}：沒有可用內容（chunk 後為空）")

        # 先刪再加（避免 Chroma 對同 ID add 的行為不一致）
        try:
            collection.delete(ids=ids)
        except Exception:
            pass

        collection.add(ids=ids,documents=docs,metadatas=metas,embeddings=embs)
        return (len(pages),len(ids),None)

    except Exception as e:
        return (0,0,f"{os.path.basename(pdf_path)}：匯入失敗 -> {e}")


def ingest_uploaded_pdfs(
    uploaded_files,
    upload_dir:str,
    collection,
    embed_model:str,
    chunk_size:int,
    overlap:int,
)->Tuple[int,int,int,List[str]]:
    """
    專給 Streamlit file_uploader 用
    return: scanned_files, added_chunks, skipped_files, notes
    """
    os.makedirs(upload_dir,exist_ok=True)
    scanned=0
    added=0
    skipped=0
    notes=[]

    for f in uploaded_files or []:
        try:
            save_path=os.path.join(upload_dir,f.name)
            with open(save_path,"wb") as out:
                out.write(f.getbuffer())

            scanned+=1
            pages_cnt,added_cnt,note=ingest_pdf_path(
                pdf_path=save_path,
                collection=collection,
                embed_model=embed_model,
                chunk_size=chunk_size,
                overlap=overlap,
                root_dir=upload_dir,
            )
            added+=added_cnt
            if note:
                skipped+=1
                notes.append(note)

        except Exception as e:
            skipped+=1
            notes.append(f"{getattr(f,'name','(unknown)')}：匯入失敗 -> {e}")

    return scanned,added,skipped,notes


def retrieve(question:str,collection,embed_model:str,top_k:int=6)->List[Hit]:
    q=(question or "").strip()
    if not q:
        return []

    q_emb=_embed(q,embed_model)
    res=collection.query(
        query_embeddings=[q_emb],
        n_results=top_k,
        include=["documents","metadatas","distances"],
    )

    docs=res.get("documents",[[]])[0] or []
    metas=res.get("metadatas",[[]])[0] or []
    dists=res.get("distances",[[]])[0] or []

    out=[]
    for d,m,dist in zip(docs,metas,dists):
        out.append(Hit(text=d,meta=m or {},distance=float(dist)))
    return out


def build_prompt(question:str,hits:List[Hit])->Tuple[str,str]:
    ctx_lines=[]
    src_lines=[]
    for i,h in enumerate(hits,start=1):
        src=h.meta.get("source","unknown")
        page=h.meta.get("page",None)
        src_label=f"{src}（第{page}頁）" if page else src
        src_lines.append(f"[{i}] {src_label}")
        ctx_lines.append(f"[{i}] {h.text}")

    sources="\n".join(src_lines) if src_lines else "(no sources)"
    context="\n\n".join(ctx_lines) if ctx_lines else "(no context found)"

    system=(
        "You are a reliable assistant. Answer using ONLY the provided context. "
        "If the context is insufficient, say you don't have enough information. "
        "Cite sources like [1], [2]."
    )
    user=(
        f"Sources:\n{sources}\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer in Traditional Chinese. Keep it concise and actionable."
    )
    return system,user


def chat_llm(system_prompt:str,user_prompt:str,model:str,temperature:float=0.2)->str:
    messages=[
        {"role":"system","content":system_prompt},
        {"role":"user","content":user_prompt},
    ]
    r=ollama.chat(model=model,messages=messages,options={"temperature":temperature})
    return (r.get("message",{}) or {}).get("content","") or ""
