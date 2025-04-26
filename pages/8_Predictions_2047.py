import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="🔮 2050 Defence Power Prediction", layout="wide")
st.title("🔮 Predicting Global & Indian Defence Power Index for 2050")

# --- Data Loading ---
@st.cache_data
def load_datasets():
    # 1. Defence Budget (% GDP)
    budget = pd.read_csv("data/Cleaned_Defence_Budget.csv")
    bud_long = (
        budget.melt(id_vars=["Country Name"], var_name="year", value_name="def_budget_pct_gdp")
              .rename(columns={"Country Name":"country"})
              .assign(year=lambda d: d["year"].astype(int))
    )
    bud_hist = bud_long[(bud_long.year>=2005)&(bud_long.year<=2018)]
    bud_feat = bud_hist.groupby('country')['def_budget_pct_gdp'].mean().reset_index()

    # 2. Military Expenditure (USD)
    exp = pd.read_excel("data/Military_Expenditure_final_rounded.xlsx")
    exp_long = (
        exp.melt(id_vars=["Name"], var_name="year", value_name="exp_usd")
           .rename(columns={"Name":"country"})
           .assign(year=lambda d: d["year"].astype(int))
    )
    exp_hist = exp_long[(exp_long.year>=2005)&(exp_long.year<=2018)]
    exp_feat = exp_hist.groupby('country')['exp_usd'].mean().reset_index()

    # 3. Arms Trade (Exports & Imports)
    trade = pd.read_csv("data/exports_imports_cleaned.csv")
    trade_hist = trade[(trade.year>=2005)&(trade.year<=2018)]
    trade_feat = (
        trade_hist.groupby('country')
                  [['exports_usd','imports_usd']]
                  .mean()
                  .reset_index()
    )

    # 4. Defence Companies Revenues
    comp = pd.read_csv("data/updated_defense_companies_2005_2020.csv")
    comp_hist = comp[(comp.year>=2005)&(comp.year<=2018)]
    # aggregate total revenue per country
    comp_feat = (
        comp_hist.groupby('country')['revenue_usd']
                 .sum()
                 .reset_index()
                 .rename(columns={'revenue_usd':'total_def_comp_revenue'})
    )

    # 5. Military Strength & Power Index (2024)
    ms = pd.read_csv("data/2024_military_strength_by_country.csv")
    ms = ms.rename(columns={
        "active_service_military_manpower":"active_personnel",
        "total_military_aircraft_strength":"total_aircraft",
        "total_combat_tank_strength":"total_tanks",
        "navy_strength":"navy_strength",
        "pwr_index":"pwr_index"
    })

    # Merge all features
    df = ms.merge(bud_feat, on='country', how='left') \
           .merge(exp_feat, on='country', how='left') \
           .merge(trade_feat, on='country', how='left') \
           .merge(comp_feat, on='country', how='left')

    # Drop missing
    df_clean = df.dropna()
    return df_clean

# Load
df = load_datasets()
st.markdown(f"Loaded data for **{len(df)}** countries with complete features.")

# --- Prepare Training Data ---
feature_cols = [
    'active_personnel','total_aircraft','total_tanks','navy_strength',
    'def_budget_pct_gdp','exp_usd','exports_usd','imports_usd','total_def_comp_revenue'
]
X = df[feature_cols]
y = df['pwr_index']

# --- Train Model ---
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# --- Predict for 2050 ---
df['pwr_index_2050'] = model.predict(X)

def display_results(df):
    # Global Top 10
    st.header("🏆 Top 10 Strongest Countries in 2050 (Lowest Power Index)")
    top10 = df.nsmallest(10, 'pwr_index_2050')[['country','pwr_index_2050']]
    fig = px.bar(
        top10, x='country', y='pwr_index_2050',
        title='Projected 2050 Power Index (lower is stronger)',
        text=top10['pwr_index_2050'].round(2),
        labels={'pwr_index_2050':'2050 Power Index'}, template='plotly_white'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis={'autorange':'reversed'})
    st.plotly_chart(fig, use_container_width=True)

    # India-specific
    st.subheader("🇮🇳 India's Projection for 2050")
    india_row = df[df.country=='India']
    if not india_row.empty:
        current = india_row['pwr_index'].values[0]
        future = india_row['pwr_index_2050'].values[0]
        st.write(f"**Current (2024) Power Index:** {current:.2f}")
        st.write(f"**Projected (2050) Power Index:** {future:.2f}")
    else:
        st.warning("India data not available.")

    # Feature Importances
    st.subheader("🔍 Feature Importance (Random Forest)")
    fi = pd.DataFrame({
        'feature':feature_cols,
        'importance':model.feature_importances_
    }).sort_values('importance', ascending=False)
    st.bar_chart(fi.set_index('feature'))

# Display
display_results(df)

# --- Explanation ---
st.markdown("""
**Model Details**  
- Trained a Random Forest on 2024 power index using historical averages (2005–2018) of budgets, expenditures, trade, companies, plus 2024 military strength.  
- Projected through the same relationships to 2050, assuming no major structural shifts.  
- Lower Power Index indicates stronger strategic position.  
""")
import plotly.express as px
import streamlit as st

# —— assume `df` is your DataFrame with columns "country" and "predicted_pwr_index_2050" —— 

st.header("🔮 2050 Projections: Visual Summary")

# ── Top 10 Strongest ──
st.subheader("🏆 Top 10 Strongest Countries by 2050")
top10 = df.nsmallest(10, "predicted_pwr_index_2050")
fig_top = px.bar(
    top10,
    x="country",
    y="predicted_pwr_index_2050",
    text=top10["predicted_pwr_index_2050"].round(2),
    labels={"predicted_pwr_index_2050":"Projected Power Index (2050)"},
    title="Lower Power Index → Stronger Power",
    template="plotly_white"
)
# invert y-axis so the strongest (lowest) appear on top
fig_top.update_layout(yaxis={"autorange":"reversed"})
fig_top.update_traces(textposition="outside")
st.plotly_chart(fig_top, use_container_width=True)

# ── Distribution ──
st.subheader("📊 Distribution of Projected Power Index (2050)")
fig_dist = px.histogram(
    df,
    x="predicted_pwr_index_2050",
    nbins=20,
    title="How the World’s Power Indices Spread Out by 2050",
    labels={"predicted_pwr_index_2050":"Projected Power Index (2050)"},
    template="plotly_white"
)
st.plotly_chart(fig_dist, use_container_width=True)

# ── India Highlight ──
india = df[df["country"] == "India"]
if not india.empty:
    india_score = india["predicted_pwr_index_2050"].iloc[0]
    india_rank = int(df["predicted_pwr_index_2050"]
                     .rank(method="min")
                     .loc[india.index[0]])
    st.markdown(f"### 🇮🇳 India\n"
                f"- **Projected Power Index (2050):** {india_score:.2f}\n"
                f"- **Projected Global Rank:** {india_rank}")
else:
    st.info("No projection available for India.")
