import streamlit as st
import requests

# Konfigurasi login
USERNAME = "admin"
PASSWORD = "123456"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("🔒 Login AI Chatbot")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
        else:
            st.error("Username atau password salah.")

if not st.session_state.authenticated:
    login()
    st.stop()

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("🤖 AI Chatbot dengan PDF & Website")
st.write("Taip soalan di bawah:")

query = st.text_input("Soalan:")

if query:
    with st.spinner("Sedang menjawab..."):
        try:
            response = requests.get("http://backend:8000/ask", params={"q": query}, timeout=30)
            st.success(response.json().get("response", "Tiada jawapan."))
        except Exception as e:
            st.error(f"Ralat: {e}")

# Butang reload index
if st.button("Reload Index"):
    requests.post("http://backend:8000/reload")
    st.success("Index sedang dimuat semula.")

# Log paparan pertanyaan
with st.expander("📜 Log Pertanyaan"):
    try:
        logs = requests.get("http://backend:8000/logs").text
        st.text(logs)
    except:
        st.info("Log belum tersedia.")
