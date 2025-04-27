import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Predictions", layout="wide")

st.title("🔮 Predicting the Future of Defence")
st.markdown(
    """
    This section provides a simple projection of each country’s military power index for 2047,
    based solely on the 2024 snapshot. Use the controls in the sidebar to explore individual countries
    and visualize the top N countries by projected strength.
    """
)

# --- Load 2024 Data ---
@st.cache_data
def load_current_power():
    """Load the latest (2024) military power index for each country."""
    df = pd.read_csv("data/2024_military_strength_by_country.csv")
    # Expect columns: 'country', 'pwr_index'
    return df[['country', 'pwr_index']]

current_df = load_current_power()

# --- Flat Projection to 2047 ---
current_df['pwr_index_2047'] = current_df['pwr_index']

# Prepare comparison DataFrame
compare_df = current_df.sort_values('pwr_index_2047').reset_index(drop=True)

# --- Sidebar Controls ---
st.sidebar.header("Options")
selected_country = st.sidebar.selectbox(
    "Select a country:",
    options=compare_df['country'].tolist()
)
top_n = st.sidebar.number_input(
    "Select top N countries:",
    min_value=1,
    max_value=len(compare_df),
    value=10,
    step=1
)

# --- Country Detail View ---
st.subheader(f"Power Index for {selected_country}")
row = compare_df[compare_df['country'] == selected_country].iloc[0]
tbl = pd.DataFrame({
    'Metric': ['Current (2024)', 'Projected (2047)'],
    'Power Index': [row['pwr_index'], row['pwr_index_2047']]
})
st.table(tbl)

# --- Top N Visualization ---
st.subheader(f"Top {top_n} Strongest Countries by Projected Power Index (2047)")
top_df = compare_df.head(top_n)
fig = px.bar(
    top_df,
    x='country',
    y='pwr_index_2047',
    title=f"Top {top_n} Countries by Projected Power Index (2047)",
    labels={'pwr_index_2047': 'Projected Power Index'},
    text=top_df['pwr_index_2047'].round(2)
)
fig.update_traces(textposition='outside')
fig.update_layout(yaxis=dict(autorange='reversed'))
st.plotly_chart(fig, use_container_width=True)

# Optional: Compare current vs projected for Top N
st.subheader(f"Current vs. Projected for Top {top_n}")
fig2 = px.bar(
    top_df,
    x='country',
    y=['pwr_index', 'pwr_index_2047'],
    labels={'value': 'Power Index', 'variable': 'Index Type'},
    title=f"Current vs Projected Power Index for Top {top_n}",
    text_auto='.2f'
)
fig2.update_layout(barmode='group', yaxis=dict(autorange='reversed'))
st.plotly_chart(fig2, use_container_width=True)

# --- Insight ---
st.markdown(
    "**Insight:** With a flat-line projection based solely on the 2024 snapshot, country rankings remain unchanged. "
    "Interactive selection lets you drill into any country and compare against the top performers."
)
