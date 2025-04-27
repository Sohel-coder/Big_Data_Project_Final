import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="🌍 Military Dashboard", layout="wide", page_icon="🌏")

st.markdown(
    """
    <style>
    /* Full-screen war-scene background */
    .stApp {
      background: url('https://t4.ftcdn.net/jpg/03/49/86/71/240_F_349867133_a2Upqgg99LIDvsGbR4Of3a0bXCwqzrAQ.jpg')
                  no-repeat center center fixed;
      background-size: cover;
    }
    /* Translucent sidebar */
    [data-testid="stSidebar"] {
      background-color: rgba(0, 0, 0, 0.6);
    }
    /* Centered hero text */
    .css-1lcbmhc {
      text-align: center !important;
      padding: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("military_data.csv")
    return df

df = load_data()
numeric_cols = df.select_dtypes(include='number').columns.tolist()
country_list = df['country'].unique().tolist()

# Main title
st.markdown("""
    <h1 style='text-align: center; color: #2E8B57;'>
        🌏 Global Military Power Visualization
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
# Module 1: Country Profile Explorer
if module == "Country Profile Explorer":
    st.header("🔍 Country Profile Explorer")

    # Default to India
    country = st.selectbox("Select a country:", sorted(df['country'].unique()), index=sorted(df['country'].unique()).index('India'))
    row = df[df['country'] == country].iloc[0]

    # General Information Section
    st.markdown("### 📌 General Information")

    # Define attractive colors
    col1, col2 = st.columns(2)
    
    # First column: Military Personnel
    with col1:
        st.markdown("<h3 style='color:#4CAF50;'>🪖 Military Personnel</h3>", unsafe_allow_html=True)
        st.markdown(f"Active Personnel: <span style='color:#009688;'>{int(row['Active Personnel']):,}</span><br><i style='color:#888;'>Number of active military members.</i>", unsafe_allow_html=True)
        st.markdown(f"Reserve Personnel: <span style='color:#009688;'>{int(row['Reserve Personnel']):,}</span><br><i style='color:#888;'>Number of personnel on reserve duty.</i>", unsafe_allow_html=True)
        st.markdown(f"Paramilitary: <span style='color:#009688;'>{int(row['Paramilitary']):,}</span><br><i style='color:#888;'>Forces performing military duties but not part of the regular army.</i>", unsafe_allow_html=True)

    # Second column: Military Assets
    with col2:
        st.markdown("<h3 style='color:#2196F3;'>✈ Military Assets</h3>", unsafe_allow_html=True)
        st.markdown(f"Total Aircraft Strength: <span style='color:#009688;'>{int(row['Total Aircraft Strength']):,}</span><br><i style='color:#888;'>Number of aircraft in the military's inventory.</i>", unsafe_allow_html=True)
        st.markdown(f"Tanks: <span style='color:#009688;'>{int(row['Tanks']):,}</span><br><i style='color:#888;'>Number of tanks in military service.</i>", unsafe_allow_html=True)
        st.markdown(f"Oil Production (Barrels/day): <span style='color:#009688;'>{int(row['Oil Production']):,}</span><br><i style='color:#888;'>Daily oil production (in barrels) of the country.</i>", unsafe_allow_html=True)

    # Economic Overview Section
    st.markdown("### 💰 Economic Overview")

    col3, col4 = st.columns(2)

    # Economic Data (Defense Budget and External Debt)
    with col3:
        st.markdown("<h3 style='color:#FFC107;'>💵 Economic Overview</h3>", unsafe_allow_html=True)
        st.markdown(f"Defense Budget (USD): <span style='color:#009688;'>${int(row['Defense Budget']):,}</span><br><i style='color:#888;'>Amount allocated for national defense spending.</i>", unsafe_allow_html=True)

    with col4:
        st.markdown(f"External Debt (USD): <span style='color:#009688;'>${int(row['External Debt']):,}</span><br><i style='color:#888;'>Total debt the country owes to foreign entities.</i>", unsafe_allow_html=True)

  
    


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

    st.markdown(f"#### Top {n} Countries by {metric}")
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
    st.markdown("## 🧠 *Correlation Heatmap of Military Metrics (Interactive)*")

    # Select only the first 7 initial attributes for a focused correlation view
    initial_attributes = [
        "Active Personnel", "Defense Budget", "Oil Production", "Tanks", "Total Aircraft Strength", 
        "Submarines", "Reserve Personnel"
    ]
    
    selected_attrs = st.multiselect("Select Attributes", initial_attributes, default=initial_attributes)

    # Only proceed if 2 or more attributes are selected
    if len(selected_attrs) >= 2:
        corr = df[selected_attrs].corr().round(2)

        # Create the correlation heatmap with a larger size and cooler style
        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="Viridis",  # Choose a cool, visually appealing color palette
            aspect="auto",  # Ensures the aspect ratio adjusts automatically
            labels=dict(color="Correlation"),
        )

        # Update layout for a more visually appealing and engaging design
        fig.update_layout(
            title="Correlation Matrix of Selected Metrics",
            title_font_size=26,
            title_font_color="white",  # White font color for better readability
            paper_bgcolor="#1E1E1E",  # Dark background for a sleek look
            plot_bgcolor="#2B2B2B",  # Slightly lighter plot background
            font_color="white",
            font=dict(family="Arial, sans-serif", size=14),  # Font style and size for readability
            margin=dict(l=40, r=40, t=60, b=40),
        )

        # Style x and y axes with better grid and font settings
        fig.update_xaxes(
            side="bottom", 
            tickangle=45, 
            showgrid=True, 
            tickfont=dict(size=12, color="white")
        )
        fig.update_yaxes(
            tickfont=dict(size=12, color="white"),
            showgrid=True
        )

        # Add a cool title and make the color scale more vibrant
        st.plotly_chart(fig, use_container_width=True)


    else:
        st.warning("Please select at least two attributes to compute the correlation matrix.")
