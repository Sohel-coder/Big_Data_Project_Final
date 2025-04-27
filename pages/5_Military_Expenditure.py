import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- App config and title ---
st.set_page_config(page_title="Military Expenditure Dashboard", layout="wide")
st.title("🌍 Military Expenditure Visualization (1960–2018)")

# ─── INJECT GLOBAL CSS ─────────────────────────────────────────────────────────
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


# --- Load and filter data ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/Military_Expenditure_final_rounded.xlsx")
    df = df[df['Indicator Name'] == 'Military expenditure (current USD)']
    return df

# Load dataframe
df = load_data()

# Validate structure
if df.columns[2] != "Type":
    st.error("❌ Third column must be 'Type'.")
    st.stop()

df = df[df["Type"] == "Country"]
if df.empty:
    st.error("❌ No entries with Type='Country'.")
    st.stop()


years_all = [str(y) for y in range(1960, 2019)]
all_countries = sorted(df['Name'].unique())
default_countries = ['United States', 'China', 'Russian Federation']

# --- Filters on main page ---
st.subheader("Filters")
countries = st.multiselect(
    "Select countries:",
    options=all_countries,
    default=[c for c in default_countries if c in all_countries]
)
year_range = st.slider(
    "Select year range:",
    1960, 2018,
    (1990, 2018)
)

# --- Selected Countries Time Series ---
if countries:
    df_sel = df[df['Name'].isin(countries)]
    df_sel = df_sel[['Name'] + years_all].set_index('Name').T
    df_sel.index = df_sel.index.astype(int)
    df_sel = df_sel.loc[year_range[0]:year_range[1]]

    st.subheader("📈 Expenditure Over Time")
    fig = go.Figure()
    for country in df_sel.columns:
        fig.add_trace(go.Scatter(
            x=df_sel.index,
            y=df_sel[country] / 1e9,
            mode='lines+markers',
            name=country,
            meta=country,
            marker=dict(size=8, opacity=0),
            hovertemplate=(
                "Country: %{meta}<br>"
                "Year: %{x}<br>"
                "Exp: %{y:.2f} Billion USD<extra></extra>"
            ),
            hoverlabel=dict(bgcolor='black', font_color='white')
        ))
    fig.update_layout(
        template='plotly_dark',
        hovermode='closest',
        xaxis=dict(title='Year', tickmode='array', tickvals=[y for y in df_sel.index if y % 5 == 0]),
        yaxis=dict(title='Expenditure (Billion USD)')
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Single-Year Comparison")
    year = st.selectbox("Select a year:", df_sel.index[::-1])
    values = df_sel.loc[year] / 1e9
    fig2 = go.Figure(go.Bar(
        x=values.index,
        y=values.values,
        marker_color='skyblue',
        hovertemplate="Country: %{x}<br>Exp: %{y:.2f} Billion USD<extra></extra>",
        hoverlabel=dict(bgcolor='black', font_color='white')
    ))
    fig2.update_layout(
        template='plotly_dark',
        yaxis_title='Expenditure (Billion USD)',
        title=f'Year {year}'
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Top/Bottom 5 Analysis on main page ---
st.subheader("💰 Top/Bottom 5 Spenders")
range_tb = st.slider("Select range for Top/Bottom analysis:", 1960, 2018, (1960, 2018))
cols_tb = [str(y) for y in range(range_tb[0], range_tb[1] + 1)]
sum_df = df[['Name'] + cols_tb].set_index('Name').sum(axis=1)

# Top 5 and Bottom 5
top5 = sum_df.nlargest(5)
bot5 = sum_df[sum_df > 0].nsmallest(5)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Top 5**")
    fig_top = go.Figure(go.Bar(
        x=top5.index,
        y=top5.values / 1e9,
        marker_color='green',
        hovertemplate="Country: %{x}<br>Total: %{y:.2f} Billion USD<extra></extra>",
        hoverlabel=dict(bgcolor='black', font_color='white')
    ))
    fig_top.update_layout(template='plotly_dark', yaxis_title='Total (Billion USD)')
    st.plotly_chart(fig_top, use_container_width=True)
with col2:
    st.markdown("**Bottom 5**")
    fig_bot = go.Figure(go.Bar(
        x=bot5.index,
        y=bot5.values / 1e9,
        marker_color='red',
        hovertemplate="Country: %{x}<br>Total: %{y:.2f} Billion USD<extra></extra>",
        hoverlabel=dict(bgcolor='black', font_color='white')
    ))
    fig_bot.update_layout(template='plotly_dark', yaxis_title='Total (Billion USD)')
    st.plotly_chart(fig_bot, use_container_width=True)

# --- Global Choropleth on main page ---
st.subheader("🗺 Global Map View")
year_map = st.slider("Select map year:", 1960, 2018, 2018)
map_df = df[['Name', str(year_map)]].rename(columns={str(year_map): 'Value'})
map_df = map_df[map_df['Value'] > 0]
fig_map = px.choropleth(
    map_df,
    locations='Name',
    locationmode='country names',
    color='Value',
    color_continuous_scale='YlOrRd',
    projection='orthographic',
    hover_name='Name',
    hover_data={'Value': ':.2f'},
)
fig_map.update_traces(
    hovertemplate="Country: %{location}<br>Value: %{z:.2f} USD<extra></extra>",
    hoverlabel=dict(bgcolor='black', font_color='white')
)
fig_map.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig_map, use_container_width=True)
