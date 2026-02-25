import streamlit as st # type: ignore
import os
import time
import pandas as pd # type: ignore
from engine import LookupEngine # type: ignore
from utils import format_bytes, get_file_info

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="QuantumLink | Quantum-Neon Core",
    page_icon="💠",
    layout="wide",
)

# --- CSS: QUANTUM-NEON PREMIUM DESIGN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;800&display=swap');

    /* ===== GLOBAL RESET & BACKGROUND ===== */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background: #0B0F19 !important;
        color: #F8FAF8 !important;
        line-height: 1.6;
    }

    /* Nebula Glow Effect */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at 0% 0%, rgba(0, 255, 136, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 100% 100%, rgba(255, 0, 127, 0.08) 0%, transparent 40%);
        pointer-events: none;
        z-index: 0;
        animation: nebula-drift 10s infinite alternate ease-in-out;
    }
    @keyframes nebula-drift {
        from { transform: scale(1); }
        to { transform: scale(1.1); }
    }

    .block-container {
        padding: 3rem 4rem !important;
        max-width: 1400px !important;
        z-index: 1;
    }

    /* ===== GLASSMORPHIC CONTAINERS ===== */
    .glass-card {
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px;
        padding: 2.2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        border-color: rgba(255, 255, 255, 0.15) !important;
    }
    .glass-card.master { border-top: 2px solid #00FF88 !important; }
    .glass-card.reference { border-top: 2px solid #FF007F !important; }

    /* ===== TITLES & TYPOGRAPHY ===== */
    h1, h2, h3, h4, .section-title {
        font-family: 'JetBrains Mono', monospace !important;
    }
    .master-header { color: #00FF88 !important; font-weight: 800; }
    .ref-header { color: #FF007F !important; font-weight: 800; }
    .secondary-text { color: #FFFFFF !important; font-weight: 800; font-size: 0.95rem; }

    /* ===== STEP NAVIGATION ===== */
    .step-widget {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 25px;
        margin-bottom: 4rem;
    }
    .step-badge {
        width: 60px; height: 60px;
        background: linear-gradient(135deg, #00FF88 0%, #FF007F 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 900;
        color: #0B0F19;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
    }

    /* ===== FILE UPLOADER CUSTOMIZATION ===== */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        background: rgba(11, 15, 25, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    /* Glow Pink on hover */
    [data-testid="stFileUploader"]:hover {
        border-color: #FF007F !important;
        box-shadow: 0 0 20px rgba(255, 0, 127, 0.2) !important;
    }
    /* Browse File Button - Black on White for High Contrast */
    [data-testid="stFileUploader"] button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 8px !important;
    }

    /* Widget Labels (Anchor Key, Registry Key, Attributes) */
    [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.5px;
    }

    /* Native File Uploader Internal Text Visibility */
    [data-testid="stFileUploaderFileName"], 
    [data-testid="stFileUploaderSize"],
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        font-weight: 900 !important;
        opacity: 1 !important;
    }

    /* ===== STATUS PILLS ===== */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: rgba(0, 255, 136, 0.05);
        border: 1px solid #00FF88;
        padding: 10px 20px;
        border-radius: 100px;
        font-size: 0.95rem;
        font-weight: 900 !important;
        color: #FFFFFF !important;
    }
    .status-pill span {
        color: #FFFFFF !important;
        font-weight: 900 !important;
    }
    .status-pill.pink {
        background: rgba(255, 0, 127, 0.05);
        border: 1px solid #FF007F;
        color: #FFFFFF !important;
    }
    .status-pill .meta {
        font-weight: 900 !important;
        color: #FFFFFF !important;
        opacity: 1;
        border-left: 1px solid rgba(255,255,255,0.3);
        padding-left: 10px;
    }

    /* ===== BUTTONS: GREEN TO PINK GRADIENT ===== */
    .stButton > button {
        background: linear-gradient(135deg, #00FF88 0%, #FF007F 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        padding: 0.75rem 2.5rem !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.4) !important;
        color: #fff !important;
    }

    /* ===== COLUMN TAGS ===== */
    .col-tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.05);
        color: #94A3B8;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
    }

    /* Expander - Pink Header Theme */
    [data-testid="stExpander"] {
        background: transparent !important;
        border: none !important;
        margin-bottom: 1rem !important;
    }
    [data-testid="stExpander"] summary {
        background: #FF007F !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        padding: 12px 20px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        list-style: none !important;
    }
    [data-testid="stExpander"] summary:hover {
        background: #334155 !important; /* Slate Grey Hover */
        color: #FFFFFF !important;
    }
    /* Hide the default triangle */
    [data-testid="stExpander"] summary::-webkit-details-marker { display: none !important; }
    
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: rgba(255, 0, 127, 0.03) !important;
        padding: 2rem !important;
        border-radius: 0 0 12px 12px !important;
        border: 1px solid rgba(255, 0, 127, 0.1) !important;
        border-top: none !important;
    }

    /* Compilation Status & Download Button - Pink to Grey */
    [data-testid="stStatusWidget"] {
        background: #FF007F !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
    }
    [data-testid="stStatusWidget"] * {
        color: white !important;
        font-weight: 800 !important;
    }

    [data-testid="stDownloadButton"] button {
        background: #FF007F !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 800 !important;
        padding: 1rem 2rem !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: #334155 !important;
        box-shadow: 0 0 20px rgba(0,0,0,0.4) !important;
    }

    /* Hide default streamlit and sidebar */
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'engine' not in st.session_state:
    st.session_state.engine = LookupEngine()

if 'main_data' not in st.session_state:
    st.session_state.main_data = {"path": "", "cols": []}
if 'ref_list' not in st.session_state:
    st.session_state.ref_list = []

def save_file(uploaded_file):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    path = os.path.join("uploads", uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

# ─────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; padding: 5rem 1rem 4rem;">
    <h1 style="font-size: 5.5rem; font-weight: 900; background: linear-gradient(135deg, #00FF88 0%, #FF007F 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -4px; margin-bottom: 0;">QUANTUMLINK</h1>
    <p style="color: #94A3B8; font-size: 1.3rem; letter-spacing: 6px; text-transform: uppercase; font-weight: 600;">Quantum-Neon Mission Control</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# STEP 1 — INGEST DATASETS
# ─────────────────────────────────────────────
st.markdown("""
<div class="step-widget">
    <div class="step-badge">01</div>
    <div class="step-info">
        <h3>INGEST DATASETS</h3>
        <p class="secondary-text">Deploy source anchors and link external registries</p>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("""
    <h4 class="master-header">🟢 MASTER DATASET</h4>
    <p class="secondary-text">Primary anchor for relational multi-chain enrichment.</p>
    """, unsafe_allow_html=True)
    
    u_main = st.file_uploader("Ingest Master File", type=["csv", "xlsx", "parquet"], key="umain", label_visibility="collapsed")
    
    if u_main:
        m_path = save_file(u_main)
        if st.session_state.main_data["path"] != m_path:
            st.session_state.main_data["cols"] = st.session_state.engine.get_columns(m_path)
            st.session_state.main_data["path"] = m_path
        
        cols = st.session_state.main_data["cols"]
        if cols:
            with st.expander("🔍 VIEW DETECTED SCHEMA", expanded=False):
                cols_html = "".join([f'<span class="col-tag">{c}</span>' for c in cols])
                st.markdown(f'<div style="max-height: 250px; overflow-y: auto;">{cols_html}</div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
    <h4 class="ref-header">🛡️ REFERENCE POOL</h4>
    <p class="secondary-text">Linked registries serving as high-speed lookup sources.</p>
    """, unsafe_allow_html=True)
    
    u_refs = st.file_uploader("Ingest Reference Files", type=["csv", "xlsx", "parquet"], accept_multiple_files=True, key="urefs", label_visibility="collapsed")
    
    if u_refs:
        temp_list = []
        total_size = 0
        for ur in u_refs:
            r_path = save_file(ur)
            total_size += os.path.getsize(r_path)
            r_cols = st.session_state.engine.get_columns(r_path)
            temp_list.append({"path": r_path, "name": ur.name, "cols": r_cols})
        st.session_state.ref_list = temp_list
        
        if st.session_state.ref_list:
            with st.expander("📚 VIEW REGISTRY ATTRIBUTES", expanded=False):
                all_pool_cols = []
                for r in st.session_state.ref_list:
                    all_pool_cols.extend(r['cols'])
                unique_pool_cols = sorted(list(set(all_pool_cols)))
                cols_html = "".join([f'<span class="col-tag">{c}</span>' for c in unique_pool_cols])
                st.markdown(f'<div style="max-height: 250px; overflow-y: auto;">{cols_html}</div>', unsafe_allow_html=True)

st.write("")
st.write("")

if st.session_state.main_data["cols"] and st.session_state.ref_list:
    # ─────────────────────────────────────────────
    # STEP 2 — JOIN CONFIG
    # ─────────────────────────────────────────────
    st.markdown("""
    <div class="step-widget">
        <div class="step-badge">02</div>
        <div class="step-info">
            <h3>CONFIGURE LOGIC</h3>
            <p class="secondary-text">Establish relational tunnels and selective schema extraction</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    chain_data = []
    for i, ref in enumerate(st.session_state.ref_list):
        with st.expander(f"🔮 NODE INTERSECTION {i+1}: Linking with {ref['name']}", expanded=(i == 0)):
            c1, c2 = st.columns([3, 2], gap="large")
            with c1:
                st.markdown('<p class="master-header" style="font-size: 0.75rem; text-transform: uppercase;">Relational Mapping</p>', unsafe_allow_html=True)
                sub1, sub2 = st.columns(2)
                with sub1:
                    m_key = st.selectbox("Anchor Key", st.session_state.main_data["cols"], key=f"mkey_{i}")
                with sub2:
                    r_key = st.selectbox("Registry Key", ref['cols'], key=f"rkey_{i}")
            with c2:
                st.markdown('<p class="ref-header" style="font-size: 0.75rem; text-transform: uppercase;">Schema Pull</p>', unsafe_allow_html=True)
                pull = st.multiselect("Attributes", ref['cols'], key=f"pull_{i}")
            chain_data.append({'path': ref['path'], 'match_pairs': [(m_key, r_key)], 'pull_cols': pull})

    st.write("")

    # ─────────────────────────────────────────────
    # STEP 3 — EXECUTION
    # ─────────────────────────────────────────────
    st.markdown("""
    <div class="step-widget">
        <div class="step-badge">03</div>
        <div class="step-info">
            <h3>INITIALIZE SYSTEM</h3>
            <p class="secondary-text">Compile relational logic and export high-dimensional dataset</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Step 3 Unified Centered Layout
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<p class="master-header" style="font-size: 1rem; margin-bottom: 1.5rem; text-transform: uppercase; text-align: center;">Compilation Settings</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            out_name = st.text_input("Object Path", value="enriched_data.csv")
        with c2:
            out_fmt = st.radio("Encoding Protocol", ["csv", "parquet"], horizontal=True)
        
        st.write("")
        if st.button("👁️ PREVIEW COMPILED OBJECT", use_container_width=True):
            with st.spinner("Processing preview..."):
                prev = st.session_state.engine.get_multi_preview(st.session_state.main_data["path"], chain_data)
                if prev is not None: st.dataframe(prev, use_container_width=True)
        
        st.write("")
        if st.button("⚡ INITIALIZE GLOBAL COMPILE", use_container_width=True):
            if not os.path.exists("results"): os.makedirs("results")
            final_path = os.path.join("results", out_name)
            with st.status("Quantum Sync Initiated...", expanded=True) as status:
                start = time.time()
                success, msg = st.session_state.engine.execute_multi_join(st.session_state.main_data["path"], chain_data, final_path, out_fmt)
                elapsed = time.time() - start
                if success:
                    status.update(label=f"Compilation Finished! ({elapsed:.2f}s)", state="complete")
                    st.balloons()
                    with open(final_path, "rb") as f:
                        st.download_button(label="📥 DOWNLOAD RESULTS", data=f, file_name=out_name, mime="text/csv" if out_fmt == "csv" else "application/octet-stream", use_container_width=True)
                else:
                    status.update(label="System Overflow", state="error")
                    st.error(msg)
