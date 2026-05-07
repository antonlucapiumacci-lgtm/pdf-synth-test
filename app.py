import streamlit as st
import PyPDF2
import google.generativeai as genai
import os
import io

# Configurazione Pagina
st.set_page_config(page_title="AI Tutor Gestionale", page_icon="🎓", layout="centered")

st.title("📚 Dashboard PDF – Ingegneria Gestionale")
st.markdown("Sintesi e Test d'esame con Google Gemini")

# Upload
uploaded_files = st.file_uploader("📂 Trascina qui i tuoi PDF", type=["pdf"], accept_multiple_files=True)

# Selezione
mode = st.radio("Cosa vuoi generare?", ["Sintesi", "Test di autovalutazione"])
num_q = st.slider("Numero domande:", 5, 20, 10) if mode == "Test di autovalutazione" else None

def extract_text(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except:
        return ""

if st.button("🚀 Elabora Documenti", use_container_width=True):
    if not uploaded_files:
        st.warning("Per favore, carica almeno un file PDF.")
        st.stop()

    # Recupero Chiave
    api_key = os.getenv("GOOGLEAPIKEY")
    if not api_key:
        st.error("Errore: Chiave API non configurata nei Secrets di Streamlit.")
        st.stop()

    # Configurazione API
    genai.configure(api_key=api_key)
    
    # Usiamo il nome del modello senza prefissi v1/v1beta
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    all_text = ""
    for f in uploaded_files:
        all_text += extract_text(f) + "\n"

    if len(all_text.strip()) < 50:
        st.error("Testo insufficiente o PDF non leggibile.")
        st.stop()

    # Prompt
    if mode == "Sintesi":
        prompt = f"Sei un assistente accademico. Riassumi i concetti chiave (definizioni, modelli, formule) di questo testo in modo schematico:\n\n{all_text[:30000]}"
    else:
        prompt = f"Crea un test di {num_q} domande basato su questo testo, includendo le soluzioni alla fine:\n\n{all_text[:30000]}"

    try:
        with st.spinner("⏳ Gemini sta studiando per te..."):
            response = model.generate_content(prompt)
            # Verifica se la risposta è valida
            if response.text:
                st.subheader("📝 Risultato")
                st.write(response.text)
                st.download_button("💾 Scarica .txt", response.text, file_name="studio_session.txt")
            else:
                st.error("Gemini non ha restituito testo. Prova con un file più breve.")
    except Exception as e:
        st.error(f"Errore tecnico: {str(e)}")
