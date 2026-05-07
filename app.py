import streamlit as st
import PyPDF2
from google import genai
import os
import io

# Configurazione Pagina
st.set_page_config(page_title="PDF AI Manager", page_icon="📚", layout="centered")

st.title("📚 Dashboard PDF – Ingegneria Gestionale")
st.markdown("Genera sintesi e test d'esame usando **Gemini 3 Flash**.")

# --- CORREZIONE QUI: file_uploader con underscore ---
uploaded_files = st.file_uploader("📂 Carica i tuoi PDF", type=["pdf"], accept_multiple_files=True)

# Opzioni
mode = st.radio("Cosa vuoi fare?", ["Sintesi", "Genera Test"])
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
        st.warning("Carica almeno un file.")
        st.stop()

    all_text = ""
    for f in uploaded_files:
        all_text += extract_text(f) + "\n"

    if not all_text.strip():
        st.error("Testo non trovato nel PDF.")
        st.stop()

    # Inizializzazione Client
    api_key = os.getenv("GOOGLEAPIKEY")
    if not api_key:
        st.error("Chiave API non trovata nei Secrets di Streamlit!")
        st.stop()
        
    client = genai.Client(api_key=api_key)

    # Prompt ottimizzato per Ingegneria Gestionale
    if mode == "Sintesi":
        prompt = f"Sei un esperto di Ingegneria Gestionale. Crea una sintesi tecnica, strutturata con titoli e punti elenco, evidenziando modelli e formule del seguente testo:\n\n{all_text[:30000]}"
    else:
        prompt = f"Genera un test di {num_q} domande (mix tra crocette e domande aperte) per preparare un esame universitario basandoti su questo testo:\n\n{all_text[:30000]}"

    try:
        with st.spinner("⏳ Gemini sta analizzando i documenti..."):
            response = client.models.generate_content(
                model="gemini-3-flash", 
                contents=prompt
            )
            output = response.text

        st.subheader("📝 Risultato")
        st.write(output)

        # Download
        st.download_button("💾 Scarica .txt", output, file_name="risultato_studio.txt")

    except Exception as e:
        st.error(f"Errore durante l'invio a Gemini: {e}")
