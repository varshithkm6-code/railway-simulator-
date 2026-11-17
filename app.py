"""
================================================================================
  RailCOA — Indian Rail Ticketing Server Memory Hierarchy Simulator
================================================================================
  Course: Computer Organization and Architecture (UE25CS2302)
  Institution: GM University | Department of Computer Science & Engineering
  Faculty: Dr. Neelambike S | Total Marks: 40
  
  High-Fidelity Architectural Simulator & Executive Dashboard:
  - Multi-Level Cache (L1/L2, AMAT, Write-Through/Back, LRU/FIFO/Random)
  - Virtual Memory (Page Table, TLB, EMAT, Page Faults)
  - IEEE 754 32-bit Single Precision vs Exact Financial Decimal Fare Engine
  - I/O Interfacing & DMA Controller (Burst vs Cycle Stealing, PIO, Interrupts)
  - Parallel Multi-Core Booking Engine (Amdahl's Law & Bus Contention)
  - Interactive 32-Bit Address Decoder
  - CircuitVerse Schematics, CPUlator Assembly & Viva Voce Preparation
================================================================================
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Import backend simulation engines
from modules.simulator import (
    run_full_rail_simulation,
    decode_address_hardware,
    HOT_TRAINS
)
from modules.hardware_demo import (
    CPULATOR_ARM_CODE,
    CPULATOR_RISCV_CODE,
    CIRCUITVERSE_GUIDE,
    TINKERCAD_SPECS,
    VIVA_VOCE_PREP,
    ACADEMIC_REPORT_DATA
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="RailCOA — Memory Hierarchy Simulator",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# MODERN HIGH-TECH UI / UX STYLING (DARK NEON GLASSMORPHIC THEME)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* Main Background and Typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Background Gradients */
.stApp {
    background: radial-gradient(circle at 15% 15%, #131b2e 0%, #0b0f19 50%, #080c14 100%);
    color: #e2e8f0;
}

/* Glassmorphic Container Cards */
.glass-card {
    background: rgba(17, 24, 39, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 22px;
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    margin-bottom: 20px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.glass-card:hover {
    border-color: rgba(99, 102, 241, 0.35);
}

/* Glowing Stat Cards */
.stat-card {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 14px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00f2fe, #4facfe, #6c5ce7);
}

.stat-label {
    font-size: 0.82rem;
    font-weight: 500;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.stat-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.stat-badge {
    display: inline-flex;
    align-items: center;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 9999px;
    margin-top: 8px;
}
.badge-cyan { background: rgba(0, 242, 254, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 254, 0.3); }
.badge-green { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
.badge-amber { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }

/* Header Banner */
.hero-banner {
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 18px;
    padding: 26px 30px;
    margin-bottom: 24px;
    position: relative;
    box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.5);
}
.hero-title {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
}
.hero-sub {
    font-size: 0.95rem;
    color: #94a3b8;
    margin-bottom: 12px;
}
.tag-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 600;
    background: rgba(99, 102, 241, 0.18);
    color: #a5b4fc;
    border: 1px solid rgba(99, 102, 241, 0.3);
    margin-right: 8px;
}

/* Bitfield Visualizer */
.bit-box {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 2px;
    text-align: center;
}
.bit-sign { background: rgba(59, 130, 246, 0.25); color: #60a5fa; border: 1px solid #3b82f6; }
.bit-exp { background: rgba(168, 85, 247, 0.25); color: #c084fc; border: 1px solid #a855f7; }
.bit-mantissa { background: rgba(16, 185, 129, 0.25); color: #34d399; border: 1px solid #10b981; }

/* Custom Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0b0f17 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

/* Tabs Styling */
button[data-baseweb="tab"] {
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
button[aria-selected="true"] {
    background-color: rgba(99, 102, 241, 0.2) !important;
    color: #818cf8 !important;
}

/* Hide streamlit deploy/menu clutter */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# MATPLOTLIB DARK THEME HELPER
# -----------------------------------------------------------------------------
def setup_dark_plot():
    """Sets up a modern, high-contrast dark palette for Matplotlib charts."""
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8, 3.6), facecolor="#0e1422")
    ax.set_facecolor("#0e1422")
    ax.grid(True, linestyle="--", alpha=0.18, color="#94a3b8")
    for spine in ax.spines.values():
        spine.set_color("#334155")
        spine.set_linewidth(0.8)
    ax.tick_params(colors="#cbd5e1", labelsize=9)
    ax.xaxis.label.set_color("#cbd5e1")
    ax.yaxis.label.set_color("#cbd5e1")
    ax.title.set_color("#f8fafc")
    ax.title.set_fontsize(11)
    ax.title.set_fontweight("bold")
    return fig, ax


# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS & PRESET CONFIGURATIONS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <span style="font-size: 1.8rem;">🚆</span>
        <div>
            <div style="font-weight: 800; font-size: 1.2rem; color: #f8fafc; letter-spacing: -0.02em;">RailCOA Engine</div>
            <div style="font-size: 0.75rem; color: #818cf8; font-weight: 600;">COA PBL • UE25CS2302</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎛️ Simulation Presets")
    preset = st.selectbox(
        "Load Configuration Profile",
        [
            "Custom Configuration",
            "⚡ 10:00 AM Tatkal Rush (Heavy Hotspots)",
            "🌤️ Normal Booking Hours (Distributed)",
            "⚠️ Extreme Cache Thrashing Stress Test",
            "🚀 High-End Enterprise Server (64KB L1, DMA)",
            "💻 Budget Classroom Node (2KB L1, PIO)"
        ]
    )
    
    # Preset default parameters
    def_req = 3000
    def_workload = "Peak booking"
    def_loc = 85
    def_l1_kb = 8
    def_blk = 64
    def_assoc = "4-way"
    def_repl = "LRU"
    def_write = "Write-Back"
    def_pg_kb = 4
    def_frames = 32
    def_pg_pol = "LRU"
    def_io_mb = 16
    def_cores = 8
    
    if "Tatkal" in preset:
        def_req = 4000
        def_workload = "Peak booking"
        def_loc = 90
        def_l1_kb = 8
        def_blk = 64
        def_assoc = "4-way"
        def_cores = 8
    elif "Normal" in preset:
        def_req = 2500
        def_workload = "Normal booking"
        def_loc = 65
        def_l1_kb = 8
        def_assoc = "4-way"
        def_cores = 4
    elif "Thrashing" in preset:
        def_req = 5000
        def_workload = "Uniform/random"
        def_loc = 20
        def_l1_kb = 2
        def_blk = 16
        def_assoc = "Direct mapped"
        def_repl = "Random"
        def_cores = 12
    elif "High-End" in preset:
        def_req = 6000
        def_l1_kb = 64
        def_blk = 128
        def_assoc = "8-way"
        def_frames = 64
        def_cores = 16
        def_io_mb = 32
    elif "Budget" in preset:
        def_req = 1500
        def_l1_kb = 2
        def_blk = 32
        def_assoc = "Direct mapped"
        def_frames = 8
        def_cores = 2
        def_io_mb = 4

    st.markdown("---")
    st.markdown("### 🚂 Workload & Traffic")
    requests_input = st.slider("Booking Requests ($N$)", 200, 10000, def_req, 100)
    workload_input = st.selectbox(
        "Workload Profile",
        ["Peak booking", "Normal booking", "Uniform/random"],
        index=["Peak booking", "Normal booking", "Uniform/random"].index(def_workload)
    )
    locality_input = st.slider("Temporal Locality (%)", 10, 95, def_loc)

    st.markdown("### 🧠 Cache Subsystem")
    l1_kb_input = st.selectbox("L1 Cache Size (KB)", [1, 2, 4, 8, 16, 32, 64], index=[1, 2, 4, 8, 16, 32, 64].index(def_l1_kb))
    block_size_input = st.selectbox("Block Size (Bytes)", [16, 32, 64, 128], index=[16, 32, 64, 128].index(def_blk))
    assoc_input = st.selectbox("Associativity", ["Direct mapped", "2-way", "4-way", "8-way", "Fully associative"], index=["Direct mapped", "2-way", "4-way", "8-way", "Fully associative"].index(def_assoc))
    replacement_input = st.selectbox("Cache Replacement Policy", ["LRU", "FIFO", "Random"], index=["LRU", "FIFO", "Random"].index(def_repl))
    write_policy_input = st.selectbox("Write Policy", ["Write-Back", "Write-Through"], index=["Write-Back", "Write-Through"].index(def_write))

    st.markdown("### 🗂️ Virtual Memory & Paging")
    page_size_input = st.selectbox("Page Size (KB)", [1, 2, 4, 8, 16], index=[1, 2, 4, 8, 16].index(def_pg_kb))
    frames_input = st.slider("Physical Page Frames (RAM)", 4, 128, def_frames)
    page_policy_input = st.selectbox("Page Replacement", ["LRU", "FIFO"], index=["LRU", "FIFO"].index(def_pg_pol))

    st.markdown("### 💾 Storage I/O & Multiprocessing")
    io_mb_input = st.selectbox("Reservation Chart Transfer (MB)", [1, 4, 8, 16, 32, 64], index=[1, 4, 8, 16, 32, 64].index(def_io_mb))
    cores_input = st.slider("CPU Processing Cores", 1, 16, def_cores)

    st.markdown("---")
    run_button = st.button("🚀 Re-Run Simulation", type="primary", use_container_width=True)


# Construct Config Dictionary
cfg = {
    "requests": requests_input,
    "workload": workload_input,
    "locality": locality_input / 100.0,
    "cache_kb": l1_kb_input,
    "block_size": block_size_input,
    "associativity": assoc_input,
    "replacement": replacement_input,
    "write_policy": write_policy_input,
    "page_size_kb": page_size_input,
    "frames": frames_input,
    "page_policy": page_policy_input,
    "io_mb": io_mb_input,
    "cores": cores_input
}

# Run or Retrieve Simulation Results
if "sim_data" not in st.session_state or run_button:
    with st.spinner("Executing hardware simulation pipeline..."):
        st.session_state.sim_data = run_full_rail_simulation(cfg)

data = st.session_state.sim_data
cache = data["cache"]
paging = data["paging"]
fare = data["fare"]
io_res = data["io"]
parallel = data["parallel"]


# -----------------------------------------------------------------------------
# HERO BANNER & ACADEMIC CONTEXT
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
        <div>
            <div class="hero-title">🚆 RailCOA — Indian Rail Ticketing Server Simulator</div>
            <div class="hero-sub">Simulation and Evaluation of Cache-Memory Hierarchy, Interfacing & Arithmetic for High-Concurrency Reservation Engines</div>
            <div>
                <span class="tag-pill">GM University • FET</span>
                <span class="tag-pill">Course: UE25CS2302 (COA)</span>
                <span class="tag-pill">Faculty: Dr. Neelambike S</span>
                <span class="tag-pill" style="background: rgba(16, 185, 129, 0.18); color: #34d399; border-color: rgba(16, 185, 129, 0.3);">Max Marks: 40</span>
            </div>
        </div>
        <div style="text-align: right; background: rgba(0, 0, 0, 0.25); padding: 12px 18px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Active Workload</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #00f2fe;">{cfg['workload']}</div>
            <div style="font-size: 0.8rem; color: #a5b4fc;">{cfg['requests']:,} Requests | {cfg['locality']*100:.0f}% Locality</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TOP-LEVEL NAVIGATION TABS
# -----------------------------------------------------------------------------
tab_overview, tab_cache, tab_vm, tab_fp, tab_io, tab_parallel, tab_decoder, tab_hardware, tab_report = st.tabs([
    "📊 Overview",
    "🧠 Cache Hierarchy",
    "🗂️ Virtual Memory",
    "💰 IEEE 754 Fare Engine",
    "💾 I/O & DMA",
    "⚡ Parallel Workers",
    "🔍 32-Bit Address Decoder",
    "🔌 Hardware & Assembly",
    "🎓 Academic Report & Viva"
])


# =============================================================================
# TAB 1: EXECUTIVE OVERVIEW & ARCHITECTURE
# =============================================================================
with tab_overview:
    st.subheader("⚡ High-Concurrency Ticketing Subsystem Performance")
    
    # 8 Key Performance Indicators (Modern Stat Cards)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">L1 Cache Hit Ratio</div>
            <div class="stat-value">{cache['l1_hit_ratio']:.2f}%</div>
            <span class="stat-badge badge-green">L1 Hits: {cache['l1_hits']:,}</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Hierarchy AMAT</div>
            <div class="stat-value">{cache['hierarchy_amat']:.2f} <span style="font-size: 1rem; color: #94a3b8;">cyc</span></div>
            <span class="stat-badge badge-cyan">L1: 1 | L2: 8 | RAM: 80</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">TLB Hit Rate</div>
            <div class="stat-value">{paging['tlb_hit_rate']:.2f}%</div>
            <span class="stat-badge badge-purple">Page Faults: {paging['page_faults']}</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">DMA Cycles Saved</div>
            <div class="stat-value">{io_res['cycles_saved_vs_pio'] / 1_000_000:.1f}M</div>
            <span class="stat-badge badge-green">vs Programmed I/O</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">L2 Cache Hit Ratio</div>
            <div class="stat-value">{cache['l2_hit_ratio']:.2f}%</div>
            <span class="stat-badge badge-cyan">{cache['l2_hits']:,} Filtered from RAM</span>
        </div>
        """, unsafe_allow_html=True)
    with c6:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Effective CPI</div>
            <div class="stat-value">{cache['effective_cpi']:.2f}</div>
            <span class="stat-badge badge-amber">Base CPI: 1.0 (Compute)</span>
        </div>
        """, unsafe_allow_html=True)
    with c7:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Multi-Core Speedup</div>
            <div class="stat-value">{parallel['actual_speedup']:.2f}×</div>
            <span class="stat-badge badge-green">{parallel['cores']} Workers Active</span>
        </div>
        """, unsafe_allow_html=True)
    with c8:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">IEEE 754 Drift</div>
            <div class="stat-value">₹{abs(fare['cumulative_drift']):.4f}</div>
            <span class="stat-badge badge-amber">Float32 vs Exact Decimal</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Architectural Memory Hierarchy Diagram
    st.markdown("""
    <div class="glass-card">
        <div style="font-weight: 700; font-size: 1.15rem; color: #f8fafc; margin-bottom: 14px;">
            🏗️ Simulated Memory Hierarchy & Interfacing Pipeline
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; background: rgba(0,0,0,0.3); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="font-size: 1.5rem;">💻</div>
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.9rem;">CPU Cores</div>
                <div style="font-size: 0.72rem; color: #94a3b8;">1 - 16 Workers</div>
            </div>
            <div style="color: #6366f1; font-weight: bold; font-size: 1.2rem;">➔</div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="font-size: 1.5rem;">⚡</div>
                <div style="font-weight: 700; color: #00f2fe; font-size: 0.9rem;">L1 Cache</div>
                <div style="font-size: 0.72rem; color: #94a3b8;">1 Cycle (Split D/I)</div>
            </div>
            <div style="color: #6366f1; font-weight: bold; font-size: 1.2rem;">➔</div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="font-size: 1.5rem;">🧠</div>
                <div style="font-weight: 700; color: #818cf8; font-size: 0.9rem;">L2 Cache</div>
                <div style="font-size: 0.72rem; color: #94a3b8;">8 Cycles (Unified)</div>
            </div>
            <div style="color: #6366f1; font-weight: bold; font-size: 1.2rem;">➔</div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="font-size: 1.5rem;">🏛️</div>
                <div style="font-weight: 700; color: #34d399; font-size: 0.9rem;">Main Memory</div>
                <div style="font-size: 0.72rem; color: #94a3b8;">80 Cycles DRAM</div>
            </div>
            <div style="color: #6366f1; font-weight: bold; font-size: 1.2rem;">➔</div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="font-size: 1.5rem;">🗂️</div>
                <div style="font-weight: 700; color: #fbbf24; font-size: 0.9rem;">TLB & Paging</div>
                <div style="font-size: 0.72rem; color: #94a3b8;">16-Entry Assoc</div>
            </div>
            <div style="color: #6366f1; font-weight: bold; font-size: 1.2rem;">➔</div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="font-size: 1.5rem;">💾</div>
                <div style="font-weight: 700; color: #f43f5e; font-size: 0.9rem;">DMA Storage</div>
                <div style="font-size: 0.72rem; color: #94a3b8;">Burst / Stealing</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Live IRCTC Trace Inspection
    st.markdown("""
    <div style="font-weight: 700; font-size: 1.1rem; color: #f8fafc; margin-top: 15px; margin-bottom: 10px;">
        🔍 Live Synthetic Booking Access Trace (IRCTC High-Traffic Stream)
    </div>
    """, unsafe_allow_html=True)
    
    trace_df = pd.DataFrame([
        {
            "Step": f"#{idx+1}",
            "32-Bit Memory Address": f"0x{item['address']:08X}",
            "Operation": item["op"],
            "Target Subsystem Region": item["region"],
            "Train Number & Name": f"{item['train']['number']} — {item['train']['name']}",
            "Quota Category": item["train"]["quota"]
        }
        for idx, item in enumerate(data["trace_sample"])
    ])
    st.dataframe(trace_df, hide_index=True, use_container_width=True)


# =============================================================================
# TAB 2: MULTI-LEVEL CACHE HIERARCHY
# =============================================================================
with tab_cache:
    st.markdown("""
    <div style="font-weight: 700; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">
        🧠 Multi-Level Cache Hierarchy (L1 & L2) Simulation
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 18px;">
        Evaluation of Set-Associative Mapping, Block Size, Replacement Policies (LRU/FIFO/Random) and Write Strategies.
    </div>
    """, unsafe_allow_html=True)

    col_c1, col_c2 = st.columns([1.2, 1.0])

    with col_c1:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 12px;">
                📐 Cache Geometry & Address Bit Breakdown
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 15px;">
                <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">TAG BITS</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #60a5fa;">{cache['tag_bits']} bits</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">SET INDEX BITS</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #c084fc;">{cache['index_bits']} bits</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">BLOCK OFFSET BITS</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #34d399;">{cache['offset_bits']} bits</div>
                </div>
            </div>
            <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
                • <b>Total Sets:</b> {cache['sets']} sets | <b>Associativity:</b> {cache['ways']}-way ({cfg['associativity']})<br>
                • <b>L1 Cache Capacity:</b> {cache['l1_kb']} KB ({cache['block_size']} bytes/block)<br>
                • <b>L2 Unified Capacity:</b> {cache['l2_kb']} KB (8-way set associative)<br>
                • <b>Write Policy:</b> {cfg['write_policy']} ({cache['l1_dirty_evictions']} dirty evictions written to L2/RAM)
            </div>
        </div>
        """, unsafe_allow_html=True)

        # LaTeX AMAT Formulation
        st.markdown("""
        <div class="glass-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 10px;">
                🧮 Average Memory Access Time (AMAT) Mathematical Derivation
            </div>
            <div style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 8px;">
                Single-Level L1 AMAT:
            </div>
        """, unsafe_allow_html=True)
        st.latex(rf"\text{{AMAT}}_{{L1}} = t_{{L1}} + (\text{{Miss Rate}}_{{L1}} \times t_{{RAM}}) = 1 + ({cache['l1_miss_ratio']/100:.4f} \times 80) = {cache['l1_amat']:.3f} \text{{ cycles}}")
        st.markdown("""
            <div style="font-size: 0.88rem; color: #cbd5e1; margin-top: 12px; margin-bottom: 8px;">
                Two-Level Hierarchy AMAT:
            </div>
        """, unsafe_allow_html=True)
        st.latex(r"\text{AMAT}_{H} = t_{L1} + \text{Miss Rate}_{L1} \times \left[ t_{L2} + (\text{Miss Rate}_{L2} \times t_{RAM}) \right]")
        st.latex(rf"\text{{AMAT}}_{{H}} = 1 + {cache['l1_miss_ratio']/100:.4f} \times \left[ 8 + ({cache['l2_miss_ratio']/100:.4f} \times 80) \right] = \mathbf{{{cache['hierarchy_amat']:.3f} \text{{ cycles}}}}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_c2:
        # Visual Hit/Miss Distribution Chart
        fig, ax = setup_dark_plot()
        categories = ["L1 Hits", "L1 Misses", "L2 Hits", "L2 Misses", "RAM Access"]
        counts = [cache["l1_hits"], cache["l1_misses"], cache["l2_hits"], cache["l2_misses"], cache["main_memory_accesses"]]
        colors = ["#10b981", "#ef4444", "#00f2fe", "#f59e0b", "#a855f7"]
        bars = ax.bar(categories, counts, color=colors, width=0.55, edgecolor="none", zorder=3)
        ax.set_ylabel("Access Count")
        ax.set_title("Memory Access Distribution Across Hierarchy")
        plt.xticks(rotation=25, ha="right")
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:,}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, color="#cbd5e1")
        st.pyplot(fig)
        plt.close(fig)

        st.info(f"💡 **Viva Tip:** Changing replacement from Random to LRU reduces conflict misses during Tatkal spikes by keeping hot seat-map mutexes in the cache.")


