import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Military Trade Data Analysis", layout="wide")
st.title("🌍 Military Trade Data Analysis")
st.markdown("""
This dashboard lets you:
1. **Inspect** a single country’s trade balance trend over time.  
2. **Compare** exports & imports for multiple countries.  
3. **Explore** India’s top-10 trading partners in any year.
""")

@st.cache_data
def load_data():
    df = pd.read_csv("data/exports_imports_cleaned.csv")
    # harmonize year
    df['year'] = df['financial_year(start)'].astype(int)
    return df

trade_df = load_data()

# 1️⃣ Single-Country Trade Balance Trend
st.header("1️⃣ Country Trade Balance Trend")
country = st.selectbox(
    "Select a country to inspect its trade balance:",
    sorted(trade_df['country'].unique())
)
country_df = trade_df[trade_df['country'] == country]

fig1 = px.bar(
    country_df,
    x='year',
    y='trade_balance',
    color='trade_balance',
    color_continuous_scale=['#E6F0FA','#4682B4'],
    labels={'trade_balance':'Trade Balance (M USD)','year':'Year'},
    title=f"{country} — Trade Balance Over Time"
)
fig1.update_layout(
    xaxis_tickangle=45,
    plot_bgcolor='#F0F8FF',
    paper_bgcolor='#F0F8FF',
    showlegend=False
)
fig1.update_traces(hovertemplate="<b>Year</b>: %{x}<br><b>Balance</b>: %{y:.2f}M<extra></extra>")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# 2️⃣ Comparative Exports & Imports Over Time
st.header("2️⃣ Comparative Exports & Imports")
countries = st.multiselect(
    "Select 2–5 countries to compare:",
    options=sorted(trade_df['country'].unique()),
    default=sorted(trade_df['country'].unique())[:2]
)
if len(countries) < 2:
    st.warning("Please select at least two countries.")
elif len(countries) > 5:
    st.warning("Please select at most five countries.")
else:
    comp_df = trade_df[trade_df['country'].isin(countries)]
    # Exports
    fig2 = px.line(
        comp_df,
        x='year',
        y='export',
        color='country',
        markers=True,
        labels={'export':'Exports (M USD)','year':'Year'},
        title="Military Exports Over Time"
    )
    fig2.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig2, use_container_width=True)
    # Imports
    fig3 = px.line(
        comp_df,
        x='year',
        y='import',
        color='country',
        markers=True,
        labels={'import':'Imports (M USD)','year':'Year'},
        title="Military Imports Over Time"
    )
    fig3.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig3, use_container_width=True)

    # Summary metrics
    summary = (
        comp_df
        .groupby('country')
        .agg(Exports=('export','sum'), Imports=('import','sum'))
        .assign(Balance=lambda d: d.Exports - d.Imports)
        .reset_index()
    )
    st.subheader("Overall Trade Balances")
    cols = st.columns(len(summary))
    for col, row in zip(cols, summary.itertuples()):
        status = "Surplus" if row.Balance >= 0 else "Deficit"
        col.metric(row.country, f"${row.Balance:,.0f}M", status)
    st.markdown("---")

# 3️⃣ India’s Top-10 Trading Partners
st.header("3️⃣ India’s Top-10 Trading Partners")
year = st.selectbox(
    "Select a year:",
    options=sorted(trade_df['year'].unique()),
    index=sorted(trade_df['year'].unique()).index(2021)
)
india_df = trade_df[(trade_df['country']=='India') & (trade_df['year']==year)]
# assume partner column is named 'partner'
india_summary = (
    india_df
    .groupby('partner')
    .agg(Exports=('export','sum'), Imports=('import','sum'))
    .assign(Total=lambda d: d.Exports + d.Imports)
    .reset_index()
)
top10 = india_summary.nlargest(10, 'Total')

fig4 = px.scatter(
    top10,
    x='partner',
    y='Total',
    size='Total',
    color='Total',
    labels={'partner':'Partner','Total':'Total Trade (M USD)'},
    title=f"India’s Top-10 Partners in {year}",
    color_continuous_scale='Blues'
)
fig4.update_layout(xaxis_tickangle=45)
fig4.update_traces(hovertemplate="<b>%{x}</b><br>Total: %{y:.2f}M<extra></extra>")
st.plotly_chart(fig4, use_container_width=True)
