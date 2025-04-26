import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px

st.set_page_config(page_title="Predictions", layout="wide")
st.title("🔮 Predicting the Future of Defence (2050)")
st.markdown("""
We train a linear model on **2024** data to predict each country’s Power Index in **2050**, 
using only:
- **Military strength** (personnel, aircraft, tanks, navy)
- **Defence budget** (% of GDP)
- **Annual military expenditure** (USD)
- **Exports & imports** (USD)
""")

# —— Load Data —— 
@st.cache_data
def load_data():
    # 1) Base 2024 strength & pwr_index
    base = pd.read_csv("data/2024_military_strength_by_country.csv")
    # Rename columns for clarity
    base = base.rename(columns={
        "active_service_military_manpower": "active_personnel",
        "total_military_aircraft_strength": "total_aircraft",
        "total_combat_tank_strength": "total_tanks",
        "navy_strength":            "navy_strength",
        "pwr_index":                "pwr_index"
    })
    # 2) Defence budget % GDP for 2024
    bud = pd.read_csv("data/Cleaned_Defence_Budget.csv")
    bud_long = (
        bud.melt(id_vars=["Country Name"], var_name="year", value_name="def_budget_pct_gdp")
           .rename(columns={"Country Name":"country"})
           .assign(year=lambda d: d["year"].astype(int))
    )
    bud2024 = bud_long[bud_long["year"]==2024][["country","def_budget_pct_gdp"]]
    # 3) Military expenditure USD for 2024
    exp = pd.read_excel("data/Military_Expenditure_final_rounded.xlsx")
    exp_long = (
        exp.melt(id_vars=["Name"], var_name="year", value_name="exp_usd")
           .rename(columns={"Name":"country"})
           .assign(year=lambda d: d["year"].astype(int))
    )
    exp2024 = exp_long[exp_long["year"]==2024][["country","exp_usd"]]
    # 4) Exports & imports for 2024
    trade = pd.read_csv("data/exports_imports_cleaned.csv")
    trade2024 = trade[trade["year"]==2024][["country","exports_usd","imports_usd"]]

    # Merge all into one DF
    df = (
        base.rename(columns={"country":"country"})
            [["country","active_personnel","total_aircraft","total_tanks","navy_strength","pwr_index"]]
            .merge(bud2024, on="country", how="left")
            .merge(exp2024, on="country", how="left")
            .merge(trade2024, on="country", how="left")
    )

    # Drop any missing
    return df.dropna()

df = load_data()

st.markdown(f"Dataset contains **{len(df)}** countries with complete 2024 data.")

# —— Prepare & train model —— 
features = [
    "active_personnel",
    "total_aircraft",
    "total_tanks",
    "navy_strength",
    "def_budget_pct_gdp",
    "exp_usd",
    "exports_usd",
    "imports_usd"
]
X = df[features]
y = df["pwr_index"]

model = LinearRegression()
model.fit(X, y)

# —— Predict for 2050 —— 
# assume features unchanged from 2024 → predict 2050 index
df["pwr_index_2050"] = model.predict(X)

# —— Top 10 strongest (lowest index) in 2050 —— 
st.header("🏆 Top 10 Countries by Projected Power Index (2050)")
top10 = df.nsmallest(10, "pwr_index_2050")[["country","pwr_index_2050"]]
fig = px.bar(
    top10, x="country", y="pwr_index_2050",
    title="Lower Power Index = Stronger Power",
    text=top10["pwr_index_2050"].round(2),
    labels={"pwr_index_2050":"Projected Power Index (2050)"},
    template="plotly_white"
)
fig.update_traces(textposition="outside")
fig.update_layout(yaxis={"autorange":"reversed"})
st.plotly_chart(fig, use_container_width=True)

# —— Full comparison table —— 
st.subheader("📋 Current vs Projected Power Index")
compare = df[["country","pwr_index","pwr_index_2050"]].rename(columns={
    "pwr_index":"Current (2024)",
    "pwr_index_2050":"Projected (2050)"
})
st.dataframe(compare.round(2), use_container_width=True)

# —— Feature coefficients —— 
st.subheader("🔍 Feature Influence (Regression Coefficients)")
coef_df = pd.DataFrame({
    "feature": features,
    "coefficient": model.coef_
}).set_index("feature").sort_values("coefficient", ascending=False)
st.bar_chart(coef_df)

# —— Explanation —— 
st.markdown("""
**Why these projections?**  
- The model learns how each 2024 metric correlates with current Power Index.  
- We then apply the same relationships to 2050, **holding features constant**.  
- **Stronger military strength** (more personnel, aircraft, tanks, navy) lowers the Index.  
- **Higher defence‐budget share** and **greater expenditure** also lower (improve) the Index.  
- **Exports/imports** reflect logistical and industrial capacity, further improving strength.  

Since we assume no major shifts in these inputs after 2024, the projected ranking for 2050 simply reflects each country’s **relative 2024 strengths** under this linear model.
""")
