import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import country_converter as coco

st.set_page_config(page_title="World Map", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    """Load military strength data from CSV."""
    return pd.read_csv("data/2024_military_strength_by_country.csv")

military_strength = load_data()

st.title("Interactive Global Military Power Map")


st.write("""
Hover over countries to see key military statistics. The map displays military power data 
for countries around the world. Colors indicate relative military strength based on the Power Index.
""")

@st.cache_data
def prepare_map_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for choropleth: ISO codes, power score, and formatted metrics."""
    map_data = df.copy()
    # ISO3 codes
    map_data['iso_alpha'] = coco.convert(names=map_data['country'].tolist(), to='ISO3')
    # Invert pwr_index to get power_score
    map_data['power_score'] = 1 - pd.to_numeric(map_data['pwr_index'], errors='coerce')
    # Numeric columns to convert
    numeric_cols = [
        'total_national_populations',
        'active_service_military_manpower',
        'total_military_aircraft_strength',
        'total_combat_tank_strength',
        'navy_strength',
        'national_annual_defense_budgets'
    ]
    for col in numeric_cols:
        if col in map_data.columns:
            map_data[col] = pd.to_numeric(map_data[col], errors='coerce')
    # Formatted strings for hover
    map_data['formatted_population'] = map_data['total_national_populations'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")
    map_data['formatted_military'] = map_data['active_service_military_manpower'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")
    map_data['formatted_aircraft'] = map_data['total_military_aircraft_strength'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")
    map_data['formatted_tanks'] = map_data['total_combat_tank_strength'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")
    map_data['formatted_navy'] = map_data['navy_strength'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")
    map_data['formatted_budget'] = map_data['national_annual_defense_budgets'].apply(lambda x: f"${int(x):,}" if pd.notna(x) else "N/A")
    return map_data

map_data = prepare_map_data(military_strength)

# Metric selection
metric_options = [
    "Military Power Index",
    "Population",
    "Active Military",
    "Aircraft",
    "Tanks",
    "Naval Vessels",
    "Defense Budget"
]
selected_metric = st.selectbox("Select a metric to display:", metric_options)

# Map configuration based on metric
metric_map = {
    "Military Power Index": dict(
        color="power_score", scale=px.colors.sequential.Reds, title="Global Military Power Index (2024)",
        hover={'formatted_population':'Population','formatted_military':'Military','pwr_index':'Power Index'}
    ),
    "Population": dict(
        color="total_national_populations", scale=px.colors.sequential.Viridis, title="National Populations",
        hover={'formatted_population':'Population','formatted_military':'Military','pwr_index':'Power Index'}
    ),
    "Active Military": dict(
        color="active_service_military_manpower", scale=px.colors.sequential.Greens, title="Active Military Personnel",
        hover={'formatted_military':'Active Military','formatted_population':'Population','pwr_index':'Power Index'}
    ),
    "Aircraft": dict(
        color="total_military_aircraft_strength", scale=px.colors.sequential.Blues, title="Military Aircraft",
        hover={'formatted_aircraft':'Aircraft','formatted_military':'Military','pwr_index':'Power Index'}
    ),
    "Tanks": dict(
        color="total_combat_tank_strength", scale=px.colors.sequential.Oranges, title="Combat Tanks",
        hover={'formatted_tanks':'Tanks','formatted_military':'Military','pwr_index':'Power Index'}
    ),
    "Naval Vessels": dict(
        color="navy_strength", scale=px.colors.sequential.Purples, title="Naval Vessels",
        hover={'formatted_navy':'Naval Vessels','formatted_military':'Military','pwr_index':'Power Index'}
    ),
    "Defense Budget": dict(
        color="national_annual_defense_budgets", scale=px.colors.sequential.Plasma, title="Defense Budget",
        hover={'formatted_budget':'Budget','formatted_military':'Military','pwr_index':'Power Index'}
    )
}
cfg = metric_map[selected_metric]

# Draw choropleth
fig = px.choropleth(
    map_data,
    locations="iso_alpha",
    color=cfg['color'],
    hover_name="country",
    hover_data=cfg['hover'],
    color_continuous_scale=cfg['scale'],
    title=cfg['title']
)
fig.update_layout(geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'))
st.plotly_chart(fig, use_container_width=True)

# Map insights
st.subheader("Map Insights")
st.markdown("""
- Darker colors mean stronger values for the chosen metric
- Hover over any country to see detailed stats
- Use the dropdown to switch between metrics
""")

# Regional analysis
st.header("Regional Military Power Analysis")
regions = {
    'North America': ['United States','Canada','Mexico'],
    'Europe': ['United Kingdom','France','Germany','Italy','Spain','Poland','Ukraine','Turkey'],
    'Asia': ['China','India','Japan','South Korea','Pakistan','Iran','Israel','Saudi Arabia'],
    'South America': ['Brazil','Argentina','Chile','Colombia','Peru'],
    'Africa': ['Egypt','South Africa','Nigeria','Algeria','Morocco'],
    'Oceania': ['Australia','New Zealand']
}

# Summarize region totals
regional = []
for region, countries in regions.items():
    df = map_data[map_data['country'].isin(countries)]
    if df.empty: continue
    regional.append({
        'Region': region,
        'Military Power': df['power_score'].sum(),
        'Active Military': df['active_service_military_manpower'].sum(),
        'Aircraft': df['total_military_aircraft_strength'].sum(),
        'Tanks': df['total_combat_tank_strength'].sum(),
        'Naval Vessels': df['navy_strength'].sum(),
        'Defense Budget': df['national_annual_defense_budgets'].sum()
    })
regional_df = pd.DataFrame(regional)

# Tabs for visualizations
tab1, tab2, tab3 = st.tabs(["Regional Power","Capabilities","Budgets"])

with tab1:
    fig1 = px.pie(regional_df, values='Military Power', names='Region', title='Regional Power Distribution')
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = go.Figure()
    for _, row in regional_df.iterrows():
        fig2.add_trace(go.Scatterpolar(
            r=[row['Active Military'], row['Aircraft'], row['Tanks'], row['Naval Vessels']],
            theta=['Active','Aircraft','Tanks','Naval'],
            fill='toself', name=row['Region']
        ))
    fig2.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, title='Military Capabilities by Region')
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig3 = px.bar(regional_df, x='Region', y='Defense Budget', title='Regional Defense Budgets')
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Regional Analysis Insights")
st.markdown("""
1. Asia & North America lead in overall power  
2. Different regions specialize in different assets  
3. Budgets largely correlate with power scores
""")
