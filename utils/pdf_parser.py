import PyPDF2

def read_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        pdf = PyPDF2.PdfReader(f)
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def read_pdf_from_streamlit(uploaded_file):
    text = ""
    pdf = PyPDF2.PdfReader(uploaded_file)
    for page in pdf.pages:
        text += page.extract_text() + "\n"
    return text
