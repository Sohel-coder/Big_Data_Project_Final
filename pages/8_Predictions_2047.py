import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px

st.set_page_config(page_title="Predictions", layout="wide")

st.title("Predicting the future of Defence")
st.markdown(
    """
    This section provides insights into the projected military power index for various countries in 2047, based on historical trends.
    """
)

# --- Load Data ---
@st.cache_data
def load_current_power():
    """Load the latest military power index for each country."""
    df = pd.read_csv("data/2024_military_strength_by_country.csv")
    # Expect columns: 'country', 'pwr_index'
    return df[['country', 'pwr_index']]

@st.cache_data
def load_power_trends():
    """Load historical power index trends for forecasting."""
    # Expect columns: 'country', 'year', 'pwr_index'
    return pd.read_csv("pwr_index_trends.csv")

# Load datasets
current_df = load_current_power()
trends_df = load_power_trends()

# Forecast to 2047 using linear regression per country
def forecast_2047(trend_df):
    X = trend_df[['year']].values.reshape(-1, 1)
    y = trend_df['pwr_index'].values
    model = LinearRegression()
    model.fit(X, y)
    pred = model.predict(np.array([[2047]]))[0]
    return pred

predictions = []
for country, grp in trends_df.groupby('country'):
    try:
        p2047 = forecast_2047(grp)
        predictions.append({'country': country, 'pwr_index_2047': p2047})
    except Exception:
        continue

pred_df = pd.DataFrame(predictions)
# Merge with current to compare
compare_df = current_df.merge(pred_df, on='country', how='inner')

# Sort by projected power (lower is stronger)
compare_df = compare_df.sort_values('pwr_index_2047')

# Display
st.header("Projected Military Power Index for 2047")

st.markdown(
    "Forecasted 'pwr_index' values for each country in 2047, based on historical trends (linear regression). Lower index = stronger power."
)

# Bar chart of top 10 strongest projected powers
top10 = compare_df.head(10)
fig = px.bar(
    top10,
    x='country',
    y='pwr_index_2047',
    title='Top 10 Countries by Projected Power Index (2047)',
    labels={'pwr_index_2047': 'Projected Power Index'},
    text=top10['pwr_index_2047'].round(2)
)
fig.update_traces(textposition='outside')
fig.update_layout(yaxis=dict(autorange='reversed'))
st.plotly_chart(fig, use_container_width=True)

# Full comparison table
st.subheader("Current vs. Projected Power Index")
compare_df['pwr_index'] = compare_df['pwr_index'].round(2)
compare_df['pwr_index_2047'] = compare_df['pwr_index_2047'].round(2)
st.dataframe(compare_df.rename(columns={
    'pwr_index': 'Current (2024)',
    'pwr_index_2047': 'Projected (2047)'
}), use_container_width=True)

# Insight
st.markdown(
    "**Insight:** Countries at the top of the projected list are expected to strengthen further relative to others by 2047, assuming linear trends."
)
