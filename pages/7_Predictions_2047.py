import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(page_title="Top Military Powers Prediction 2047", layout="wide")

# Title
st.title("Top Military Powers Prediction for 2047")

# Load data
@st.cache_data
def load_data():
    """
    Load military strength and defense budget datasets.
    Expects:
    - 2024_military_strength_by_country.csv
    - Defence_budget_cleaned.csv
    """
    military_strength = pd.read_csv("2024_military_strength_by_country.csv")
    defense_budget = pd.read_csv("Defence_budget_cleaned.csv")
    return military_strength, defense_budget

military_strength, defense_budget = load_data()

# Utility functions
def create_strength_score(df):
    """Compute a composite strength score from selected metrics."""
    power_columns = [
        'total_national_populations', 
        'active_service_military_manpower',
        'total_military_aircraft_strength',
        'total_combat_tank_strength',
        'navy_strength',
        'national_annual_defense_budgets',
        'purchasing_power_parities'
    ]
    # Convert and drop incomplete
    for col in power_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df_clean = df.dropna(subset=[c for c in power_columns if c in df.columns])

    scaler = StandardScaler()
    scaled = scaler.fit_transform(df_clean[power_columns])
    scaled_df = pd.DataFrame(scaled, columns=power_columns)
    scaled_df['strength_score'] = scaled_df.mean(axis=1)
    scaled_df['country'] = df_clean['country'].values
    scaled_df['pwr_index'] = pd.to_numeric(df_clean['pwr_index'], errors='coerce')
    return scaled_df.sort_values('strength_score', ascending=False)


def analyze_growth_trajectory(strength_df, budget_df):
    """Estimate budget growth slopes as growth indicators."""
    # Assume 'Country Code' matches 'country_code' in strength_df
    # Build mapping if needed
    growth_scores = []
    for country in strength_df['country']:
        # Filter budget by country code or name
        sub = budget_df[budget_df['Country Name'] == country]
        if sub.empty:
            growth_scores.append(0)
            continue
        years = [str(y) for y in range(2000, 2021) if str(y) in sub.columns]
        if not years:
            growth_scores.append(0)
            continue
        vals = sub[years].values.flatten().astype(float)
        idx = np.arange(len(vals))[~np.isnan(vals)].reshape(-1, 1)
        y = vals[~np.isnan(vals)]
        if len(y) < 5:
            growth_scores.append(0)
            continue
        model = LinearRegression().fit(idx, y)
        growth_scores.append(model.coef_[0])

    strength_df['growth_score'] = growth_scores
    # Normalize
    min_g, max_g = strength_df['growth_score'].min(), strength_df['growth_score'].max()
    if max_g > min_g:
        strength_df['growth_score_normalized'] = (
            (strength_df['growth_score'] - min_g) / (max_g - min_g)
        )
    else:
        strength_df['growth_score_normalized'] = 0
    return strength_df


def predict_future_ranking(df, target_year=2047):
    """Combine strength and growth into a projection score."""
    years_proj = target_year - 2024
    strength_w, growth_w = (0.5, 0.5) if years_proj > 10 else (0.7, 0.3)
    df['projection_score'] = (
        strength_w * df['strength_score'] +
        growth_w * df['growth_score_normalized'] -
        0.2 * df['pwr_index']
    )
    return df.sort_values('projection_score', ascending=False)

# Prediction and display
with st.spinner("Generating predictions..."):
    strength_df = create_strength_score(military_strength)
    projection_df = analyze_growth_trajectory(strength_df, defense_budget)
    future_ranking = predict_future_ranking(projection_df)

# Show tables
col1, col2 = st.columns(2)
with col1:
    st.subheader("Current Top 10 Military Powers (2024)")
    current = strength_df[['country', 'strength_score']].head(10).rename(
        columns={'country': 'Country', 'strength_score': 'Strength Score'}
    )
    st.table(current)
with col2:
    st.subheader("Predicted Top 10 Military Powers (2047)")
    future = future_ranking[['country', 'projection_score']].head(10).rename(
        columns={'country': 'Country', 'projection_score': 'Projection Score'}
    )
    st.table(future)

# Rank change visualization
st.subheader("Projected Changes in Military Power Rankings (2024 vs 2047)")
# Prepare data
cur_ranks = {c: i+1 for i, c in enumerate(strength_df['country'].head(15))}
fut_ranks = {c: i+1 for i, c in enumerate(future_ranking['country'].head(15))}
vis = []
for c in set(cur_ranks) | set(fut_ranks):
    cr, fr = cur_ranks.get(c, 20), fut_ranks.get(c, 20)
    if cr <= 15 or fr <= 15:
        vis.append({'Country': c, '2024': cr, '2047': fr})
vis_df = pd.DataFrame(vis).sort_values('2047')

fig, ax = plt.subplots(figsize=(8, 6))
for _, r in vis_df.iterrows():
    ax.plot([1, 2], [r['2024'], r['2047']], 'k-', alpha=0.3)
ax.scatter([1]*len(vis_df), vis_df['2024'], s=100, label='2024')
ax.scatter([2]*len(vis_df), vis_df['2047'], s=100, label='2047')
for _, r in vis_df.iterrows():
    ax.text(0.9, r['2024'], r['Country'], ha='right', va='center')
    ax.text(2.1, r['2047'], r['Country'], ha='left', va='center')
ax.set_xticks([1, 2]); ax.set_xticklabels(['2024', '2047'])
ax.set_ylim(16, 0); ax.set_ylabel('Rank'); ax.grid(True, linestyle='--', alpha=0.7)
st.pyplot(fig)

# Explanation
st.subheader("Key Factors Influencing Predictions")
st.markdown(
    """
    1. Current Military Strength
    2. Defense Budget Growth Trends
    3. Economic Indicators
    4. Technological Advancements
    5. Geopolitical Factors

    *Predictions are illustrative and subject to data limitations.*
    """
)
