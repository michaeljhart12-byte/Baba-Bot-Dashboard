import streamlit as st
import pandas as pd
import numpy as np

# ──────────────────────────────────────────────
# Page config: Wide layout + light theme
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Bet Baba Signals Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏀"
)

# Clean light theme styling
st.markdown("""
    <style>
        /* Main spacing */
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }
        h1, h2, h3 {
            color: #1a1a1a;
            font-family: 'Segoe UI', sans-serif;
        }
        /* Stat cards */
        .stMetric {
            background-color: #f8f9fa;
            border-radius: 12px;
            padding: 1.4rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            text-align: center;
            border: 1px solid #e0e0e0;
            transition: transform 0.2s;
        }
        .stMetric:hover {
            transform: translateY(-2px);
        }
        .stMetricLabel {
            font-size: 1.05rem !important;
            color: #555 !important;
            margin-bottom: 0.6rem;
        }
        .stMetricValue {
            font-size: 2.4rem !important;
            font-weight: 700 !important;
        }
        /* Chart container */
        .stPlotlyChart, .stLineChart {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            padding: 1.2rem;
        }
        /* Sidebar */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Title
# ──────────────────────────────────────────────
st.title("Bet Baba Signals Dashboard")
st.markdown("Professional overview of all signals & performance")

# ──────────────────────────────────────────────
# Load Data
# ──────────────────────────────────────────────
try:
    df = pd.read_csv("signals.csv", parse_dates=['Signal Time', 'Commence Time', 'Resolved Time'])
    st.success(f"Loaded {len(df)} signals")
except Exception as e:
    st.error(f"Error loading signals.csv: {str(e)}")
    df = pd.DataFrame()

# ──────────────────────────────────────────────
# Sidebar Filters (apply to all stats/chart)
# ──────────────────────────────────────────────
st.sidebar.header("Filters")

books = st.sidebar.multiselect(
    "Sportsbooks",
    options=df['Book'].unique() if 'Book' in df.columns else [],
    default=[]
)
if books:
    df = df[df['Book'].isin(books)]

markets = st.sidebar.multiselect(
    "Props/Markets",
    options=df['Market'].unique() if 'Market' in df.columns else [],
    default=[]
)
if markets:
    df = df[df['Market'].isin(markets)]

# ──────────────────────────────────────────────
# Top Stat Cards (with green/red coloring)
# ──────────────────────────────────────────────
if not df.empty:
    st.subheader("Key Statistics")
    
    resolved = df[df['Resolved?'] == True]
    pending = df[df['Resolved?'] == False]
    
    total_bets = len(df)
    wins = len(resolved[resolved['Actual Outcome'] == 'Win'])
    losses = len(resolved[resolved['Actual Outcome'] == 'Loss'])
    voids_dnp = len(resolved[resolved['Actual Outcome'].isin(['Void', 'DNP or no data'])]) + len(resolved[resolved['Actual Outcome'].isna()])
    graded_bets = wins + losses
    win_rate = (wins / graded_bets * 100) if graded_bets > 0 else 0
    
    # Profit/Loss & ROI ($100 flat bet, American odds)
    def calc_profit(odds, outcome):
        if pd.isna(outcome) or outcome in ['Void', 'Pending', 'DNP or no data']:
            return 0
        if outcome != 'Win':
            return -100
        if odds > 0:
            return odds
        else:
            return 10000 / abs(odds)
    
    resolved['Profit'] = resolved.apply(lambda row: calc_profit(row['Odds'], row['Actual Outcome']), axis=1)
    total_profit = resolved['Profit'].sum()
    roi = (total_profit / (graded_bets * 100)) * 100 if graded_bets > 0 else 0
    
    # Display in wide columns
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([1.2, 1.4, 1.2, 1.4, 1.2])  # wider for RECORD
        
        col1.metric("TOTAL BETS", f"{total_bets:,}", delta=f"{len(pending)} pending")
        
        record_delta = f"{voids_dnp} void/DNP"
        record_color = "#2ecc71" if wins > losses else "#e74c3c"
        with col2:
            st.metric("RECORD", f"{wins}W - {losses}L", delta=record_delta, delta_color="normal")
            st.markdown(f"<div style='color:{record_color}; font-weight:bold; text-align:center;'>{wins}W - {losses}L</div>", unsafe_allow_html=True)
        
        win_rate_delta = f"{52.4:.1f}% to break even"
        col3.metric("WIN RATE", f"{win_rate:.1f}%", delta=win_rate_delta)
        
        pl_color = "normal" if total_profit >= 0 else "inverse"
        col4.metric("PROFIT/LOSS", f"+${total_profit:,.0f}", delta="$100/bet", delta_color=pl_color)
        
        roi_color = "normal" if roi >= 0 else "inverse"
        col5.metric("ROI", f"+{roi:.1f}%", delta="return on investment", delta_color=roi_color)

# ──────────────────────────────────────────────
# Cumulative P/L Chart
# ──────────────────────────────────────────────
if not df.empty and 'Profit' in resolved.columns:
    st.subheader("Cumulative Profit/Loss Over Time")
    
    resolved = resolved.sort_values('Signal Time')
    resolved['Cumulative Profit'] = resolved['Profit'].cumsum()
    
    # Line chart with conditional coloring (green up, red down)
    chart_data = resolved.set_index('Signal Time')['Cumulative Profit']
    
    st.line_chart(
        chart_data,
        use_container_width=True,
        height=500,
        color="#2ecc71" if chart_data.iloc[-1] >= 0 else "#e74c3c"
    )
    
    st.caption(f"Total P/L: +${total_profit:,.0f} | {len(resolved)} graded bets")

# Footer note
st.markdown("---")
st.caption("Bet Baba Signals Dashboard • Updated from signals.csv • Last refresh: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
