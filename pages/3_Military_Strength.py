import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(page_title="Military Strength", layout="wide")

st.title("Military Strength Comparison (2024)")
st.markdown(
    """
    This section provides insights into the military strength of various countries in 2024.
    You can compare different countries based on various military metrics.
    Use the sidebar to select countries and metrics for a more tailored analysis.
    """
)


# Helper function to ensure dataframes are Arrow-compatible

def make_arrow_compatible(df):
    """Convert all columns to string to avoid Arrow conversion issues."""
    df_copy = df.copy()
    for col in df_copy.columns:
        if df_copy[col].dtype == 'object':
            df_copy[col] = df_copy[col].astype(str)
        elif col != 'Year' and col != 'Metric':
            try:
                df_copy[col] = df_copy[col].apply(
                    lambda x: "{:,}".format(int(x)) if isinstance(x, (int, float)) and abs(x) >= 1 and not pd.isna(x)
                    else (f"{x:.2f}" if isinstance(x, (int, float)) and not pd.isna(x)
                          else ("N/A" if pd.isna(x) else str(x)))
                )
            except:
                df_copy[col] = df_copy[col].astype(str)
    return df_copy

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/2024_military_strength_by_country.csv")

military_strength = load_data()



# Country selection
countries = sorted(military_strength['country'].unique().tolist())
num_countries = st.slider("Number of countries to compare:", min_value=2, max_value=5, value=2)
default = []
for c in ['United States','China','Russia','India']:
    if c in countries and len(default) < num_countries:
        default.append(c)
while len(default) < num_countries:
    for c in countries:
        if c not in default:
            default.append(c)
            break
selected_countries = st.multiselect(
    "Select countries to compare:", options=countries, default=default[:num_countries]
)

# Validate selection
if len(selected_countries) < 2:
    st.warning("Please select at least 2 countries for comparison.")
elif len(selected_countries) > 5:
    st.warning("Please select at most 5 countries for comparison.")
else:
    # Prepare comparison table
    metrics = {
        'Population':'total_national_populations',
        'Active Military':'active_service_military_manpower',
        'Reserve Forces':'active_service_reserve_components',
        'Defense Budget':'national_annual_defense_budgets',
        'Fighter Aircraft':'total_fighter/interceptor_aircraft_strength',
        'Attack Aircraft':'total_attack_aircraft_strength',
        'Helicopters':'total_helicopter_strength',
        'Tanks':'total_combat_tank_strength',
        'Navy Ships':'navy_strength',
        'Power Index (lower is better)':'pwr_index'
    }
    data = []
    for label, m in metrics.items():
        row = {'Metric': label}
        for country in selected_countries:
            val = military_strength.loc[military_strength['country']==country, m]
            if not val.empty:
                v = val.iloc[0]
                if pd.api.types.is_number(v):
                    row[country] = f"{int(v):,}" if v>=1 else str(v)
                else:
                    row[country] = str(v)
            else:
                row[country] = "N/A"
        data.append(row)
    df = pd.DataFrame(data)
    st.dataframe(make_arrow_compatible(df), use_container_width=True)

    # Detailed category comparison
    category_options = ['Air Power','Land Forces','Naval Power','Economic Factors']
    selected_cat = st.selectbox("Select Category for Detailed Comparison:", category_options)
    cat_metrics = {
        'Air Power':[ 'total_military_aircraft_strength','total_fighter/interceptor_aircraft_strength','total_attack_aircraft_strength','total_helicopter_strength'],
        'Land Forces':[ 'active_service_military_manpower','total_combat_tank_strength'],
        'Naval Power':['navy_strength','navy_submarine_strength'],
        'Economic Factors':['national_annual_defense_budgets']
    }[selected_cat]
    chart_data = []
    for m in cat_metrics:
        for country in selected_countries:
            v = military_strength.loc[military_strength['country']==country, m]
            chart_data.append({'Metric': m.replace('_',' ').title(),'Country':country,'Value': float(v.iloc[0]) if not v.empty else 0})
    cdf = pd.DataFrame(chart_data)
    st.subheader(f"Detailed Comparison: {selected_cat}")
    fig = px.bar(cdf, x='Metric', y='Value', color='Country', barmode='group', title=selected_cat)
    st.plotly_chart(fig, use_container_width=True)

    # Radar chart
    st.subheader("Overall Military Capability Comparison")
    radar_metrics = ['active_service_military_manpower','total_military_aircraft_strength','total_combat_tank_strength','navy_strength','national_annual_defense_budgets']
    radar_labels = ['Personnel','Aircraft','Tanks','Navy','Budget']
    values = {country: [] for country in selected_countries}
    for m in radar_metrics:
        vals = military_strength.set_index('country')[m].reindex(selected_countries).fillna(0)
        maxv = vals.max() or 1
        for country in selected_countries:
            values[country].append(vals[country]/maxv)
    angles = np.linspace(0, 2*np.pi, len(radar_labels), endpoint=False).tolist()
    angles += angles[:1]
    radar_fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    for country in selected_countries:
        vals = values[country] + values[country][:1]
        ax.plot(angles, vals, label=country)
        ax.fill(angles, vals, alpha=0.1)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(radar_labels)
    ax.legend(loc='upper right')
    st.pyplot(radar_fig)
