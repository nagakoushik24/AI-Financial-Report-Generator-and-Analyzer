import os
os.environ["TRANSFORMERS_NO_TF"] = "1"

import streamlit as st
from pdf_utils import extract_text_from_pdf, chunk_text
from vector_store import build_faiss_index
from summarizer import summarize_text
from rag_pipeline import get_rag_chain
from kpi_extractor import extract_kpis
from sec_utils import fetch_sec_filing_by_year, download_pdf
from pdf_download import generate_pdf
import requests

# --------------------- Page Setup --------------------- #
st.set_page_config(page_title="AI Financial Report Generator", layout="centered", initial_sidebar_state="expanded")
if "pdf_url" not in st.session_state:
    st.session_state["pdf_url"] = None

st.title("📊 AI Financial Report Generator")

# --------------------- Sidebar --------------------- #
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2331/2331966.png", width=80)
    st.markdown("## 🧠 About This App")
    st.markdown("""
Welcome to the **AI Financial Report Generator**, an AI-powered platform that:
- Fetches SEC 10-K reports 🧾
- Summarizes financial data 📈
- Extracts KPIs 📊
- Answers your queries 🤖

Built using **LangChain**, **HuggingFace Transformers**, **FAISS**, and **Streamlit**.
    """)
    st.markdown("---")

# --------------------- Company Selection --------------------- #
cik_map = {
    "Apple Inc. (AAPL)": {"ticker": "AAPL", "cik": "0000320193"},
    "Microsoft Corp. (MSFT)": {"ticker": "MSFT", "cik": "0000789019"},
    "Amazon.com Inc. (AMZN)": {"ticker": "AMZN", "cik": "0001018724"},
    "Alphabet Inc. (GOOGL)": {"ticker": "GOOGL", "cik": "0001652044"},
    "Meta Platforms (META)": {"ticker": "META", "cik": "0001326801"},
    "Tesla Inc. (TSLA)": {"ticker": "TSLA", "cik": "0001318605"}
}

company_input = st.selectbox("🏢 Select Company", list(cik_map.keys()))
year = st.selectbox("📅 Select Filing Year", list(range(2024, 2014, -1)))

ticker = cik_map[company_input]["ticker"]
cik = cik_map[company_input]["cik"]

# --------------------- Process Filing Once --------------------- #
if "processed" not in st.session_state:
    st.session_state["processed"] = False

if st.button("🔍 Fetch and Analyze 10-K Filing"):
    with st.spinner("📥 Downloading and analyzing SEC filing..."):
        filing = fetch_sec_filing_by_year(cik, "10-K", year)

        if "filingURL" in filing:
            pdf_url = filing["filingURL"]
            local_pdf_path = download_pdf(pdf_url)

            if local_pdf_path:
                text = extract_text_from_pdf(local_pdf_path)
                chunks = chunk_text(text)
                index, chunk_data = build_faiss_index(chunks)
                summary = summarize_text(" ".join(chunks[:3]))[:500] + "..."
                kpis = extract_kpis(text)
                rag_chain = get_rag_chain(chunk_data)

                # Save to session state
                st.session_state["summary"] = summary
                st.session_state["kpis"] = kpis
                st.session_state["rag_chain"] = rag_chain
                st.session_state["source_chunks"] = chunk_data
                st.session_state["ticker"] = ticker
                st.session_state["year"] = year
                st.session_state["processed"] = True

                st.success("✅ Filing successfully processed!")
            else:
                st.error("❌ Failed to download or read the SEC filing PDF.")
        else:
            st.error(filing.get("message", "❌ No filing found for this year."))

# --------------------- Display Results --------------------- #

if st.session_state["pdf_url"]:
    pdf_url = st.session_state["pdf_url"]
    st.markdown("### 🔗 Original SEC Filing")
    st.markdown(f"[📄 View on SEC Website]({pdf_url})", unsafe_allow_html=True)
    st.markdown("---")



if st.session_state["processed"]:
    st.markdown("### 📋 Financial Summary")
    st.markdown(f"**Brief Overview:**\n\n{st.session_state['summary']}")
    st.markdown("---")

    st.markdown("### 📌 Key Financial Metrics")
    st.table(st.session_state["kpis"])
    st.markdown("---")

    # Ask a question
    question = st.text_input("💬 Ask a financial question (e.g. What are the risks?)")
    answer = ""
    source_docs = []

    if question:
        with st.spinner("💡 Finding the answer..."):
            result = st.session_state["rag_chain"]({"query": question})
            answer = result["result"]
            source_docs = result.get("source_documents", [])

        st.markdown("### 💬 Answer to Your Question")
        st.markdown(f"**{answer.strip()}**")

        st.markdown("### 📚 Sources from the Report")
        for i, doc in enumerate(source_docs):
            st.markdown(f"""
**Source {i + 1}:**
> {doc.page_content.strip()}
---""")


if "pdf_url" in locals():
    sec_response = requests.get(pdf_url, headers={"User-Agent": "Naga Koushik <nagakoushik24@gmail.com>"})
    if sec_response.status_code == 200:
        st.download_button(
            label="📥 Download Original SEC 10-K Filing",
            data=sec_response.content,
            file_name=f"{st.session_state['ticker']}_{st.session_state['year']}_SEC_10K.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("⚠️ Could not fetch the original SEC PDF.")

# AI-Generated PDF Summary
pdf_path = generate_pdf(
    st.session_state["summary"],
    st.session_state["kpis"],
    question,
    answer,
    source_docs
)
with open(pdf_path, "rb") as f:
    st.download_button(
        label="📥 Download AI-Generated Summary Report",
        data=f,
        file_name=f"{st.session_state['ticker']}_{st.session_state['year']}_financial_summary.pdf",
        mime="application/pdf"
    )
