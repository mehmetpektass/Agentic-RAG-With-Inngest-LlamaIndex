import streamlit as st
from pathlib import Path
import sys
import time
from datetime import datetime

# Backend modüllerini import et
sys.path.append('.')
from data_loader import load_and_chunk_pdf, embed_text, embed_query_text
from vector_db import QdrantStorage
import uuid
import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Page config
st.set_page_config(
    page_title="Enterprise AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN VE MINIMALIST CSS (Claude/OpenAI Tarzı) ---
st.markdown("""
    <style>
    /* 1. GENEL AYARLAR: Font ve Arka Plan */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* 2. CHAT MESAJLARI: Claude/GPT Tarzı */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 20px 0 !important;
        margin: 0 !important;
        border-bottom: 1px solid rgba(128, 128, 128, 0.1) !important;
    }

    /* Kullanıcı Mesajı */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: transparent; 
    }

    /* Asistan Mesajı (Hafif Arka Plan Farkı) */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: rgba(128, 128, 128, 0.04); 
    }

    /* Mesaj ikonları */
    .stChatMessage .stAvatar {
        background-color: #ECECF1;
        border: 1px solid #E5E5E5;
    }

    /* 3. INPUT ALANI: Temiz ve Geniş */
    .stChatInput {
        border-radius: 12px !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* 4. SIDEBAR: Daha Kurumsal */
    section[data-testid="stSidebar"] {
        background-color: #f9f9fa; /* Light Mode Sidebar */
        border-right: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    /* Dark Mode Uyumluluğu için Sidebar */
    @media (prefers-color-scheme: dark) {
        section[data-testid="stSidebar"] {
            background-color: #1e1e1e;
        }
    }

    /* 5. UPLOAD ALANI */
    .upload-box {
        border: 2px dashed rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }

    /* 6. BUTONLAR: Minimalist */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* 7. BAŞLIKLAR */
    h1, h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }
    
    /* Gereksiz üst boşlukları sil */
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False
if "total_chunks" not in st.session_state:
    st.session_state.total_chunks = 0
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

# Sidebar
with st.sidebar:
    st.markdown("### 🗂️ Document Manager")
    
    # Upload section with custom styling class
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Select PDF Document",
        type="pdf",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file:
        st.success(f"Selected: **{uploaded_file.name}**")
        
        col1, col2 = st.columns(2)
        with col1:
            process_btn = st.button("Analyze", use_container_width=True, type="primary")
        with col2:
            if st.session_state.pdf_processed:
                if st.button("Clear", use_container_width=True):
                    st.session_state.messages = []
                    st.session_state.pdf_processed = False
                    st.session_state.total_chunks = 0
                    st.session_state.pdf_name = ""
                    st.rerun()
        
        if process_btn:
            with st.spinner("Processing document..."):
                progress_bar = st.progress(0)
                
                # --- DÜZELTME BURADA BAŞLIYOR ---
                # 1. ADIM: TEMİZLİK (Eski verileri sil)
                try:
                    # QdrantStorage'ı başlat ve koleksiyonu sıfırla
                    # Not: "docs" senin vector_db.py dosyasındaki varsayılan koleksiyon ismin olmalı.
                    store = QdrantStorage()
                    store.client.delete_collection("docs")
                    # Silindikten sonra upsert işlemi koleksiyonu otomatik yeniden oluşturacaktır.
                except Exception as e:
                    # Koleksiyon zaten yoksa veya silinemezse devam et
                    pass
                # --- DÜZELTME BURADA BİTİYOR ---

                # Save file
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                progress_bar.progress(20)
                time.sleep(0.3)
                
                # Chunk
                chunks = load_and_chunk_pdf(temp_path)
                progress_bar.progress(40)
                
                # Embed (Değişken ismi korundu)
                vecs = embed_text(chunks) 
                progress_bar.progress(60)
                
                # Store
                ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{temp_path}: {i}")) for i in range(len(chunks))]
                payloads = [{"source": temp_path, "text": chunks[i]} for i in range(len(chunks))]
                
                # Upsert (Veri tabanına yazma)
                # Not: Eğer upsert hata verirse, delete_collection sonrası create_collection gerekebilir.
                # Genelde QdrantStorage içinde bu kontrol vardır. Eğer yoksa aşağıda yazacağım.
                QdrantStorage().upsert(ids, vecs, payloads)
                
                # Complete
                progress_bar.progress(100)
                time.sleep(0.5)
                
                st.session_state.pdf_processed = True
                st.session_state.total_chunks = len(chunks)
                st.session_state.pdf_name = uploaded_file.name
                st.toast("Document ready for chat!", icon="✨")
                st.rerun()

    # Stats (Minimalist)
    if st.session_state.pdf_processed:
        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.metric("Chunks", st.session_state.total_chunks)
        c2.metric("Chat", len([m for m in st.session_state.messages if m["role"] == "user"]))
        
    st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color: gray; font-size: 12px; margin-top: 20px;'>
    Powered by <b>Llama 3</b> & <b>Qdrant</b>
    </div>
    """, unsafe_allow_html=True)

# Main Chat Area
if not st.session_state.pdf_processed:
    # Boş Durum (Welcome Screen) - Minimalist Merkez
    st.markdown("""
    <div style='text-align: center; margin-top: 100px;'>
        <h1 style='font-size: 3rem;'>How can I help you today?</h1>
        <p style='color: gray; font-size: 1.1rem; margin-top: 10px;'>
            Upload a PDF document to start analyzing, summarizing, and asking questions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Örnek kartlar
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div style='border: 1px solid rgba(128,128,128,0.2); border-radius: 10px; padding: 20px; height: 150px;'>
            <b>📄 Summarize Content</b><br><br>
            <span style='color: gray; font-size: 14px;'>Get a quick overview of long documents instantly.</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style='border: 1px solid rgba(128,128,128,0.2); border-radius: 10px; padding: 20px; height: 150px;'>
            <b>🔍 Extract Details</b><br><br>
            <span style='color: gray; font-size: 14px;'>Find specific figures, dates, and names within seconds.</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div style='border: 1px solid rgba(128,128,128,0.2); border-radius: 10px; padding: 20px; height: 150px;'>
            <b>💡 Semantic Search</b><br><br>
            <span style='color: gray; font-size: 14px;'>Ask questions in natural language, not just keywords.</span>
        </div>
        """, unsafe_allow_html=True)

else:
    # Dolu Durum (Chat Interface)
    st.markdown(f"### Chatting with: {st.session_state.pdf_name}")
    
    # Mesajları Göster
    for msg in st.session_state.messages:
        # Avatar: Kullanıcı için boş, AI için ikon (OpenAI tarzı)
        avatar = None if msg["role"] == "user" else "🤖"
        
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])
            
            # Metadata (Varsa, minimalist şekilde göster)
            if msg["role"] == "assistant" and "metadata" in msg and msg["metadata"]["sources"]:
                with st.expander("View Sources", expanded=False):
                    for src in msg["metadata"]["sources"]:
                        st.caption(f"📄 Source: {Path(src).name}")

    # Input Alanı
    if question := st.chat_input("Message PDF AI..."):
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        
        # Cevap Üret
        with st.chat_message("assistant", avatar="🤖"):
            # Boş bir alan yaratıp akışkan yazı efekti verebiliriz (isteğe bağlı) veya spinner
            with st.spinner("Thinking..."):
                start_time = time.time()
                
                # Search (Değişken ismi korundu)
                query_vec = embed_query_text([question])[0]
                store = QdrantStorage()
                found = store.search(query_vec, 5)
                
                if not found["context"]:
                    answer = "I couldn't find relevant information in this document."
                    sources = []
                else:
                    context_block = "\n\n".join(f"- {c}" for c in found["context"])
                    
                    response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
                        json={
                            "model": "llama-3.3-70b-versatile",
                            "messages": [
                                {"role": "system", "content": "You are a professional AI assistant. Answer based on the context provided."},
                                {"role": "user", "content": f"Context:\n{context_block}\n\nQuestion: {question}"}
                            ],
                            "max_tokens": 1024,
                            "temperature": 0.1 
                        }
                    )
                    answer = response.json()["choices"][0]["message"]["content"]
                    sources = found["sources"]
                
                # Cevabı yaz
                st.write(answer)
                
                # Geçmişe kaydet
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "metadata": {
                        "sources": sources
                    }
                })