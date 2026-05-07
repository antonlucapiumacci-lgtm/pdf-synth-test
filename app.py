import streamlit as st
import PyPDF2
import google.generativeai as genai
import os
import io

# Configurazione Pagina
st.set_page_config(page_title="AI Studio Manager", page_icon="📚", layout="centered")

st.title("📚 Dashboard PDF – Ingegneria Gestionale")
st.markdown("Genera sintesi e test usando **Google Gemini**.")

# Caricamento file
uploaded_files = st.file_uploader("📂 Carica i tuoi PDF", type=["pdf"], accept_multiple_files=True)

# Opzioni interfaccia
mode = st.radio("Scegli l'operazione:", ["Sintesi", "Genera Test"])
num_q = st.slider("Numero domande:", 5, 30, 10) if mode == "Genera Test" else None

def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text

if st.button("🚀 Avvia Elaborazione", use_container_width=True):
    if not uploaded_files:
        st.warning("Carica almeno un file PDF.")
        st.stop()

    # Recupero chiave dai Secrets
    api_key = os.getenv("GOOGLEAPIKEY")
    if not api_key:
        st.error("Chiave API non trovata! Controlla i Secrets di Streamlit.")
        st.stop()

    # Configurazione Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    all_text = ""
    for f in uploaded_files:
        all_text += extract_text(f) + "\n"

    if not all_text.strip():
        st.error("Impossibile estrarre testo dai file caricati.")
        st.stop()

    # Prompt personalizzato per il tuo percorso di studi
    if mode == "Sintesi":
        prompt = f"Sei un tutor di Ingegneria Gestionale. Analizza il seguente testo e fanne una sintesi strutturata per punti, focalizzandoti su definizioni, modelli e formule:\n\n{all_text[:30000]}"
    else:
        prompt = f"Genera un test di {num_q} domande (aperte e chiuse) basato sul seguente testo universitario per preparare un esame:\n\n{all_text[:30000]}"

    try:
        with st.spinner("⏳ Analisi in corso..."):
            response = model.generate_content(prompt)
            output = response.text

        st.subheader("📝 Risultato")
        st.write(output)

        # Bottone di download
        st.download_button("💾 Scarica Risultato", output, file_name="studio_ai.txt")

    except Exception as e:
        st.error(f"Errore durante l'elaborazione: {e}")
