import torch
from transformers import pipeline as hf_pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

def get_rag_chain(chunks):
    embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Make sure `chunks` are plain strings, not Document objects
    texts = [doc.page_content if hasattr(doc, "page_content") else doc for doc in chunks]
    db = FAISS.from_texts(texts, embedding=embed)
    retriever = db.as_retriever(search_kwargs={"k": 4})

    pipe = hf_pipeline("text2text-generation", model="google/flan-t5-base", device=0 if torch.cuda.is_available() else -1)

    llm = HuggingFacePipeline(pipeline=pipe)

    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    return rag_chain
