import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="🌍 Military Dashboard", layout="wide", page_icon="🌏")

# —— Data loading —— 
@st.cache_data
def load_data():
    return pd.read_csv("data/military_data.csv")

df = load_data()
numeric_cols = df.select_dtypes(include='number').columns.tolist()
country_list = df['country'].unique().tolist()

# —— Header & logo —— 
st.markdown("""
    <h1 style='text-align: center; color: #2E8B57;'>
        🌏 Global Military Power Interactive Dashboard
    </h1>
""", unsafe_allow_html=True)
st.image("https://cdn-icons-png.flaticon.com/512/1035/1035529.png", width=100)

# —— Tabs —— 
tabs = st.tabs([
    "🔍 Country Profile Explorer",
    "📺 Choropleth Map",
    "📊 Compare Countries",
    "🏆 Top-N Ranking Tool",
    "🧠 Correlation Explorer"
])

# — Module 1: Country Profile Explorer —
with tabs[0]:
    st.header("🔍 Country Profile Explorer")
    country = st.selectbox("Select a country:", sorted(country_list))
    row = df[df['country'] == country].iloc[0]

    st.markdown("### 📌 General Information")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Personnel", f"{int(row['Active Personnel']):,}")
        st.metric("Reserve Personnel", f"{int(row['Reserve Personnel']):,}")
        st.metric("Paramilitary", f"{int(row['Paramilitary']):,}")
        st.metric("Defense Budget (USD)", f"${int(row['Defense Budget']):,}")
    with col2:
        st.metric("Total Aircraft Strength", f"{int(row['Total Aircraft Strength']):,}")
        st.metric("Tanks", f"{int(row['Tanks']):,}")
        st.metric("Oil Production (Barrels/day)", f"{int(row['Oil Production']):,}")
        st.metric("External Debt (USD)", f"${int(row['External Debt']):,}")

    st.subheader("📊 Military Metrics Overview (Normalized)")
    bar_attrs = ['Active Personnel', 'Total Aircraft Strength', 'Tanks', 'Oil Production', 'Defense Budget']
    bar_vals = [0 if pd.isna(row.get(a)) else row.get(a) for a in bar_attrs]
    log_vals = [np.log1p(v) for v in bar_vals]
    lo, hi = min(log_vals), max(log_vals)
    norm_vals = [(v - lo)/(hi - lo) if hi>lo else 1 for v in log_vals]

    bar_df = pd.DataFrame({
        'Metric': bar_attrs,
        'Normalized Score': norm_vals,
        'Original Value': bar_vals
    }).sort_values('Normalized Score')

    fig1 = px.bar(
        bar_df, x='Normalized Score', y='Metric', orientation='h',
        title=f"{country} — Normalized Metrics",
        template='plotly_dark',
        color='Metric',
        hover_data=['Original Value']
    )
    st.plotly_chart(fig1, use_container_width=True)


# — Module 2: Choropleth Map —
with tabs[1]:
    st.header("📺 Global Metric Choropleth Map")
    metric = st.selectbox("Select Metric", numeric_cols, key='choropleth')
    fig2 = px.choropleth(
        df,
        locations="country_code",
        color=metric,
        hover_name="country",
        color_continuous_scale="Agsunset",
        projection="natural earth",
        template='plotly_dark',
        title=f"Global Distribution of {metric}"
    )
    st.plotly_chart(fig2, use_container_width=True)


# — Module 3: Compare Countries —
with tabs[2]:
    st.header("📊 Compare Countries")
    sel_countries = st.multiselect("Select Countries", country_list, default=country_list[:5])
    comp_metric = st.selectbox("Select Attribute", numeric_cols, key='compare')
    subset = df[df['country'].isin(sel_countries)]

    fig3 = px.bar(
        subset, x="country", y=comp_metric, color="country",
        title=f"Country Comparison: {comp_metric}",
        text_auto='.2s',
        template='plotly_dark'
    )
    st.plotly_chart(fig3, use_container_width=True)


# — Module 4: Top-N Ranking Tool —
with tabs[3]:
    st.header("🏆 Top-N Countries by Metric")
    rank_metric = st.selectbox("Select Metric", numeric_cols, key='ranking')
    n = st.slider("Select Top N", 5, 30, 10)
    top_df = df.nlargest(n, rank_metric)[['country', rank_metric]]

    st.markdown(f"#### Top {n} Countries by `{rank_metric}`")
    fig4 = px.bar(
        top_df, x=rank_metric, y="country", orientation='h',
        text_auto='.2s',
        template='plotly_dark',
        color_discrete_sequence=['goldenrod']
    )
    fig4.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig4, use_container_width=True)
    st.dataframe(top_df.reset_index(drop=True), use_container_width=True)


# — Module 5: Correlation Explorer —
with tabs[4]:
    st.header("🧠 Correlation Explorer")
    attrs = st.multiselect("Select Attributes", numeric_cols, default=numeric_cols[:8])
    if len(attrs) < 2:
        st.warning("Select at least 2 attributes for correlation.")
    else:
        corr = df[attrs].corr().round(2)
        fig5 = px.imshow(
            corr, text_auto=True,
            color_continuous_scale="RdBu_r",
            labels={'color':'Correlation'},
            title="Correlation Matrix",
            template='plotly_dark'
        )
        fig5.update_xaxes(side="bottom", tickangle=45)
        st.plotly_chart(fig5, use_container_width=True)
