import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px

# ── Streamlit page setup ──
st.set_page_config(
    page_title="🔮 Defence Power Index Projection (2050)",
    layout="wide"
)
st.title("🔮 Predicting Global & Indian Defence Power Index (2050)")
st.markdown("""
We train a linear regression model on **2024** military-strength data combined with
**2005–2018** averages of:
- **Defence budget** (% of GDP)
- **Annual military expenditure** (USD)
- **Exports & imports** (USD)
- **Defence-industry scale** (annual revenue & employees)

We then predict each country’s **Power Index** in **2050**, assuming these inputs
remain at their historical averages.
""")

# ── Data loading & aggregation ──
@st.cache_data
def load_and_aggregate():
    # 1) Defence budget % GDP 2005–2018
    bud = pd.read_csv("data/Cleaned_Defence_Budget.csv")
    # identify year‐columns by checking if the column name is all digits
    year_cols = [c for c in bud.columns if c.isdigit()]
    
    bud_long = ( bud.melt(
        id_vars=["Country Name"],
        var_name="year",
        value_name="def_budget_pct_gdp"
    )
    .rename(columns={"Country Name": "country"})
    .assign(year=lambda df: df["year"].astype(int))
    )

    bud_long["year"] = bud_long["year"].astype(int)
    bud_avg = (
        bud_long
        .query("2005 <= year <= 2018")
        .groupby("country", as_index=False)["def_budget_pct_gdp"]
        .mean()
    )

    # 2) Military expenditure USD 2005–2018
    exp = pd.read_excel("data/Military_Expenditure_final_rounded.xlsx")
    exp_long = (
        exp
        .melt(id_vars=["Name"], var_name="year", value_name="exp_usd")
        .rename(columns={"Name": "country"})
    )
    exp_long["year"] = exp_long["year"].astype(int)
    exp_avg = (
        exp_long
        .query("2005 <= year <= 2018")
        .groupby("country", as_index=False)["exp_usd"]
        .mean()
    )

    # 3) Trade (exports & imports) 2005–2018
    trade = pd.read_csv("data/exports_imports_cleaned.csv")
    trade_avg = (
        trade
        .query("2005 <= year <= 2018")
        .groupby("country", as_index=False)[["exports_usd", "imports_usd"]]
        .mean()
    )

    # 4) Defence-industry companies 2005–2018
    comp = pd.read_csv("data/updated_defense_companies_2005_2020.csv")
    comp_avg = (
        comp
        .query("2005 <= year <= 2018")
        .groupby("country", as_index=False)[["revenue_usd", "employees"]]
        .mean()
    )

    # 5) 2024 military strength & current Power Index
    strength = pd.read_csv("data/2024_military_strength_by_country.csv")
    strength = strength.rename(columns={
        "active_service_military_manpower": "active_personnel",
        "total_military_aircraft_strength": "total_aircraft",
        "total_combat_tank_strength": "total_tanks",
        "navy_strength":            "navy_strength",
        "pwr_index":                "pwr_index"
    })

    # Merge all data on 'country'
    df = (
        strength[[
            "country","active_personnel","total_aircraft",
            "total_tanks","navy_strength","pwr_index"
        ]]
        .merge(bud_avg,    on="country", how="left")
        .merge(exp_avg,    on="country", how="left")
        .merge(trade_avg,  on="country", how="left")
        .merge(comp_avg,   on="country", how="left")
    )

    # Drop rows with any missing values
    return df.dropna()

df = load_and_aggregate()
st.markdown(f"Dataset contains **{len(df)}** countries with complete data.")

# ── Model training ──
features = [
    "active_personnel",
    "total_aircraft",
    "total_tanks",
    "navy_strength",
    "def_budget_pct_gdp",
    "exp_usd",
    "exports_usd",
    "imports_usd",
    "revenue_usd",
    "employees"
]
X = df[features]
y = df["pwr_index"]

model = LinearRegression()
model.fit(X, y)

# ── Predict 2050 ──
df["predicted_pwr_index_2050"] = model.predict(X)

# ── Show coefficients ──
st.subheader("🔍 Feature Influence on Power Index")
coef_df = (
    pd.DataFrame({
        "feature": features,
        "coefficient": model.coef_
    })
    .set_index("feature")
    .sort_values("coefficient", ascending=False)
)
st.bar_chart(coef_df)

# ── Top 10 strongest in 2050 ──
st.header("🏆 Top 10 Countries by Projected Power Index (2050)")
top10 = df.nsmallest(10, "predicted_pwr_index_2050")
fig_top = px.bar(
    top10,
    x="country",
    y="predicted_pwr_index_2050",
    text=top10["predicted_pwr_index_2050"].round(2),
    labels={"predicted_pwr_index_2050":"Projected Power Index (2050)"},
    title="Lower Index ⇒ Stronger Power",
    template="plotly_white"
)
fig_top.update_layout(yaxis={"autorange":"reversed"})
fig_top.update_traces(textposition="outside")
st.plotly_chart(fig_top, use_container_width=True)

# ── Distribution of projections ──
st.subheader("📊 Distribution of Projected Power Index (2050)")
fig_dist = px.histogram(
    df,
    x="predicted_pwr_index_2050",
    nbins=20,
    title="Global Spread of Defence Power Indices by 2050",
    labels={"predicted_pwr_index_2050":"Projected Power Index (2050)"},
    template="plotly_white"
)
st.plotly_chart(fig_dist, use_container_width=True)

# ── India callout ──
st.subheader("🇮🇳 Spotlight: India")
india = df[df["country"] == "India"]
if not india.empty:
    idx = india.index[0]
    india_score = india.at[idx, "predicted_pwr_index_2050"]
    india_rank  = int(df["predicted_pwr_index_2050"].rank(method="min").iloc[idx])
    st.markdown(f"""
    - **Projected Power Index (2050):** {india_score:.2f}  
    - **Global Rank (2050):** {india_rank} / {len(df)}
    """)
else:
    st.info("No projection available for India.")

# ── Comparison table ──
st.subheader("📋 Current (2024) vs Projected (2050) Power Index")
compare = df[["country", "pwr_index", "predicted_pwr_index_2050"]].rename(columns={
    "pwr_index": "Current (2024)",
    "predicted_pwr_index_2050": "Projected (2050)"
})
st.dataframe(compare.round(2), use_container_width=True)

# ── Explanation ──
st.markdown("""
**Model Explanation**  
- We train on **2024** Power Index using a country’s:
  - **Military strength** (personnel, aircraft, tanks, navy)  
  - **Historic averages (2005–2018)** of budget, expenditure, trade, and industry scale  
- We then apply the learned linear relationships to project **2050** indices,  
  assuming these inputs stay constant at their historical averages.  
- A **lower** Power Index signifies **greater** defence strength.
""")
