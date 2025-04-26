import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Military Strength", layout="wide")

st.title("🎖️ Military Strength Comparison (2024)")
st.markdown(
    """
    This section provides insights into the military strength of various countries in 2024.
    You can compare different countries based on various military metrics.
    Use the sidebar to select countries and metrics for tailored analysis.
    """
)

# Helper function to ensure Arrow compatibility
def make_arrow_compatible(df):
    df_copy = df.copy()
    for col in df_copy.columns:
        if df_copy[col].dtype == 'object':
            df_copy[col] = df_copy[col].astype(str)
        elif col not in ['Year', 'Metric']:
            df_copy[col] = df_copy[col].apply(
                lambda x: "{:,}".format(int(x)) if isinstance(x, (int, float)) and abs(x) >= 1 and not pd.isna(x)
                else (f"{x:.2f}" if isinstance(x, (int, float)) and not pd.isna(x)
                      else ("N/A" if pd.isna(x) else str(x)))
            )
    return df_copy

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/2024_military_strength_by_country.csv")

military_strength = load_data()

# Country selection
countries = sorted(military_strength['country'].unique().tolist())
num_countries = st.slider("Number of countries to compare:", min_value=2, max_value=5, value=2)
default_countries = ['United States', 'China', 'Russia', 'India']
default = [c for c in default_countries if c in countries][:num_countries]
while len(default) < num_countries:
    default.append(next(c for c in countries if c not in default))

selected_countries = st.multiselect("Select countries:", options=countries, default=default)

if len(selected_countries) < 2:
    st.warning("Select at least 2 countries.")
else:
    # Metrics for comparison
    metrics = {
        'Population': 'total_national_populations',
        'Active Military': 'active_service_military_manpower',
        'Reserve Forces': 'active_service_reserve_components',
        'Defense Budget': 'national_annual_defense_budgets',
        'Fighter Aircraft': 'total_fighter/interceptor_aircraft_strength',
        'Attack Aircraft': 'total_attack_aircraft_strength',
        'Helicopters': 'total_helicopter_strength',
        'Tanks': 'total_combat_tank_strength',
        'Navy Ships': 'navy_strength',
        'Power Index (lower is better)': 'pwr_index'
    }

    data = []
    for label, m in metrics.items():
        row = {'Metric': label}
        for country in selected_countries:
            val = military_strength.loc[military_strength['country'] == country, m]
            row[country] = "{:,}".format(int(val.iloc[0])) if not val.empty and pd.notna(val.iloc[0]) else "N/A"
        data.append(row)

    df = pd.DataFrame(data)
    st.dataframe(make_arrow_compatible(df), use_container_width=True)

    # Detailed category comparison
    categories = ['Air Power', 'Land Forces', 'Naval Power', 'Economic Factors']
    selected_cat = st.selectbox("Select Category:", categories)

    cat_metrics = {
        'Air Power': ['total_military_aircraft_strength', 'total_fighter/interceptor_aircraft_strength', 'total_attack_aircraft_strength', 'total_helicopter_strength'],
        'Land Forces': ['active_service_military_manpower', 'total_combat_tank_strength'],
        'Naval Power': ['navy_strength', 'navy_submarine_strength'],
        'Economic Factors': ['national_annual_defense_budgets']
    }[selected_cat]

    chart_data = []
    for m in cat_metrics:
        for country in selected_countries:
            v = military_strength.loc[military_strength['country'] == country, m]
            val = float(v.iloc[0]) if not v.empty else 0
            chart_data.append({'Metric': m.replace('_', ' ').title(), 'Country': country, 'Value': val})

    cdf = pd.DataFrame(chart_data)

    st.subheader(f"📊 Detailed Comparison: {selected_cat}")
    fig = px.bar(cdf, x='Metric', y='Value', color='Country', barmode='group', title=f"{selected_cat} Comparison")
    st.plotly_chart(fig, use_container_width=True)

    # Radar chart
    st.subheader("🛡️ Overall Capability Radar")
    radar_metrics = ['active_service_military_manpower', 'total_military_aircraft_strength', 'total_combat_tank_strength', 'navy_strength', 'national_annual_defense_budgets']
    radar_labels = ['Personnel', 'Aircraft', 'Tanks', 'Navy', 'Budget']
    angles = np.linspace(0, 2 * np.pi, len(radar_labels), endpoint=False).tolist()
    angles += angles[:1]

    radar_fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    for country in selected_countries:
        vals = [military_strength.loc[military_strength['country'] == country, m].iloc[0] for m in radar_metrics]
        max_vals = [military_strength[m].max() or 1 for m in radar_metrics]
        normalized_vals = [vals[i] / max_vals[i] for i in range(len(vals))]
        normalized_vals += normalized_vals[:1]
        ax.plot(angles, normalized_vals, label=country)
        ax.fill(angles, normalized_vals, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(radar_labels)
    ax.legend(loc='upper right')
    st.pyplot(radar_fig)
