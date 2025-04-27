import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Predictions", layout="wide")

st.title("🔮 Predicting the Future of Defence")
st.markdown(
    """
    This section provides a simple projection of each country’s military power index for 2047,
    based solely on the 2024 snapshot. Since we no longer have multi-year trends, the projection
    holds 2024 values constant through to 2047.
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

# Sort by projected power (lower = stronger)
compare_df = current_df.sort_values('pwr_index_2047')

# --- Visualization: Top 10 Strongest in 2047 ---
st.header("Top 10 Strongest Countries by Projected Power Index (2047)")
fig = px.bar(
    compare_df.head(10),
    x='country',
    y='pwr_index_2047',
    title='Projected Power Index (2047)',
    labels={'pwr_index_2047': 'Projected Power Index'},
    text=compare_df.head(10)['pwr_index_2047'].round(2)
)
fig.update_traces(textposition='outside')
fig.update_layout(yaxis=dict(autorange='reversed'))
st.plotly_chart(fig, use_container_width=True)

# --- Full Comparison Table ---
st.subheader("Current (2024) vs. Projected (2047) Power Index")
display_df = compare_df.copy()
display_df['pwr_index'] = display_df['pwr_index'].round(2)
display_df['pwr_index_2047'] = display_df['pwr_index_2047'].round(2)
st.dataframe(
    display_df.rename(columns={
        'pwr_index': 'Current (2024)',
        'pwr_index_2047': 'Projected (2047)'
    }),
    use_container_width=True
)

# --- Insight ---
st.markdown(
    "**Insight:**\n"
    "With a flat-line projection based solely on the 2024 snapshot, country rankings remain unchanged. "
    "For more nuanced forecasts, you’ll need multi-year trend data or a defined growth/decay rate."
)
