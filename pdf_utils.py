import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter


def extract_text_from_pdf(file):
    """
    Extract raw text from a PDF file uploaded via Streamlit or from path.
    """
    if hasattr(file, 'read'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
    else:
        doc = fitz.open(file)

    text = ""
    for page in doc:
        text += page.get_text()
    return text


def chunk_text(text, chunk_size=1000, chunk_overlap=200):
    """
    Split the text into semantically meaningful chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)
