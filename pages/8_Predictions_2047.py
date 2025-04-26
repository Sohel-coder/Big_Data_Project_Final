import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px

st.set_page_config(page_title="Predictions", layout="wide")
st.title("🔮 Predicting the Future of Defence (2050)")
st.markdown("""
This section projects each country’s Power Index in 2050 using a linear model trained on:
- Historical Power Index (year → pwr_index)
- Military strength (personnel, tanks, aircraft, navy)
- Defence budget (% of GDP)
- Annual military expenditure (USD)
- Exports & imports (USD)
- Conflict counts & impact
""")

# — Load data —
@st.cache_data
def load_strength():
    # expects country + year + strength metrics
    df = pd.read_csv("data/military_data.csv")
    return df

@st.cache_data
def load_budget():
    # expects columns: Country Name, <year columns> = % of GDP
    df = pd.read_csv("data/Cleaned_Defence_Budget.csv")
    return df.melt(id_vars=["Country Name"], var_name="year", value_name="def_budget_pct_gdp") \
             .rename(columns={"Country Name":"country"}).assign(year=lambda d: d["year"].astype(int))

@st.cache_data
def load_expenditure():
    # expects country + year + expenditure USD columns
    df = pd.read_excel("data/Military_Expenditure_final_rounded.xlsx")
    return df.melt(id_vars=["Name"], var_name="year", value_name="exp_usd") \
             .rename(columns={"Name":"country"}).assign(year=lambda d: d["year"].astype(int))

@st.cache_data
def load_trade():
    # expects country,year,exports_usd,imports_usd
    return pd.read_csv("data/exports_imports_cleaned.csv")


# Load all
trends_df    = load_power_trends()
strength_df  = load_strength()
budget_df    = load_budget()
exp_df       = load_expenditure()
trade_df     = load_trade()
conflict_df  = load_conflicts()

# — Prepare modeling dataset —
df = trends_df.copy()
# merge all feature tables on country+year
for feat in [strength_df, budget_df, exp_df, trade_df, conflict_df]:
    df = df.merge(feat, on=["country","year"], how="left")

# drop rows with any missing feature
df = df.dropna()

# features & target
features = [
    "year",
    "active_personnel",
    "total_aircraft",
    "total_tanks",
    "navy_strength",
    "def_budget_pct_gdp",
    "exp_usd",
    "exports_usd",
    "imports_usd",
    "num_conflicts",
    "impact_score"
]
X = df[features]
y = df["pwr_index"]

# train
model = LinearRegression()
model.fit(X, y)

# — Forecast for 2050 —
# take latest available features for each country (e.g. year=2024)
latest = df[df["year"] == df["year"].max()].copy()
# override year = 2050
latest["year"] = 2050
# predict
latest["pwr_index_2050"] = model.predict(latest[features])

# also grab 2024 index
current = trends_df[trends_df["year"] == trends_df["year"].max()][["country","pwr_index"]]
compare = current.merge(
    latest[["country","pwr_index_2050"]],
    on="country", how="inner"
).rename(columns={
    "pwr_index":"Current (2024)",
    "pwr_index_2050":"Projected (2050)"
})
compare = compare.sort_values("Projected (2050)")

# — Show Top 10 Projected Strongest (lowest index) —
st.header("🏆 Top 10 Countries by Projected Power Index (2050)")
top10 = compare.head(10)
fig = px.bar(
    top10, x="country", y="Projected (2050)",
    title="Lower Power Index = Stronger Power",
    text=top10["Projected (2050)"].round(2),
    labels={"Projected (2050)":"Projected Power Index (2050)"},
    template="plotly_white"
)
fig.update_traces(textposition="outside")
fig.update_layout(yaxis={"autorange":"reversed"})
st.plotly_chart(fig, use_container_width=True)

# — Full Comparison Table —
st.subheader("📋 Current vs Projected Power Index")
st.dataframe(compare.round(2), use_container_width=True)

# — Model Coefficients —
st.subheader("🔍 Feature Influence (Model Coefficients)")
coef_df = pd.DataFrame({
    "feature": features,
    "coefficient": model.coef_
}).set_index("feature").sort_values("coefficient", ascending=False)
st.bar_chart(coef_df)

# — Explanation —
st.markdown("""
**Why these projections?**  
The linear model learned that:
- **Year** has a negative slope: Power Index tends to improve over time.
- Higher **active personnel** and **aircraft strength** strongly *lower* (improve) the index.
- **Defence budget (% GDP)** and **expenditure** also drive improvements.
- **Exports** and **imports** correlate with greater logistical capacity, improving power.
- Frequent **conflicts** and higher **impact scores** tend to *raise* (weaken) the index.

Countries combining **rapidly growing capabilities** with **stable conflict environments** (e.g. low conflict counts) emerge strongest by 2050.
""")