# =============================================================================
# TAB 3: VIRTUAL MEMORY, PAGE TABLE & TLB
# =============================================================================
with tab_vm:
    st.markdown("""
    <div style="font-weight: 700; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">
        🗂️ Virtual Memory Paging, TLB & Effective Memory Access Time (EMAT)
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 18px;">
        Simulates 32-bit Virtual Address Translation, 16-entry TLB hits/misses, and Page Faults into physical frames.
    </div>
    """, unsafe_allow_html=True)

    vm_col1, vm_col2 = st.columns([1.1, 1.0])

    with vm_col1:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 12px;">
                🗺️ Virtual Address Split & Paging Geometry
            </div>
            <div style="display: flex; gap: 10px; margin-bottom: 12px;">
                <div style="flex: 1; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">VPN (VIRTUAL PAGE NUMBER)</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #c084fc;">{paging['vpn_bits']} bits</div>
                </div>
                <div style="flex: 1; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">PAGE OFFSET</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #34d399;">{paging['offset_bits']} bits</div>
                </div>
            </div>
            <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
                • <b>Configured Page Size:</b> {paging['page_size_kb']} KB ({2**paging['offset_bits']:,} bytes per page)<br>
                • <b>Physical RAM Frames:</b> {paging['physical_frames']} frames allocated for booking worker process<br>
                • <b>Page Replacement Policy:</b> {cfg['page_policy']} ({paging['replacements']:,} page frames evicted to storage)
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 10px;">
                ⚡ Effective Memory Access Time (EMAT) Derivation
            </div>
        """, unsafe_allow_html=True)
        st.latex(r"\text{EMAT} = p_{tlb} \times (t_{tlb} + t_{ram}) + (1 - p_{tlb}) \times \left[ (1 - p_{fault})(t_{tlb} + 2 t_{ram}) + p_{fault}(t_{tlb} + 2 t_{ram} + t_{fault}) \right]")
        st.markdown(f"""
            <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 8px;">
                • $t_{{tlb}} = 1$ cycle | $t_{{ram}} = 80$ cycles | $t_{{fault}} = 8000$ cycles (Disk I/O penalty)<br>
                • <b>Effective EMAT Result:</b> <span style="color: #34d399; font-weight: 700;">{paging['emat']:.2f} cycles</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with vm_col2:
        # TLB vs Page Fault Rates Bar Chart
        fig, ax = setup_dark_plot()
        bars = ax.bar(["TLB Hits", "TLB Misses", "Page Faults", "Frame Evictions"],
                      [paging["tlb_hits"], paging["tlb_misses"], paging["page_faults"], paging["replacements"]],
                      color=["#10b981", "#f59e0b", "#ef4444", "#a855f7"], width=0.5)
        ax.set_ylabel("Count")
        ax.set_title("TLB Performance & Page Fault Occurrences")
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f'{h:,}', xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
        st.pyplot(fig)
        plt.close(fig)

    st.markdown("""
    <div style="font-weight: 700; font-size: 1.05rem; color: #f8fafc; margin-top: 10px; margin-bottom: 8px;">
        📋 Active Page Table Snapshots (Inverted Resident Frame Table)
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(paging["sample_table"]), hide_index=True, use_container_width=True)


# =============================================================================
# TAB 4: IEEE 754 FLOATING-POINT FEE ENGINE
# =============================================================================
with tab_fp:
    st.markdown("""
    <div style="font-weight: 700; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">
        💰 IEEE 754 Floating-Point vs. Decimal Fee Processing
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 18px;">
        Exposes hardware single-precision (32-bit float) rounding errors, catastrophic cancellation, and financial drift.
    </div>
    """, unsafe_allow_html=True)

    fp_col1, fp_col2 = st.columns([1.1, 1.0])

    with fp_col1:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 12px;">
                🎟️ Indian Railway Ticket Fare Breakdown (Vande Bharat Sample)
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 15px;">
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">BASE FARE</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc;">₹{fare['base_fare']:.2f}</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">TATKAL SURCHARGE (30%)</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc;">₹{fare['tatkal_charge']:.2f}</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">GST (5.0%)</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc;">₹{fare['gst_charge']:.2f}</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">50% CANCELLATION REFUND</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc;">₹{fare['decimal_refund']:.2f}</div>
                </div>
            </div>
            <div style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 10px; display: flex; justify-content: space-between;">
                <div>
                    <span style="color: #94a3b8; font-size: 0.8rem;">Exact Decimal Total:</span>
                    <div style="color: #34d399; font-weight: 700; font-size: 1.3rem;">₹{fare['decimal_total']:.2f}</div>
                </div>
                <div>
                    <span style="color: #94a3b8; font-size: 0.8rem;">Hardware Float32 Total:</span>
                    <div style="color: #f59e0b; font-weight: 700; font-size: 1.3rem;">₹{fare['float_total']:.6f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Bitfield Visualizer Card
        comp = fare["ieee754_total_components"]
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 8px;">
                🔬 Total Fare IEEE 754 32-Bit Representation (Hex: <span style="color: #00f2fe;">{comp['hex']}</span>)
            </div>
            <div style="margin-bottom: 12px;">
                <span class="bit-box bit-sign">Sign [1b]: {comp['sign_bit']}</span>
                <span class="bit-box bit-exp">Exp [8b]: {comp['exponent_bits']} ({comp['unbiased_exp']} biased)</span>
                <span class="bit-box bit-mantissa">Mantissa [23b]: {comp['mantissa_bits'][:12]}...</span>
            </div>
        """, unsafe_allow_html=True)
        st.latex(rf"(-1)^{{\text{{Sign}}}} \times 2^{{E - 127}} \times (1.\text{{Mantissa}}) = (-1)^0 \times 2^{{{comp['unbiased_exp']}}} \times (1.M)")
        st.markdown("</div>", unsafe_allow_html=True)

    with fp_col2:
        # Accumulated Discrepancy Chart over passenger volume
        fig, ax = setup_dark_plot()
        vol = np.linspace(100, 10000, 50)
        single_err = fare["single_ticket_error"]
        drift_vals = vol * single_err
        ax.plot(vol, drift_vals, color="#f43f5e", linewidth=2.2, label="Accumulated Drift (₹)")
        ax.axhline(0, color="#94a3b8", linestyle="--", alpha=0.5)
        ax.set_xlabel("Number of Processed Tickets")
        ax.set_ylabel("Total Financial Drift (₹)")
        ax.set_title("Financial Loss Accumulation: Float32 vs Decimal")
        ax.legend(facecolor="#0e1422", edgecolor="#334155")
        st.pyplot(fig)
        plt.close(fig)

        st.warning(f"""
        ⚠️ **COA PBL Observation:** Single ticket discrepancy is **₹{fare['single_ticket_error']:.8f}**. Over **{fare['passenger_count']:,}** passenger bookings, the cumulative ledger mismatch totals **₹{fare['cumulative_drift']:.4f}**. This is why IRCTC production systems store fares in integer minor units (paise) or use BCD Decimal arithmetic!
        """)


