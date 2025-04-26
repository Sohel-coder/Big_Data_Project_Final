import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from matplotlib.ticker import StrMethodFormatter  # for x-axis formatting

st.set_page_config(page_title="Military Expenditure", layout="wide")

st.title("🌍 Military Expenditure Visualization (1960–2018)")
st.markdown(
    """
    This section provides insights into military expenditure trends across various countries 
    from 1960 to 2018. You can visualize the data through line charts, bar charts, 
    and a global map via the tabs below.
    """
)

@st.cache_data
def load_data():
    df = pd.read_excel("data/Military_Expenditure_final_rounded.xlsx")
    df = df[df['Indicator Name'] == 'Military expenditure (current USD)']
    return df

df = load_data()

# sanity checks
if df.columns[2] != "Type" or df["Type"].iloc[0] != "Country":
    st.error("❌ Data must have a third column named 'Type' with value 'Country'.")
    st.stop()

years_all = [str(y) for y in range(1960, 2019)]
all_countries = sorted(df['Name'].unique())
default_countries = ['United States', 'China', 'Russian Federation']

# create three tabs
tab1, tab2, tab3 = st.tabs([
    "📈 Custom Trends",
    "💰 Top & Bottom Spenders",
    "🗺️ Global Map"
])

with tab1:
    st.header("Custom Expenditure Trends")
    countries = st.multiselect(
        "Select countries to visualize:",
        options=all_countries,
        default=[c for c in default_countries if c in all_countries]
    )
    year_range = st.slider(
        "Select year range:",
        min_value=1960, max_value=2018, value=(1990, 2018)
    )

    if countries:
        df_sel = (
            df[df['Name'].isin(countries)]
             [['Name'] + years_all]
             .set_index('Name')
             .transpose()
        )
        df_sel.index = df_sel.index.astype(int)
        df_sel = df_sel.loc[year_range[0]:year_range[1]]

        st.subheader("Line Chart: Expenditure Over Time")
        st.line_chart(df_sel)

        st.subheader("Bar Chart: Single Year Comparison")
        year_choice = st.selectbox(
            "Pick a year to compare:",
            options=list(df_sel.index)[::-1]
        )
        st.bar_chart(df_sel.loc[year_choice])

with tab2:
    st.header("Top & Bottom 5 Spenders")
    # Top 5
    st.subheader("🔝 Top 5 Countries by Total Expenditure")
    top_range = st.slider(
        "Year span for Top 5 analysis:",
        min_value=1960, max_value=2018, value=(1960, 2018),
        key="top_span"
    )
    top_years = [str(y) for y in range(top_range[0], top_range[1] + 1)]
    df_total = df[['Name'] + top_years].set_index('Name')
    top5 = df_total.sum(axis=1).nlargest(5)
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(top5.index, top5.values, color='green')
    ax1.set_title(f"Top 5 Spenders ({top_range[0]}–{top_range[1]})")
    ax1.set_ylabel("Total Expenditure (USD)")
    ax1.set_xticklabels(top5.index, rotation=30)
    ax1.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    st.pyplot(fig1)

    st.subheader("📈 Trends for Top 5")
    df_top5 = df[df['Name'].isin(top5.index)][['Name'] + years_all]\
                 .set_index('Name').transpose()
    df_top5.index = df_top5.index.astype(int)
    st.line_chart(df_top5.loc[top_range[0]:top_range[1]])

    # Bottom 5
    st.markdown("---")
    st.subheader("🔻 Bottom 5 Non-Zero Spenders")
    bottom_range = st.slider(
        "Year span for Bottom 5 analysis:",
        min_value=1960, max_value=2018, value=(1970, 2018),
        key="bottom_span"
    )
    bottom_years = [str(y) for y in range(bottom_range[0], bottom_range[1] + 1)]
    df_bottom = df[['Name'] + bottom_years].set_index('Name')
    bottom5 = df_bottom.sum(axis=1)
    bottom5 = bottom5[bottom5 > 0].nsmallest(5)
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(bottom5.index, bottom5.values, color='red')
    ax2.set_title(f"Bottom 5 Spenders ({bottom_range[0]}–{bottom_range[1]})")
    ax2.set_ylabel("Total Expenditure (USD)")
    ax2.set_xticklabels(bottom5.index, rotation=30)
    ax2.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    st.pyplot(fig2)

    st.subheader("📈 Trends for Bottom 5")
    df_bot5 = df[df['Name'].isin(bottom5.index)][['Name'] + years_all]\
                  .set_index('Name').transpose()
    df_bot5.index = df_bot5.index.astype(int)
    st.line_chart(df_bot5.loc[bottom_range[0]:bottom_range[1]])

with tab3:
    st.header("Global Military Expenditure Map")
    year_map = st.slider(
        "Select a year for the map:",
        min_value=1960, max_value=2018, value=2018
    )
    df_map = df[["Name", str(year_map)]].copy()
    df_map.columns = ["Country", "Expenditure"]
    df_map = df_map[df_map["Expenditure"] > 0]

    fig_map = px.choropleth(
        df_map,
        locations="Country",
        locationmode="country names",
        color="Expenditure",
        hover_name="Country",
        color_continuous_scale="YlOrRd",
        projection="orthographic",
        title=f"Military Expenditure by Country in {year_map}"
    )
    fig_map.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            showland=True, landcolor="rgb(217,217,217)",
            subunitcolor="rgb(255,255,255)",
            lataxis_showgrid=True, lonaxis_showgrid=True
        ),
        coloraxis_colorbar=dict(title="Expenditure (USD)")
    )
    st.plotly_chart(fig_map, use_container_width=True)
