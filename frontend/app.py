import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.title("AI Chatbot dengan Ollama")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.expander("Admin Login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "123456":
                st.session_state.logged_in = True
                st.success("Login berjaya!")
            else:
                st.error("Login gagal.")

st.subheader("Tanya Soalan kepada AI")

query = st.text_input("Soalan anda")
model = "qwen2:1.5b"

if st.button("Hantar"):
    if not query:
        st.warning("Sila masukkan soalan.")
    else:
        with st.spinner("Sedang menjawab..."):
            try:
                response = requests.get(
                    f"{BACKEND_URL}/ask",
                    params={"q": query, "model": model},
                    timeout=120
                )
                if response.status_code == 200:
                    st.write("**Jawapan:**")
                    st.write(response.json()["answer"])
                else:
                    st.error("Ralat daripada API.")
            except Exception as e:
                st.error(f"Ralat: {e}")

if st.session_state.logged_in:
    st.subheader("Admin Panel")

    # Muat naik PDF
    uploaded_file = st.file_uploader("Muat naik fail PDF", type="pdf")
    if uploaded_file is not None:
        try:
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            response = requests.post(f"{BACKEND_URL}/upload", files=files)
            if response.status_code == 200:
                st.success("Fail berjaya dimuat naik.")
            else:
                st.error("Gagal memuat naik fail.")
        except Exception as e:
            st.error(f"Ralat: {e}")

    # Tambah URL
    st.markdown("---")
    st.write("Tambah URL Sumber")
    new_url = st.text_input("Masukkan URL laman web")
    if st.button("Tambah URL"):
        if new_url:
            try:
                response = requests.post(f"{BACKEND_URL}/add_url", json={"url": new_url})
                if response.status_code == 200:
                    st.success("URL berjaya ditambah.")
                else:
                    st.error("Gagal menambah URL.")
            except Exception as e:
                st.error(f"Ralat: {e}")
        else:
            st.warning("Sila masukkan URL.")

    # Reload index
    if st.button("Reload Index"):
        try:
            requests.post(f"{BACKEND_URL}/reload")
            st.success("Index berjaya dimuat semula.")
        except Exception as e:
            st.error(f"Ralat: {e}")

    # Papar log
    st.markdown("---")
    st.subheader("Log Soalan")
    try:
        logs = requests.get(f"{BACKEND_URL}/logs")
        if logs.status_code == 200:
            st.text(logs.text)
        else:
            st.warning("Gagal mendapatkan log.")
    except Exception as e:
        st.error(f"Ralat: {e}")
