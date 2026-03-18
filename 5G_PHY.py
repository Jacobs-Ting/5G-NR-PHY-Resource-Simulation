import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.patches as patches

# --- 1. Page Configuration & Cyberpunk CSS ---
st.set_page_config(page_title="5G NR Pro Scheduler (HUD Edition)", layout="wide", initial_sidebar_state="expanded")

# 注入科技感 CSS (發光邊框、終端機字體)
st.markdown("""
<style>
    h1, h2, h3 {
        color: #00e5ff !important;
        font-family: 'Courier New', monospace !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    /* 儀表板卡片科技感設計 */
    [data-testid="metric-container"] {
        background-color: #0b101a;
        border: 1px solid #00e5ff;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
        padding: 15px;
        border-radius: 4px;
        border-left: 5px solid #00e5ff;
    }
    [data-testid="stMetricValue"] {
        color: #39ff14 !important;
        font-family: 'Courier New', monospace !important;
    }
    .stAlert {
        border-left-color: #ff007f !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📡 5G NR Tactical Scheduler [HUD.v1]")
st.markdown("Advanced L1/MAC Resource Allocation Console | **Status: ONLINE**")

# --- 1.5 3GPP Reference Expander ---
with st.expander("📚 SYSTEM ARCHITECTURE & 3GPP COMPLIANCE (REL-18)", expanded=False):
    st.markdown("""
    * **TS 38.211**: Resource grid structure, Logical Antenna Ports, CORESET, DFT-s-OFDM.
    * **TS 38.101-1 / -2 / -5**: N_RB tables, Global Frequency Raster, SDL/SUL characteristics.
    * **TS 38.521-1 / -2 / -5**: Band boundaries, NR-ARFCNs derivation, Inner/Outer Full allocations.
    * **TS 38.306**: Theoretical Maximum Throughput calculation.
    """)

# --- 2. 3GPP Data Repositories ---
TS_38101_N_RB_FR1 = {
    5: {15: 25, 30: 11}, 10: {15: 52, 30: 24, 60: 11}, 15: {15: 79, 30: 38, 60: 18},
    20: {15: 106, 30: 51, 60: 24}, 25: {15: 133, 30: 65, 60: 31}, 30: {15: 160, 30: 78, 60: 38},
    40: {15: 216, 30: 106, 60: 51}, 50: {15: 270, 30: 133, 60: 65}, 60: {30: 162, 60: 79},
    70: {30: 189, 60: 93}, 80: {30: 217, 60: 107}, 90: {30: 245, 60: 121}, 100: {30: 273, 60: 135}
}
TS_38101_N_RB_FR2 = {
    50: {60: 66, 120: 32}, 100: {60: 132, 120: 66}, 200: {60: 264, 120: 132}, 400: {120: 264}
}

band_db_fr1 = {
    "n1": {"mode": "FDD", "dl_min": 2110.0, "dl_max": 2170.0, "ul_min": 1920.0, "ul_max": 1980.0},
    "n2": {"mode": "FDD", "dl_min": 1930.0, "dl_max": 1990.0, "ul_min": 1850.0, "ul_max": 1910.0},
    "n3": {"mode": "FDD", "dl_min": 1805.0, "dl_max": 1880.0, "ul_min": 1710.0, "ul_max": 1785.0},
    "n5": {"mode": "FDD", "dl_min": 869.0, "dl_max": 894.0, "ul_min": 824.0, "ul_max": 849.0},
    "n7": {"mode": "FDD", "dl_min": 2620.0, "dl_max": 2690.0, "ul_min": 2500.0, "ul_max": 2570.0},
    "n8": {"mode": "FDD", "dl_min": 925.0, "dl_max": 960.0, "ul_min": 880.0, "ul_max": 915.0},
    "n12": {"mode": "FDD", "dl_min": 729.0, "dl_max": 746.0, "ul_min": 699.0, "ul_max": 716.0},
    "n14": {"mode": "FDD", "dl_min": 758.0, "dl_max": 768.0, "ul_min": 788.0, "ul_max": 798.0},
    "n20": {"mode": "FDD", "dl_min": 791.0, "dl_max": 821.0, "ul_min": 832.0, "ul_max": 862.0},
    "n25": {"mode": "FDD", "dl_min": 1930.0, "dl_max": 1995.0, "ul_min": 1850.0, "ul_max": 1915.0},
    "n28": {"mode": "FDD", "dl_min": 758.0, "dl_max": 803.0, "ul_min": 703.0, "ul_max": 748.0},
    "n29": {"mode": "SDL", "dl_min": 717.0, "dl_max": 728.0, "ul_min": 0.0, "ul_max": 0.0},
    "n30": {"mode": "FDD", "dl_min": 2350.0, "dl_max": 2360.0, "ul_min": 2305.0, "ul_max": 2315.0},
    "n38": {"mode": "TDD", "dl_min": 2570.0, "dl_max": 2620.0, "ul_min": 2570.0, "ul_max": 2620.0},
    "n39": {"mode": "TDD", "dl_min": 1880.0, "dl_max": 1920.0, "ul_min": 1880.0, "ul_max": 1920.0},
    "n40": {"mode": "TDD", "dl_min": 2300.0, "dl_max": 2400.0, "ul_min": 2300.0, "ul_max": 2400.0},
    "n41": {"mode": "TDD", "dl_min": 2496.0, "dl_max": 2690.0, "ul_min": 2496.0, "ul_max": 2690.0},
    "n48": {"mode": "TDD", "dl_min": 3550.0, "dl_max": 3700.0, "ul_min": 3550.0, "ul_max": 3700.0},
    "n66": {"mode": "FDD", "dl_min": 2110.0, "dl_max": 2200.0, "ul_min": 1710.0, "ul_max": 1780.0},
    "n71": {"mode": "FDD", "dl_min": 617.0, "dl_max": 652.0, "ul_min": 663.0, "ul_max": 698.0},
    "n77": {"mode": "TDD", "dl_min": 3300.0, "dl_max": 4200.0, "ul_min": 3300.0, "ul_max": 4200.0},
    "n78": {"mode": "TDD", "dl_min": 3300.0, "dl_max": 3800.0, "ul_min": 3300.0, "ul_max": 3800.0},
    "n79": {"mode": "TDD", "dl_min": 4400.0, "dl_max": 5000.0, "ul_min": 4400.0, "ul_max": 5000.0},
    "n80": {"mode": "SUL", "dl_min": 0.0, "dl_max": 0.0, "ul_min": 1710.0, "ul_max": 1785.0}
}
band_db_fr2 = {
    "n257": {"mode": "TDD", "dl_min": 26500.0, "dl_max": 29500.0, "ul_min": 26500.0, "ul_max": 29500.0},
    "n258": {"mode": "TDD", "dl_min": 24250.0, "dl_max": 27500.0, "ul_min": 24250.0, "ul_max": 27500.0},
    "n260": {"mode": "TDD", "dl_min": 37000.0, "dl_max": 40000.0, "ul_min": 37000.0, "ul_max": 40000.0},
    "n261": {"mode": "TDD", "dl_min": 27500.0, "dl_max": 28350.0, "ul_min": 27500.0, "ul_max": 28350.0}
}
band_db_ntn = {
    "n255": {"mode": "FDD", "dl_min": 1525.0, "dl_max": 1559.0, "ul_min": 1626.5, "ul_max": 1660.5},
    "n256": {"mode": "FDD", "dl_min": 2170.0, "dl_max": 2200.0, "ul_min": 1980.0, "ul_max": 2010.0}
}

# Algorithms
def freq_to_arfcn(freq_mhz):
    if freq_mhz < 3000.0: return int(round(freq_mhz / 0.005))
    elif freq_mhz <= 10050.0: return int(round(600000 + (freq_mhz - 3000.0) / 0.015))
    else: return int(round(2016667 + (freq_mhz - 24250.08) / 0.06))

def arfcn_to_freq_mhz(arfcn):
    if arfcn <= 600000: return arfcn * 0.005 
    elif arfcn <= 2016666: return 3000.0 + (arfcn - 600000) * 0.015
    else: return 24250.08 + (arfcn - 2016667) * 0.06

# --- 3. Sidebar Configuration Console ---
st.sidebar.header("0. RF DOMAIN")
domain_selection = st.sidebar.radio("Select Active Domain", ["TS 38.521-1 (FR1)", "TS 38.521-2 (FR2)", "TS 38.521-5 (NTN)"])

if "FR2" in domain_selection:
    active_band_db, active_n_rb_table, def_band = band_db_fr2, TS_38101_N_RB_FR2, "n257"
elif "NTN" in domain_selection:
    active_band_db, active_n_rb_table, def_band = band_db_ntn, TS_38101_N_RB_FR1, "n256"
else:
    active_band_db, active_n_rb_table, def_band = band_db_fr1, TS_38101_N_RB_FR1, "n78"

st.sidebar.markdown("---")
st.sidebar.header("1. CARRIER SPECS")
user_band = st.sidebar.text_input("Operating Band", value=def_band).strip().lower()

if user_band in active_band_db:
    b_info = active_band_db[user_band]
    duplex_mode = b_info["mode"]
    dl_min, dl_max, ul_min, ul_max = float(b_info["dl_min"]), float(b_info["dl_max"]), float(b_info["ul_min"]), float(b_info["ul_max"])
    if duplex_mode == "SDL":
        st.sidebar.warning("🚨 SDL Detected: Ext. Anchor required for UL.")
else:
    duplex_mode = st.sidebar.radio("Duplex", ["TDD", "FDD", "SDL", "SUL"])
    base_f = 28000.0 if "FR2" in domain_selection else 3300.0
    dl_min = st.sidebar.number_input("DL Min (MHz)", value=base_f) if duplex_mode != "SUL" else 0.0
    dl_max = st.sidebar.number_input("DL Max (MHz)", value=base_f + 100.0) if duplex_mode != "SUL" else 0.0
    ul_min = st.sidebar.number_input("UL Min (MHz)", value=base_f - 400.0) if duplex_mode in ["FDD", "SUL"] else (dl_min if duplex_mode=="TDD" else 0.0)
    ul_max = st.sidebar.number_input("UL Max (MHz)", value=base_f - 300.0) if duplex_mode in ["FDD", "SUL"] else (dl_max if duplex_mode=="TDD" else 0.0)

spacing_mhz = ul_min - dl_min if duplex_mode not in ["SDL", "SUL"] else 0

if "TDD" in duplex_mode:
    tdd_pattern = st.sidebar.text_input("TDD Slots", value="D,D,U,U")
    slots = [s.strip().upper() for s in tdd_pattern.split(',')]
    n_slots = len(slots)
    dl_syms, ul_syms = slots.count('D') * 14, slots.count('U') * 14
else:
    n_slots = st.sidebar.number_input("Sim Slots", min_value=1, max_value=20, value=4)
    slots = []
    dl_syms = n_slots * 14 if duplex_mode != "SUL" else 0
    ul_syms = n_slots * 14 if duplex_mode != "SDL" else 0
n_symbols = n_slots * 14
total_symbols_in_pattern = n_symbols if n_symbols > 0 else 1

calc_min, calc_max = (ul_min, ul_max) if duplex_mode == "SUL" else (dl_min, dl_max)
valid_bws = [bw for bw in active_n_rb_table.keys() if bw <= (calc_max - calc_min)]
if not valid_bws: 
    st.sidebar.error("❌ Invalid physical width!")
    st.stop()

selected_bw = st.sidebar.selectbox("Bandwidth (MHz)", valid_bws, index=len(valid_bws)-1)
test_ch = st.sidebar.radio("Test Channel", ["Low", "Mid", "High", "Custom"], index=1)
f_l, f_h = calc_min + selected_bw/2.0, calc_max - selected_bw/2.0
if test_ch == "Low": t_fc = f_l
elif test_ch == "High": t_fc = f_h
elif test_ch == "Mid": t_fc = (f_l + f_h)/2.0
else: t_fc = st.sidebar.number_input("Custom FC (MHz)", value=float((f_l+f_h)/2.0))

t_arfcn = freq_to_arfcn(t_fc)
t_fc_mhz = arfcn_to_freq_mhz(t_arfcn)
if duplex_mode == "SDL": fc_dl_mhz, fc_ul_mhz, dl_arfcn = t_fc_mhz, 0.0, t_arfcn
elif duplex_mode == "SUL": fc_dl_mhz, fc_ul_mhz, ul_arfcn = 0.0, t_fc_mhz, t_arfcn
else: fc_dl_mhz, fc_ul_mhz, dl_arfcn = t_fc_mhz, t_fc_mhz + spacing_mhz, t_arfcn

st.sidebar.markdown("---")
st.sidebar.header("2. PHYSICAL ALLOCATION")
selected_scs = st.sidebar.selectbox("SCS (kHz)", list(active_n_rb_table[selected_bw].keys()))
max_n_rb = active_n_rb_table[selected_bw][selected_scs]
conf_rbs = st.sidebar.number_input(f"PRBs Configured (Max {max_n_rb})", min_value=1, max_value=max_n_rb, value=max_n_rb)

if 'bwp_start' not in st.session_state: st.session_state.bwp_start = 0
if 'bwp_len' not in st.session_state: st.session_state.bwp_len = conf_rbs

def set_alloc(mode, total):
    if mode == "OF": st.session_state.bwp_start, st.session_state.bwp_len = 0, total
    elif mode == "IF": l = max(1, total//2); st.session_state.bwp_start, st.session_state.bwp_len = (total-l)//2, l
    elif mode == "E1": st.session_state.bwp_start, st.session_state.bwp_len = 0, 1
    elif mode == "I1": st.session_state.bwp_start, st.session_state.bwp_len = 1, 1

c1, c2 = st.sidebar.columns(2)
c1.button("Outer Full", on_click=set_alloc, args=("OF", conf_rbs), use_container_width=True)
c2.button("Inner Full", on_click=set_alloc, args=("IF", conf_rbs), use_container_width=True)
c3, c4 = st.sidebar.columns(2)
c3.button("Edge 1RB", on_click=set_alloc, args=("E1", conf_rbs), use_container_width=True)
c4.button("Inner 1RB", on_click=set_alloc, args=("I1", conf_rbs), use_container_width=True)

bwp_s = st.sidebar.number_input("BWP Start Index", min_value=0, max_value=conf_rbs-1, key='bwp_start')
bwp_l = st.sidebar.number_input("Active BWP Size", min_value=1, max_value=conf_rbs-bwp_s, key='bwp_len')

# --- 4. CORESET & Scheduler ---
max_core = (bwp_l // 6) * 6
core_d = st.sidebar.slider("CORESET Symbols", 1, 3, 2) if max_core >= 6 and duplex_mode != "SUL" else 0
core_l = st.sidebar.number_input("CORESET RBs", min_value=6, max_value=max_core, step=6, value=min(24, max_core)) if max_core >= 6 and duplex_mode != "SUL" else 0
core_s = st.sidebar.number_input("CORESET Offset", min_value=0, max_value=max(0, bwp_l-core_l), value=0) if max_core >= 6 and duplex_mode != "SUL" else 0

ul_waveform = st.sidebar.radio("Uplink Waveform", ["CP-OFDM", "DFT-s-OFDM"])
pucch_edge_rbs = max(1, int(bwp_l * 0.05))
pusch_rb_len = max(0, bwp_l - 2 * pucch_edge_rbs)

# --- 5. Antenna Port Filters & Signals ---
st.sidebar.markdown("---")
st.sidebar.header("3. LOGICAL PORTS")
port_filter = st.sidebar.selectbox("Signal Overlay", [
    "COMPOSITE (ALL)", "[DL] Port 1000", "[DL] Port 2000", 
    "[UL] Port 0", "[UL] Port 2000", "[DL] Port 4000 (SSB)", "[UL] Port 4000 (PRACH)"
])

# --- 6. TS 38.306 Throughput Configuration ---
st.sidebar.markdown("---")
st.sidebar.header("4. MAC LAYER MODULATION")
c5, c6 = st.sidebar.columns(2)
mimo_layers_dl = c5.selectbox("DL MIMO", [1, 2, 4, 8], index=2)
mimo_layers_ul = c6.selectbox("UL MIMO", [1, 2, 4], index=1) if "CP-OFDM" in ul_waveform else 1
mod_dict = {"QPSK": 2, "16QAM": 4, "64QAM": 6, "256QAM": 8}
mod_dl_str = c5.selectbox("DL Mod", list(mod_dict.keys()), index=3)
mod_ul_str = c6.selectbox("UL Mod", list(mod_dict.keys()), index=2)

# --- Grid Generation ---
n_sc = conf_rbs * 12
grid_tdd, grid_dl, grid_ul = np.zeros((n_sc, n_symbols)), np.zeros((n_sc, n_symbols)), np.zeros((n_sc, n_symbols))
PDCCH, PDSCH, CSI_RS, PUCCH, PUSCH, DMRS_DL, PTRS_DL, DMRS_UL, PTRS_UL, SSB, PRACH = 1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 9

def fill_dl(g, s):
    g[bwp_s*12:(bwp_s+bwp_l)*12, s:s+14] = PDSCH
    if core_l > 0 and core_d > 0: g[(bwp_s+core_s)*12:(bwp_s+core_s+core_l)*12, s:s+core_d] = PDCCH
    g[bwp_s*12:(bwp_s+bwp_l)*12:2, s+(3 if core_d==3 else 2)] = DMRS_DL
    g[bwp_s*12:(bwp_s+bwp_l)*12:48, s+4:s+13:4] = PTRS_DL
    center = bwp_s + bwp_l//2
    ssb_start = max(0, (center-10)*12)
    ssb_end = min(ssb_start+240, n_sc)
    if ssb_end > ssb_start: g[ssb_start:ssb_end, s+2:s+6] = SSB

def fill_ul(g, s):
    pe = pucch_edge_rbs * 12
    if pusch_rb_len > 0:
        g[bwp_s*12+pe:(bwp_s+bwp_l)*12-pe, s:s+13] = PUSCH
        g[bwp_s*12+pe:(bwp_s+bwp_l)*12-pe:2, s] = DMRS_UL
        g[bwp_s*12+pe:(bwp_s+bwp_l)*12-pe:48, s+2:s+12:4] = PTRS_UL
    center = bwp_s + bwp_l//2
    pr_start = max(0, (center-3)*12)
    pr_end = min(pr_start+72, n_sc)
    if pr_end > pr_start: g[pr_start:pr_end, s+2:s+12] = PRACH
    g[bwp_s*12:bwp_s*12+pe, s:s+13] = PUCCH
    g[(bwp_s+bwp_l)*12-pe:(bwp_s+bwp_l)*12, s:s+13] = PUCCH

if duplex_mode == "TDD":
    for idx, t in enumerate(slots):
        if t == 'D': fill_dl(grid_tdd, idx*14)
        elif t == 'U': fill_ul(grid_tdd, idx*14)
elif duplex_mode == "SDL":
    for idx in range(n_slots): fill_dl(grid_dl, idx*14)
elif duplex_mode == "SUL":
    for idx in range(n_slots): fill_ul(grid_ul, idx*14)
else:
    for idx in range(n_slots): fill_dl(grid_dl, idx*14); fill_ul(grid_ul, idx*14)

def apply_port_filter(g):
    f = g.copy()
    if "COMPOSITE" in port_filter: return f
    if "[DL] Port 1000" in port_filter: f[~np.isin(f, [PDSCH, DMRS_DL, PTRS_DL])] = 0
    elif "[DL] Port 2000" in port_filter: f[~np.isin(f, [PDCCH])] = 0
    elif "[UL] Port 0" in port_filter: f[~np.isin(f, [PUSCH, DMRS_UL, PTRS_UL])] = 0
    elif "[UL] Port 2000" in port_filter: f[~np.isin(f, [PUCCH])] = 0
    elif "[DL] Port 4000" in port_filter: f[~np.isin(f, [SSB])] = 0
    elif "[UL] Port 4000" in port_filter: f[~np.isin(f, [PRACH])] = 0
    return f

grid_tdd, grid_dl, grid_ul = apply_port_filter(grid_tdd), apply_port_filter(grid_dl), apply_port_filter(grid_ul)

# --- Throughput Calculation ---
mu = {15: 0, 30: 1, 60: 2, 120: 3}[selected_scs]
t_s_mu = (10**-3) / (14 * (2**mu))
def calc_tput(layers, qm, overhead, rb_len, sym_count):
    if sym_count == 0 or rb_len == 0: return 0.0
    return (10**-6) * layers * qm * 1.0 * (948/1024) * (rb_len * 12) / t_s_mu * (1 - overhead) * (sym_count / total_symbols_in_pattern)

dl_mbps = calc_tput(mimo_layers_dl, mod_dict[mod_dl_str], 0.14, bwp_l, dl_syms)
ul_mbps = calc_tput(mimo_layers_ul, mod_dict[mod_ul_str], 0.08, pusch_rb_len, ul_syms)

# --- Live Telemetry Dashboard ---
st.markdown("### 📡 LIVE TELEMETRY FEED")
m1, m2, m3, m4 = st.columns(4)
m1.metric("DL Throughput", f"{dl_mbps:.1f} Mbps")
m2.metric("UL Throughput", f"{ul_mbps:.1f} Mbps")
m3.metric("Target ARFCN", f"{t_arfcn}")
m4.metric("Resource Util", f"{bwp_l} / {conf_rbs} PRB")
st.markdown("---")

# --- Tactical Visualization (Cyberpunk Theme) ---
plt.style.use('dark_background') # 啟動 Matplotlib 黑暗模式
total_ms = n_slots * (1.0 / (2**mu))
carrier_bw_mhz = n_sc * (selected_scs / 1000.0)

# Cyberpunk Neon Colormap
cyber_colors = [
    '#0e1117', # 0: BG (Dark space)
    '#00e5ff', # 1: PDCCH (Neon Cyan)
    '#112240', # 2: PDSCH (Deep Navy)
    '#1a1a1a', # 3: CSI-RS 
    '#39ff14', # 4: PUCCH (Neon Green)
    '#0a3619', # 5: PUSCH (Dark Forest Green)
    '#1a1a1a', # 6: SRS
    '#00ffff', # 7: DMRS DL (Bright Cyan)
    '#ff007f', # 8: PTRS DL (Neon Pink)
    '#ff4500', # 9: PRACH (Neon Orange)
    '#adff2f', # 10: DMRS UL (Yellow-Green)
    '#ff1493', # 11: PTRS UL (Deep Pink)
    '#ff003c'  # 12: SSB (Neon Red)
]
cmap = mcolors.ListedColormap(cyber_colors)
norm = mcolors.BoundaryNorm(np.arange(-0.5, 13.5, 1), cmap.N)

legend = [
    mpatches.Patch(color='#00e5ff', label='PDCCH'), mpatches.Patch(color='#112240', label='PDSCH'),
    mpatches.Patch(color='#ff003c', label='SSB'), mpatches.Patch(color='#39ff14', label='PUCCH'), 
    mpatches.Patch(color='#0a3619', label='PUSCH'), mpatches.Patch(color='#00ffff', label='DMRS'),
    mpatches.Patch(color='#ff007f', label='PTRS'), mpatches.Patch(color='#ff4500', label='PRACH'),
    patches.Patch(edgecolor='#ff003c', facecolor='none', linestyle='--', linewidth=2, label='Active BWP')
]

def plot_grid(g, ax, base_f, title, ylabel):
    ax.set_facecolor('#0e1117') # 畫布底色
    ax.grid(color='#2b2b2b', linestyle=':', linewidth=0.5) # 科技感輔助格線
    
    # 軸線發光效果
    for spine in ax.spines.values():
        spine.set_color('#00e5ff')
        spine.set_linewidth(1.5)
        
    ax.xaxis.label.set_color('#00e5ff')
    ax.yaxis.label.set_color('#00e5ff')
    ax.tick_params(axis='x', colors='#00e5ff')
    ax.tick_params(axis='y', colors='#00e5ff')
    ax.title.set_color('#00e5ff')

    X, Y = np.meshgrid(np.linspace(0, total_ms, n_symbols+1), np.linspace(base_f, base_f+carrier_bw_mhz, n_sc+1))
    ax.pcolormesh(X, Y, g, cmap=cmap, norm=norm, edgecolors='none')
    
    # 霓虹紅 BWP 邊框
    bwp_min = base_f + bwp_s*12*(selected_scs/1000.0)
    ax.add_patch(patches.Rectangle((0, bwp_min), total_ms, bwp_l*12*(selected_scs/1000.0), linewidth=2.5, edgecolor='#ff003c', facecolor='none', linestyle='--'))
    ax.set_title(title, pad=15, fontdict={'family': 'monospace', 'weight': 'bold'}); ax.set_ylabel(ylabel); ax.set_xlabel("Time (ms)")

if duplex_mode == "TDD":
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('#0e1117')
    plot_grid(grid_tdd, ax, fc_dl_mhz-carrier_bw_mhz/2, f"> TDD GRID | BAND {user_band.upper()} | {test_ch.upper()} CH", "Freq (MHz)")
    ax.legend(handles=legend, loc='center left', bbox_to_anchor=(1.02, 0.5), facecolor='#0e1117', edgecolor='#00e5ff', labelcolor='#00e5ff')
    st.pyplot(fig)
elif duplex_mode == "SDL":
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('#0e1117')
    plot_grid(grid_dl, ax, fc_dl_mhz-carrier_bw_mhz/2, f"> SDL GRID (DOWNLINK) | BAND {user_band.upper()}", "DL Freq (MHz)")
    ax.legend(handles=legend, loc='center left', bbox_to_anchor=(1.02, 0.5), facecolor='#0e1117', edgecolor='#00e5ff', labelcolor='#00e5ff')
    st.pyplot(fig)
elif duplex_mode == "SUL":
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('#0e1117')
    plot_grid(grid_ul, ax, fc_ul_mhz-carrier_bw_mhz/2, f"> SUL GRID (UPLINK) | BAND {user_band.upper()}", "UL Freq (MHz)")
    ax.legend(handles=legend, loc='center left', bbox_to_anchor=(1.02, 0.5), facecolor='#0e1117', edgecolor='#00e5ff', labelcolor='#00e5ff')
    st.pyplot(fig)
else:
    fig, (ax_d, ax_u) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    fig.patch.set_facecolor('#0e1117')
    plot_grid(grid_dl, ax_d, fc_dl_mhz-carrier_bw_mhz/2, f"> DL GRID | BAND {user_band.upper()}", "DL Freq (MHz)")
    plot_grid(grid_ul, ax_u, fc_ul_mhz-carrier_bw_mhz/2, f"> UL GRID | SPACING: {spacing_mhz}MHz", "UL Freq (MHz)")
    fig.legend(handles=legend, loc='center right', bbox_to_anchor=(1.12, 0.5), facecolor='#0e1117', edgecolor='#00e5ff', labelcolor='#00e5ff')
    st.pyplot(fig)