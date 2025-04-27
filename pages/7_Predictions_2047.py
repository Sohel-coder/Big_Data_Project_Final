import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(page_title="Top Military Powers Prediction 2047", layout="wide")

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
    ms = pd.read_csv("2024_military_strength_by_country.csv")
    db = pd.read_csv("Defence_budget_cleaned.csv")
    return ms, db

military_strength, defense_budget = load_data()

def create_strength_score(df):
    """Compute a composite strength score from selected metrics."""
    metrics = [
        'total_national_populations',
        'active_service_military_manpower',
        'total_military_aircraft_strength',
        'total_combat_tank_strength',
        'navy_strength',
        'national_annual_defense_budgets',
        'purchasing_power_parities'
    ]
    for m in metrics:
        if m in df.columns:
            df[m] = pd.to_numeric(df[m], errors='coerce')
    df_clean = df.dropna(subset=[m for m in metrics if m in df.columns])
    scaler = StandardScaler()
    scaled = scaler.fit_transform(df_clean[metrics])
    sdf = pd.DataFrame(scaled, columns=metrics)
    sdf['strength_score'] = sdf.mean(axis=1)
    sdf['country'] = df_clean['country'].values
    sdf['pwr_index'] = pd.to_numeric(df_clean['pwr_index'], errors='coerce')
    return sdf.sort_values('strength_score', ascending=False)


def analyze_growth_trajectory(strength_df, budget_df):
    """Estimate budget growth slopes as growth indicators."""
    growth = []
    for c in strength_df['country']:
        subset = budget_df[budget_df['Country Name'] == c]
        years = [str(y) for y in range(2000, 2021) if str(y) in subset.columns]
        if subset.empty or len(years) < 5:
            growth.append(0)
        else:
            vals = subset[years].values.flatten().astype(float)
            idx = np.arange(len(vals))[~np.isnan(vals)].reshape(-1,1)
            y = vals[~np.isnan(vals)]
            model = LinearRegression().fit(idx, y)
            growth.append(model.coef_[0])
    strength_df['growth_slope'] = growth
    # normalize
    gs = strength_df['growth_slope']
    strength_df['growth_norm'] = (gs - gs.min())/(gs.max()-gs.min() + 1e-9)
    return strength_df


def predict_future(df, target_year=2047):
    years_proj = target_year - 2024
    # Projected strength = current + growth impact
    df['projected_strength'] = df['strength_score'] + df['growth_norm'] * (years_proj/5)
    # Combine with PWR index
    df['projection_score'] = df['projected_strength'] - 0.1 * df['pwr_index']
    return df.sort_values('projection_score', ascending=False)

# Run predictions
with st.spinner("Calculating predictions..."):
    strength = create_strength_score(military_strength)
    strength = analyze_growth_trajectory(strength, defense_budget)
    future = predict_future(strength)

# Display current vs predicted
col1, col2 = st.columns(2)
with col1:
    st.subheader("Current Top 10 Military Powers (2024)")
    cur = strength[['country','strength_score']].head(10).rename(columns={'country':'Country','strength_score':'Strength Score'})
    st.table(cur)
with col2:
    st.subheader("Predicted Top 10 Military Powers (2047)")
    pred = future[['country','projection_score']].head(10).rename(columns={'country':'Country','projection_score':'Projection Score'})
    st.table(pred)

# Show some rank changes
st.subheader("Changes in Rankings (2024 → 2047)")
cr = {c:i+1 for i,c in enumerate(cur['Country'])}
pr = {c:i+1 for i,c in enumerate(pred['Country'])}
changes=[]
for c in set(list(cr.keys())+list(pr.keys())):
    changes.append({'Country':c,'2024':cr.get(c,20),'2047':pr.get(c,20)})
chg_df = pd.DataFrame(changes)

fig,ax = plt.subplots(figsize=(8,6))
for _,r in chg_df.iterrows(): ax.plot([1,2],[r['2024'],r['2047']],'-',alpha=0.3)
ax.scatter([1]*len(chg_df),chg_df['2024'],s=80,label='2024')
ax.scatter([2]*len(chg_df),chg_df['2047'],s=80,label='2047')
for _,r in chg_df.iterrows():
    ax.text(0.8,r['2024'],r['Country'],ha='right')
    ax.text(2.1,r['2047'],r['Country'],ha='left')
ax.set_xticks([1,2]);ax.set_xticklabels(['2024','2047']);ax.set_ylim(16,0);ax.set_ylabel('Rank')
ax.legend();st.pyplot(fig)

st.markdown("**Note:** Increased weight to growth slope creates movement in top rankings.")
