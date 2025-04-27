import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="🌍 Military Dashboard", layout="wide", page_icon="🌏")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("data/military_data.csv")
    return df

df = load_data()
numeric_cols = df.select_dtypes(include='number').columns.tolist()
country_list = df['country'].unique().tolist()

# Main title
st.markdown("""
    <h1 style='text-align: center; color: #2E8B57;'>
        🌏 Global Military Power Interactive Dashboard
    </h1>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1035/1035529.png", width=100)
module = st.sidebar.radio("Choose a Module", [
    "Country Profile Explorer",
    "Choropleth Map",
    "Compare Countries",
    "Top-N Ranking Tool",
    "Correlation Explorer"
])

st.sidebar.markdown("<hr style='border:1px solid #ccc;'>", unsafe_allow_html=True)

# Module 1: Country Profile Explorer
if module == "Country Profile Explorer":
    st.header("🔍 Country Profile Explorer")
        
    country = st.selectbox("Select a country:", sorted(df['country'].unique()))
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

    # Bar Chart for selected attributes (Normalized for better comparison)
    st.subheader("📊 Military Metrics Overview (Normalized Bar Chart)")
    bar_attrs = ['Active Personnel', 'Total Aircraft Strength', 'Tanks', 'Oil Production', 'Defense Budget']

    # Extract values safely
    # Extract values safely
    bar_values = [0 if pd.isna(row.get(attr)) else row.get(attr) for attr in bar_attrs]

    # Normalize using log scale
    log_values = [np.log1p(val) for val in bar_values]
    min_log = min(log_values)
    max_log = max(log_values)
    if max_log != min_log:
        normalized_values = [(val - min_log) / (max_log - min_log) for val in log_values]
    else:
        normalized_values = [1 for _ in log_values]

    bar_df = pd.DataFrame({
        'Metric': bar_attrs,
        'Normalized Value': normalized_values,
        'Original Value': bar_values
    }).sort_values(by='Normalized Value', ascending=True)

    fig = px.bar(
        bar_df,
        x='Normalized Value',
        y='Metric',
        orientation='h',
        labels={'Normalized Value': 'Normalized Score', 'Metric': 'Military Metric'},
        title=f"{country} - Normalized Military Metrics",
        template='plotly_dark',
        color='Metric',
        color_discrete_sequence=px.colors.qualitative.Set2,
        hover_data=['Original Value']
    )

    st.plotly_chart(fig, use_container_width=True)
# Module 2: Choropleth Map
elif module == "Choropleth Map":
    st.subheader("📺 Global Metric Choropleth Map")
    metric = st.selectbox("Select Metric", numeric_cols)
    fig = px.choropleth(
        df,
        locations="country_code",
        color=metric,
        hover_name="country",
        color_continuous_scale="Agsunset",
        projection="natural earth",
        template='plotly_dark',
        title=f"Global Distribution of {metric}"
    )
    st.plotly_chart(fig, use_container_width=True)

# Module 3: Compare Countries
elif module == "Compare Countries":
    st.subheader("📊 Compare Countries")
    countries = st.multiselect("Select Countries", country_list, default=country_list[:5])
    metric = st.selectbox("Select Attribute to Compare", numeric_cols)
    subset = df[df['country'].isin(countries)]

    fig = px.bar(
        subset,
        x="country",
        y=metric,
        color="country",
        title=f"Comparison on {metric}",
        text_auto='.2s',
        template='plotly_dark',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig, use_container_width=True)

# Module 4: Top-N Ranking Tool
elif module == "Top-N Ranking Tool":
    st.subheader("🏆 Top-N Countries by Metric")
    metric = st.selectbox("Select Metric", numeric_cols, key='ranking_metric')
    n = st.slider("Select Top N", 5, 30, 10)
    top_df = df.nlargest(n, metric)[['country', metric]]

    st.markdown(f"#### Top {n} Countries by `{metric}`")
    fig = px.bar(
        top_df,
        x=metric,
        y="country",
        orientation='h',
        text_auto='.2s',
        template='plotly_dark',
        color_discrete_sequence=['goldenrod']
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_df.reset_index(drop=True), use_container_width=True)

# Module 5: Correlation Explorer
elif module == "Correlation Explorer":
    st.markdown("## 🧠 Correlation Heatmap of Military Metrics (Interactive)")
    selected_attrs = st.multiselect("Select Attributes", numeric_cols, default=numeric_cols[:8])

    if len(selected_attrs) >= 2:
        corr = df[selected_attrs].corr().round(2)
        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            aspect="auto",
            labels=dict(color="Correlation"),
        )
        fig.update_layout(
            title="Correlation Matrix",
            title_font_size=22,
            paper_bgcolor="#222",
            plot_bgcolor="#111",
            font_color="white",
            margin=dict(l=40, r=40, t=60, b=40),
        )
        fig.update_xaxes(side="bottom", tickangle=45, showgrid=False)
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least 2 attributes to show correlation heatmap.")
