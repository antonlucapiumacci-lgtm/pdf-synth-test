import streamlit as st
import PyPDF2
from google import genai
from google.genai import types
import os
import io

# Configurazione Pagina
st.set_page_config(page_title="PDF AI Manager", page_icon="📚", layout="centered")

st.title("📚 Dashboard PDF – Ingegneria Gestionale")
st.markdown("Genera sintesi e test d'esame usando **Gemini 3 Flash**.")

# Upload File
uploaded_files = st.fileuploader("📂 Carica i tuoi PDF", type=["pdf"], accept_multiple_files=True)

# Opzioni
mode = st.radio("Cosa vuoi fare?", ["Sintesi", "Genera Test"])
num_q = st.slider("Numero domande:", 5, 30, 10) if mode == "Genera Test" else None

def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])

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

    # Nuova inizializzazione Client Google Gen AI
    client = genai.Client(api_key=os.getenv("GOOGLEAPIKEY"))

    prompt = (f"Crea una sintesi strutturata per punti di questo testo universitario:\n{all_text[:20000]}" 
              if mode == "Sintesi" else 
              f"Genera un test di {num_q} domande con risposte basato su:\n{all_text[:20000]}")

    try:
        with st.spinner("⏳ Gemini sta elaborando..."):
            # Utilizziamo Gemini 3 Flash (molto più veloce per testi lunghi)
            response = client.models.generate_content(
                model="gemini-3-flash", 
                contents=prompt
            )
            output = response.text

        st.subheader("📝 Risultato")
        st.write(output)

        # Download
        st.download_button("💾 Scarica .txt", output, file_name="risultato.txt")

    except Exception as e:
        st.error(f"Errore: {e}")
