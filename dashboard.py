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
    page_icon="⚽️"
)

# Light theme clean styling
st.markdown("""
    <style>
        /* Main spacing & fonts */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
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
            padding: 1.2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.08);
            text-align: center;
            border: 1px solid #e0e0e0;
        }
        .stMetricLabel {
            font-size: 1rem !important;
            color: #555 !important;
            margin-bottom: 0.5rem;
        }
        .stMetricValue {
            font-size: 2.2rem !important;
            font-weight: 700 !important;
        }
        /* Chart container */
        .stPlotlyChart {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.08);
            padding: 1rem;
        }
        /* Table */
        .stDataFrame {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Title & Load Data
# ──────────────────────────────────────────────
st.title("Bet Baba Signals Dashboard")
st.markdown("Professional overview of all signals — editable & sortable table below")

try:
    df = pd.read_csv("signals.csv", parse_dates=['Signal Time', 'Commence Time', 'Resolved Time'])
    st.success(f"Loaded {len(df)} signals")
except Exception as e:
    st.error(f"Error loading signals.csv: {str(e)}")
    df = pd.DataFrame()

# ──────────────────────────────────────────────
# Sidebar Filters
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
# Top Stat Cards (like your screenshot)
# ──────────────────────────────────────────────
if not df.empty:
    st.subheader("Key Statistics")
    
    resolved = df[df['Resolved?'] == True]
    pending = df[df['Resolved?'] == False]
    
    total_bets = len(df)
    wins = len(resolved[resolved['Actual Outcome'] == 'Win'])
    losses = len(resolved[resolved['Actual Outcome'] == 'Loss'])
    voids = len(resolved[resolved['Actual Outcome'] == 'Void']) + len(resolved[resolved['Actual Outcome'].isna()])
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    record_str = f"{wins}W - {losses}L"
    
    # Simple ROI % (assumes $100 flat bet, American odds)
    def calc_profit(odds, outcome):
        if pd.isna(outcome) or outcome in ['Void', 'Pending']:
            return 0
        if outcome != 'Win':
            return -100
        if odds > 0:
            return odds
        else:
            return 10000 / abs(odds)
    
    resolved['Profit'] = resolved.apply(lambda row: calc_profit(row['Odds'], row['Actual Outcome']), axis=1)
    total_profit = resolved['Profit'].sum()
    roi = (total_profit / (len(resolved) * 100)) * 100 if len(resolved) > 0 else 0
    
    # Display in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("TOTAL BETS", f"{total_bets:,}", delta=f"{len(pending)} pending")
    col2.metric("RECORD", record_str, delta=f"{voids} void/DNP")
    col3.metric("WIN RATE", f"{win_rate:.1f}%", delta=f"{52.4:.1f}% to break even")
    col4.metric("PROFIT/LOSS", f"+${total_profit:,.0f}", delta="$100/bet")
    col5.metric("ROI", f"+{roi:.1f}%", delta="return on investment")

# ──────────────────────────────────────────────
# Cumulative P/L Chart
# ──────────────────────────────────────────────
if not df.empty and 'Profit' in resolved.columns:
    st.subheader("Cumulative Profit/Loss Over Time")
    
    # Sort by Signal Time
    resolved = resolved.sort_values('Signal Time')
    resolved['Cumulative Profit'] = resolved['Profit'].cumsum()
    
    # Simple line chart (Streamlit native)
    st.line_chart(
        resolved.set_index('Signal Time')['Cumulative Profit'],
        use_container_width=True,
        height=400
    )
    
    st.caption(f"Total P/L: +${total_profit:,.0f} | {len(resolved)} graded bets")

# ──────────────────────────────────────────────
# Filters & Editable Table (your existing code)
# ──────────────────────────────────────────────
st.subheader("Signals Table (Editable & Sortable)")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=False,
    column_config={
        "Signal Time": st.column_config.DatetimeColumn("Signal Time", format="DD/MM/YYYY HH:mm"),
        "Commence Time": st.column_config.DatetimeColumn("Commence Time", format="DD/MM/YYYY HH:mm"),
        "Resolved Time": st.column_config.DatetimeColumn("Resolved Time", format="DD/MM/YYYY HH:mm"),
        "Resolved?": st.column_config.CheckboxColumn("Resolved?", default=False),
    }
)

# Save button
if st.button("Save Changes"):
    edited_df.to_csv("signals.csv", index=False)
    st.success("Changes saved! Refresh to see updates.")
