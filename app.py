import streamlit as st
import PyPDF2
from openai import OpenAI
import io

st.set_page_config(page_title="PDF Synth & Test Generator", page_icon="📚", layout="centered")

st.title("📚 Dashboard PDF – Sintesi e Generazione di Test")

st.markdown("""
Carica uno o più file PDF e scegli se generare:
- una **sintesi strutturata** del contenuto;
- un **test automatico** (domande aperte o a scelta multipla).
""")

uploaded_files = st.file_uploader(
    "📂 Carica i tuoi file PDF",
    type=["pdf"],
    accept_multiple_files=True
)

mode = st.radio("Scegli l’operazione:", ["Sintesi", "Genera Test"])

num_questions = None
if mode == "Genera Test":
    num_questions = st.slider("Numero di domande da generare:", 5, 30, 10)

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

if st.button("🚀 Esegui", use_container_width=True):
    if not uploaded_files:
        st.warning("Carica almeno un file PDF.")
        st.stop()

    all_text = ""
    for f in uploaded_files:
        pdf_text = extract_text_from_pdf(f)
        all_text += pdf_text + "\n"

    if not all_text.strip():
        st.error("Non è stato possibile estrarre testo dai PDF caricati.")
        st.stop()

    if mode == "Sintesi":
        user_prompt = f"""Crea una sintesi accademica chiara, strutturata e completa del seguente testo:
        {all_text[:15000]}"""
    else:
        user_prompt = f"""Genera un test di {num_questions} domande basato sul seguente testo.
        Alterna domande a scelta multipla e aperte, includendo le risposte corrette.
        Testo di riferimento:
        {all_text[:15000]}"""

    try:
        client = OpenAI()
        with st.spinner("⏳ Elaborazione in corso..."):
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": user_prompt}],
            )

        output = response.choices[0].message.content
        st.subheader(f"📝 Risultato: {mode}")
        st.write(output)

        buffer = io.BytesIO()
        buffer.write(output.encode('utf-8'))
        buffer.seek(0)
        st.download_button(
            label="💾 Scarica risultato (.txt)",
            data=buffer,
            file_name=f"output_{mode.lower().replace(' ', '_')}.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"Errore durante l'elaborazione: {e}")
