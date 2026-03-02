import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bet Baba Signals Dashboard", layout="wide")

st.title("Bet Baba Signals Dashboard")
st.markdown("Signals Table (Editable & Sortable)")

# Load signals with error handling
try:
    df = pd.read_csv("signals.csv", parse_dates=['Signal Time', 'Commence Time', 'Resolved Time'])
    st.success(f"Loaded {len(df)} signals")
except Exception as e:
    st.error(f"Error loading signals.csv: {str(e)}")
    df = pd.DataFrame()

# Filters (sidebar)
st.sidebar.header("Filters")
books = st.sidebar.multiselect("Sportsbooks", options=df['Book'].unique() if 'Book' in df.columns else [], default=[])
if books:
    df = df[df['Book'].isin(books)]

# More filters (add as needed, e.g. markets)
markets = st.sidebar.multiselect("Props/Markets", options=df['Market'].unique() if 'Market' in df.columns else [], default=[])
if markets:
    df = df[df['Market'].isin(markets)]

# Display editable table
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=False)

# Save button
if st.button("Save Changes"):
    edited_df.to_csv("signals.csv", index=False)
    st.success("Changes saved!")