# =============================================================================
# TAB 5: I/O INTERFACING & DMA CONTROLLER
# =============================================================================
with tab_io:
    st.markdown("""
    <div style="font-weight: 700; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">
        💾 Storage I/O Interfacing: Programmed I/O vs. Interrupts vs. DMA
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 18px;">
        Models CPU overhead and bus occupancy when flushing reservation chart logs (16 MB = 4,194,304 words) to secondary storage.
    </div>
    """, unsafe_allow_html=True)

    io_c1, io_c2 = st.columns([1.1, 1.0])

    with io_c1:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 12px;">
                ⚙️ I/O Mode Performance Breakdown ({io_res['io_mb']} MB Transfer)
            </div>
            <table style="width: 100%; font-size: 0.86rem; border-collapse: collapse; color: #cbd5e1;">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08); text-align: left;">
                    <th style="padding: 8px;">I/O Technique</th>
                    <th style="padding: 8px;">CPU Cycles</th>
                    <th style="padding: 8px;">CPU Utilization</th>
                    <th style="padding: 8px;">Mechanism</th>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 8px; color: #f43f5e; font-weight: 600;">Programmed I/O</td>
                    <td style="padding: 8px;">{io_res['pio_cpu_cycles']:,}</td>
                    <td style="padding: 8px;">100.0%</td>
                    <td style="padding: 8px;">Busy-wait status polling per word</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 8px; color: #f59e0b; font-weight: 600;">Interrupt-Driven</td>
                    <td style="padding: 8px;">{io_res['interrupt_cpu_cycles']:,}</td>
                    <td style="padding: 8px;">{io_res['interrupt_cpu_utilization']:.1f}%</td>
                    <td style="padding: 8px;">ISR context switch per block</td>
                </tr>
                <tr>
                    <td style="padding: 8px; color: #10b981; font-weight: 600;">Direct Memory Access</td>
                    <td style="padding: 8px;">{io_res['dma_cpu_cycles']:,}</td>
                    <td style="padding: 8px;">{io_res['dma_cpu_utilization']:.3f}%</td>
                    <td style="padding: 8px;">Hardware Bus Master (Setup + IRQ)</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 8px;">
                🔄 DMA Modes: Burst vs. Cycle-Stealing
            </div>
            <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
                • <b>Burst Mode (Block Transfer):</b> DMA takes full control of system bus and transfers all {io_res['words_count']:,} words continuously. Maximizes transfer throughput; CPU is halted from external bus access.<br>
                • <b>Cycle-Stealing Mode:</b> DMA steals memory cycles during instruction decode / internal ALU operations without stalling the CPU pipeline.<br>
                • <b>CPU Clock Cycles Saved by DMA:</b> <span style="color: #34d399; font-weight: 700;">{io_res['cycles_saved_vs_pio']:,} cycles</span> ({io_res['speedup_dma_vs_pio']:.1f}× CPU speedup vs PIO).
            </div>
        </div>
        """, unsafe_allow_html=True)

    with io_c2:
        # Comparison Bar Chart
        fig, ax = setup_dark_plot()
        modes = ["Programmed I/O", "Interrupt I/O", "DMA Controller"]
        cycles = [io_res["pio_cpu_cycles"] / 1e6, io_res["interrupt_cpu_cycles"] / 1e6, io_res["dma_cpu_cycles"] / 1e6]
        colors = ["#f43f5e", "#f59e0b", "#10b981"]
        bars = ax.bar(modes, cycles, color=colors, width=0.55)
        ax.set_ylabel("CPU Cycles Consumed (Millions)")
        ax.set_title("CPU Overhead Across Storage I/O Strategies")
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f'{h:.2f}M', xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
        st.pyplot(fig)
        plt.close(fig)


# =============================================================================
# TAB 6: PARALLEL WORKERS & BUS CONTENTION
# =============================================================================
with tab_parallel:
    st.markdown("""
    <div style="font-weight: 700; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">
        ⚡ Multi-Core Parallel Processing & Shared Bus Contention
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 18px;">
        Models Amdahl's Law speedup vs shared memory bus saturation and MESI cache invalidations.
    </div>
    """, unsafe_allow_html=True)

    par_c1, par_c2 = st.columns([1.1, 1.0])

    with par_c1:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 12px;">
                🚀 Multi-Core Execution Metrics ({parallel['cores']} Worker Cores)
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 14px;">
                <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">SEQUENTIAL CYCLES</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc;">{parallel['sequential_cycles']:,}</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">PARALLEL EXEC CYCLES</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #34d399;">{parallel['parallel_cycles']:,}</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">ACTUAL SPEEDUP</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #00f2fe;">{parallel['actual_speedup']:.2f}×</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">CORE EFFICIENCY</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #c084fc;">{parallel['parallel_efficiency']:.1f}%</div>
                </div>
            </div>
            <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
                • <b>Parallelizable Code Fraction ($P$):</b> 92% (Independent seat searches & fare math)<br>
                • <b>Serial Fraction ($1 - P$):</b> 8% (Critical seat mutex locks, PNR database commits)<br>
                • <b>Amdahl's Theoretical Ceiling:</b> {parallel['amdahl_speedup']:.2f}× (Reduced to {parallel['actual_speedup']:.2f}× by bus contention)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with par_c2:
        # Multi-Core Scaling Curve Chart
        fig, ax = setup_dark_plot()
        df_curve = pd.DataFrame(parallel["scaling_curve"])
        ax.plot(df_curve["cores"], df_curve["ideal"], label="Ideal Linear Speedup", linestyle="--", color="#64748b", linewidth=1.5)
        ax.plot(df_curve["cores"], df_curve["amdahl"], label="Amdahl's Law (P=0.92)", color="#00f2fe", linewidth=2.0)
        ax.plot(df_curve["cores"], df_curve["actual"], label="Actual (With Bus Contention)", color="#10b981", linewidth=2.2)
        ax.scatter([parallel["cores"]], [parallel["actual_speedup"]], color="#f59e0b", s=90, zorder=5, label=f"Current: {parallel['cores']} Cores")
        ax.set_xlabel("Number of CPU Cores")
        ax.set_ylabel("Speedup Factor (×)")
        ax.set_title("Multi-Core Scaling & Contention Curve")
        ax.legend(facecolor="#0e1422", edgecolor="#334155")
        st.pyplot(fig)
        plt.close(fig)


# =============================================================================
# TAB 7: INTERACTIVE 32-BIT ADDRESS DECODER
# =============================================================================
with tab_decoder:
    st.markdown("""
    <div style="font-weight: 700; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">
        🔍 Interactive 32-Bit Memory Address Bitfield Decoder
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 18px;">
        Test any 32-bit hexadecimal address and inspect exact hardware bit slicing for Cache and Virtual Memory.
    </div>
    """, unsafe_allow_html=True)

    input_hex = st.text_input("Enter 32-Bit Hexadecimal Memory Address:", "0x004A2F8C")
    decoded = decode_address_hardware(input_hex, cfg, cfg)

    c_dec1, c_dec2 = st.columns(2)

    with c_dec1:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 10px;">
                🧠 Cache Hierarchy Address Split ({cfg['associativity']}, {cfg['block_size']}B blocks)
            </div>
            <div style="margin-bottom: 12px;">
                <span class="bit-box bit-sign">TAG [{decoded['cache']['tag_bits']}b]: {decoded['cache']['tag_val']}</span>
                <span class="bit-box bit-exp">INDEX [{decoded['cache']['index_bits']}b]: Set #{decoded['cache']['index_val']}</span>
                <span class="bit-box bit-mantissa">OFFSET [{decoded['cache']['offset_bits']}b]: {decoded['cache']['offset_val']}</span>
            </div>
            <div style="font-family: monospace; font-size: 0.8rem; background: rgba(0,0,0,0.4); padding: 10px; border-radius: 6px; color: #94a3b8;">
                Full 32-Bit Binary:<br>
                <span style="color: #60a5fa;">{decoded['cache']['tag_binary']}</span>
                <span style="color: #c084fc;">{decoded['cache']['index_binary']}</span>
                <span style="color: #34d399;">{decoded['cache']['offset_binary']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_dec2:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 10px;">
                🗂️ Virtual Memory Address Split ({cfg['page_size_kb']} KB Pages)
            </div>
            <div style="margin-bottom: 12px;">
                <span class="bit-box bit-exp">VPN [{decoded['vm']['vpn_bits']}b]: {decoded['vm']['vpn_val']}</span>
                <span class="bit-box bit-mantissa">PAGE OFFSET [{decoded['vm']['offset_bits']}b]: {decoded['vm']['page_offset_val']}</span>
            </div>
            <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; font-size: 0.85rem; color: #cbd5e1;">
                • <b>Mapped Physical Frame:</b> <span style="color: #00f2fe; font-weight: 600;">{decoded['vm']['simulated_ppn']}</span><br>
                • <b>Translated Physical Address:</b> <span style="color: #34d399; font-weight: 700;">{decoded['vm']['physical_addr']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# TAB 8: HARDWARE & ASSEMBLY DEMONSTRATION (CPULATOR & CIRCUITVERSE)
# =============================================================================
with tab_hardware:
    st.markdown("""
    <div style="font-weight: 700; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">
        🔌 Hardware-Level Demonstration: CPUlator Assembly & CircuitVerse
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 18px;">
        Fully runnable assembly code and gate-level circuit schematics ready for viva voce demonstration.
    </div>
    """, unsafe_allow_html=True)

    hw_t1, hw_t2, hw_t3 = st.tabs(["💻 CPUlator Assembly (ARM & RISC-V)", "⚡ CircuitVerse Schematics", "🤖 Tinkercad Arduino"])

    with hw_t1:
        st.markdown("""
        Paste this code directly into **CPUlator** ([cpulator.01xz.net/?sys=arm](https://cpulator.01xz.net/?sys=arm)) to step through ticket loop counting, memory loads/stores, and device status branch:
        """)
        st.code(CPULATOR_ARM_CODE, language="armasm")
        st.markdown("---")
        st.markdown("**Alternative RISC-V RV32I Implementation:**")
        st.code(CPULATOR_RISCV_CODE, language="assembly")

    with hw_t2:
        for c in CIRCUITVERSE_GUIDE["circuits"]:
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-weight: 700; color: #00f2fe; font-size: 1.05rem; margin-bottom: 4px;">{c['name']}</div>
                <div style="color: #cbd5e1; font-size: 0.85rem; margin-bottom: 8px;">{c['objective']}</div>
                <div style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 10px;">
                    <b>Required Components:</b> {', '.join(c['components'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("**Truth Table Verification:**")
            st.dataframe(pd.DataFrame(c["truth_table"]), hide_index=True, use_container_width=True)

    with hw_t3:
        st.markdown(f"**{TINKERCAD_SPECS['title']}**")
        st.markdown(f"Microcontroller: `{TINKERCAD_SPECS['microcontroller']}`")
        for p in TINKERCAD_SPECS["peripherals"]:
            st.markdown(f"- {p}")
        st.code(TINKERCAD_SPECS["arduino_code"], language="cpp")


# =============================================================================
# TAB 9: ACADEMIC REPORT & VIVA VOCE PREPARATION
# =============================================================================
with tab_report:
    st.markdown("""
    <div style="font-weight: 700; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">
        🎓 Project Report Documentation & Rapid-Fire Viva Voce Preparation
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 18px;">
        Aligned with GM University 40-Mark Evaluation Rubrics (Units 4-6: Memory Hierarchy & Storage).
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem; margin-bottom: 8px;">
            👥 Team Individual Contribution Declaration (10 Marks Component)
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(ACADEMIC_REPORT_DATA["team_members"]), hide_index=True, use_container_width=True)

    st.markdown("""
    <div style="font-weight: 700; font-size: 1.15rem; color: #f8fafc; margin-top: 20px; margin-bottom: 12px;">
        🎯 Top 10 Rapid-Fire Viva Voce Questions & Answers
    </div>
    """, unsafe_allow_html=True)

    for item in VIVA_VOCE_PREP:
        with st.expander(f"❓ {item['q']}"):
            st.markdown(f"**Model Viva Answer:**\n\n{item['ans']}")


# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; font-size: 0.8rem; padding: 10px 0;">
    RailCOA Simulator • Department of Computer Science & Engineering • GM University<br>
    Built with Python & Streamlit • Educational Testbed for Computer Organization & Architecture
</div>
""", unsafe_allow_html=True)
