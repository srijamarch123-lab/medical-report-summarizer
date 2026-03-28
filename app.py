import streamlit as st
from pdf_parser import extract_text_from_pdf, get_pdf_metadata
from summarizer import summarize_report, ask_followup

# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="Medical Report Summarizer",
    page_icon="🏥",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .risk-high { background-color: #ffcccc; padding: 10px; border-radius: 8px; border-left: 4px solid red; }
    .risk-none { background-color: #ccffcc; padding: 10px; border-radius: 8px; border-left: 4px solid green; }
    .section-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0; }
    .disclaimer { font-size: 0.8em; color: gray; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────
if "report_text" not in st.session_state:
    st.session_state.report_text = ""
if "summary" not in st.session_state:
    st.session_state.summary = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Header ────────────────────────────────────────────────
st.title("🏥 Medical Report Summarizer")
st.caption("Upload your medical report PDF and get an AI-powered plain-English summary")

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    patient_context = st.text_area(
        "Optional: Add context",
        placeholder="e.g. 'I'm a 25-year-old male with no prior conditions'",
        height=100
    )
    st.divider()
    st.markdown("**How to use:**")
    st.markdown("1. Upload your medical PDF\n2. Click Summarize\n3. Ask follow-up questions")
    st.divider()
    st.warning("⚠️ This tool is for informational purposes only. Always consult a doctor.")

# ── File Upload ───────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload Medical Report (PDF)",
    type=["pdf"],
    help="Supports blood reports, radiology reports, discharge summaries, etc."
)

if uploaded_file:
    meta = get_pdf_metadata(uploaded_file)
    col1, col2 = st.columns(2)
    col1.metric("📄 File Name", uploaded_file.name)
    col2.metric("📑 Pages", meta["pages"])
    
    uploaded_file.seek(0)
    
    if st.button("🔍 Summarize Report", type="primary", use_container_width=True):
        with st.spinner("Reading PDF..."):
            text = extract_text_from_pdf(uploaded_file)
            st.session_state.report_text = text
        
        if not text or text.startswith("Error"):
            st.error("Could not extract text from this PDF. It may be scanned/image-based.")
        else:
            with st.spinner("Analyzing with AI... this may take a few seconds"):
                result = summarize_report(text, patient_context)
                st.session_state.summary = result
                st.session_state.chat_history = []

# ── Display Summary ───────────────────────────────────────
if st.session_state.summary:
    result = st.session_state.summary
    
    if not result["success"]:
        st.error(f"AI Error: {result['error']}")
    else:
        s = result["sections"]
        st.success("✅ Report analyzed successfully!")
        st.divider()
        
        # Plain Summary
        st.subheader("📋 Plain English Summary")
        st.info(s["plain_summary"])
        
        # Two columns for findings
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔎 Key Findings")
            st.markdown(f'<div class="section-box">{s["key_findings"]}</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader("📊 Abnormal Values")
            st.markdown(f'<div class="section-box">{s["abnormal_values"]}</div>', unsafe_allow_html=True)
        
        # Risk Flags (color coded)
        st.subheader("🚨 Risk Flags")
        has_risk = s["risk_flags"].lower() not in ["none", "none detected", ""]
        if has_risk:
            st.markdown(f'<div class="risk-high">{s["risk_flags"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="risk-none">✅ No immediate risk flags detected</div>', unsafe_allow_html=True)
        
        # Next Steps
        st.subheader("🗓️ Recommended Next Steps")
        st.markdown(s["next_steps"])
        
        # Disclaimer
        st.divider()
        st.markdown(f'<p class="disclaimer">{s["disclaimer"]}</p>', unsafe_allow_html=True)
        
        # Download summary
        st.download_button(
            "⬇️ Download Summary as Text",
            data=result["raw"],
            file_name="medical_summary.txt",
            mime="text/plain"
        )
        
        # ── Follow-up Chat ─────────────────────────────────
        st.divider()
        st.subheader("💬 Ask Follow-up Questions")
        
        # Show chat history
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat["q"])
            with st.chat_message("assistant"):
                st.write(chat["a"])
        
        # Chat input
        user_q = st.chat_input("Ask something about your report...")
        if user_q:
            with st.chat_message("user"):
                st.write(user_q)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = ask_followup(
                        st.session_state.report_text,
                        user_q,
                        st.session_state.chat_history
                    )
                st.write(answer)
            st.session_state.chat_history.append({"q": user_q, "a": answer})