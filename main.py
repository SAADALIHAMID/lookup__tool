import streamlit as st # type: ignore
import os
import time
import pandas as pd # type: ignore
from engine import LookupEngine # type: ignore
from utils import format_bytes, get_file_info

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="QuantumLink Multi-Chain | Data Enrichment Pro",
    page_icon="🔗",
    layout="wide",
)

# --- CSS: PREMIUM DESIGN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
        background-color: #0c0f16;
        color: #e2e8f0;
    }

    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }

    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .st-emotion-cache-12w0qpk, .st-emotion-cache-6qob1r {
        background: rgba(17, 25, 40, 0.75) !important;
        backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.125) !important;
        border-radius: 24px !important;
        padding: 2rem !important;
    }

    .stButton > button {
        border-radius: 12px !important;
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.75rem !important;
        transition: all 0.3s ease !important;
    }

    .col-tag {
        display: inline-block;
        background: rgba(79, 172, 254, 0.1);
        color: #4facfe;
        border: 1px solid rgba(79, 172, 254, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'engine' not in st.session_state:
    st.session_state.engine = LookupEngine()

# Initialize data states
if 'main_data' not in st.session_state:
    st.session_state.main_data = {"path": "", "cols": []}
if 'ref_list' not in st.session_state:
    st.session_state.ref_list = [] # List of dicts: {'path':, 'cols':, 'name':}

def save_file(uploaded_file):
    if not os.path.exists("uploads"): os.makedirs("uploads")
    path = os.path.join("uploads", uploaded_file.name)
    with open(path, "wb") as f: f.write(uploaded_file.getbuffer())
    return path

# --- HEADER ---
st.markdown('<h1 class="main-title">QUANTUM LINK PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Multi-File Chain Joining & Enrichment System</p>', unsafe_allow_html=True)

# --- STEP 1: MULTI-UPLOAD ---
st.markdown("### 📥 Step 1: Ingest All Datasets")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("#### 🟢 Main Dataset (The Base)")
    u_main = st.file_uploader("Upload Master File", type=["csv", "xlsx", "parquet"], key="umain")
    if u_main:
        m_path = save_file(u_main)
        if st.session_state.main_data["path"] != m_path:
            st.session_state.main_data["cols"] = st.session_state.engine.get_columns(m_path)
            st.session_state.main_data["path"] = m_path
        
        st.success(f"Loaded: {u_main.name}")
        with st.expander("View Master Columns"):
            cols_html = "".join([f'<span class="col-tag">{c}</span>' for c in st.session_state.main_data["cols"]])
            st.markdown(cols_html, unsafe_allow_html=True)

with col2:
    st.markdown("#### 🔵 Reference Files (Lookup Pool)")
    u_refs = st.file_uploader("Upload Multiple Lookup Files", type=["csv", "xlsx", "parquet"], accept_multiple_files=True, key="urefs")
    
    if u_refs:
        # Clear list and re-populate to stay in sync with uploader
        temp_list = []
        for ur in u_refs:
            r_path = save_file(ur)
            r_cols = st.session_state.engine.get_columns(r_path)
            temp_list.append({"path": r_path, "name": ur.name, "cols": r_cols})
        st.session_state.ref_list = temp_list
        
        st.info(f"Loaded {len(u_refs)} reference files for joining.")

st.divider()

# --- STEP 2: CHAIN CONFIGURATION ---
if st.session_state.main_data["cols"] and st.session_state.ref_list:
    st.markdown("### 🧬 Step 2: Configure Chain Join Logic")
    
    chain_data = [] # Combined data for engine
    
    for i, ref in enumerate(st.session_state.ref_list):
        with st.expander(f"🔗 JOINING: Master ↔ {ref['name']}", expanded=(i == 0)):
            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.markdown("**Relational Mapping (The Link)**")
                sub1, sub2 = st.columns(2)
                with sub1:
                    m_key = st.selectbox(f"Key in Master", st.session_state.main_data["cols"], key=f"mkey_{i}")
                with sub2:
                    r_key = st.selectbox(f"Key in {ref['name']}", ref['cols'], key=f"rkey_{i}")
            
            with c2:
                st.markdown("**Extraction**")
                pull = st.multiselect(f"Columns to pull from {ref['name']}", ref['cols'], key=f"pull_{i}")
            
            chain_data.append({
                'path': ref['path'],
                'match_pairs': [(m_key, r_key)],
                'pull_cols': pull
            })

    st.divider()

    # --- STEP 3: OUTPUT & DOWNLOAD ---
    st.markdown("### 🚀 Step 3: Multi-Chain Execution")
    ec1, ec2 = st.columns([1, 1])
    
    with ec1:
        out_name = st.text_input("Final Filename", value="enriched_data.csv")
        out_fmt = st.radio("Format", ["csv", "parquet"], horizontal=True)
        
        if st.button("👁️ PREVIEW ENRICHED DATA"):
            with st.spinner("Processing Chain Join..."):
                prev = st.session_state.engine.get_multi_preview(st.session_state.main_data["path"], chain_data)
                if prev is not None:
                    st.dataframe(prev, use_container_width=True)

    with ec2:
        st.write("") # Spacer
        st.write("")
        if st.button("⚡ EXECUTE GLOBAL MERGE"):
            if not os.path.exists("results"): os.makedirs("results")
            final_path = os.path.join("results", out_name)
            
            with st.status("Chaining Joins in DuckDB Engine...", expanded=True) as status:
                start = time.time()
                success, msg = st.session_state.engine.execute_multi_join(
                    st.session_state.main_data["path"],
                    chain_data,
                    final_path,
                    out_fmt
                )
                end = time.time()
                
                if success:
                    status.update(label="Global Merge Complete!", state="complete")
                    st.balloons()
                    with open(final_path, "rb") as f:
                        st.download_button(
                            label="📥 DOWNLOAD MERGED CSV",
                            data=f,
                            file_name=out_name,
                            mime="text/csv" if out_fmt == "csv" else "application/octet-stream"
                        )
                else:
                    status.update(label="Chain Join Failed", state="error")
                    st.error(msg)
else:
    st.info("👋 **Waiting for Ingestion...** Please upload 1 Master file and at least 1 Reference file to start chaining.")
