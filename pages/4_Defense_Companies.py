import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Defense Revenue Insights", layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/updated_defense_companies_2005_2020.csv")  # Update path if needed

df = load_data()

st.title("💼 Defense Companies Analysis (2005–2020)")

# --- In-Page Filters ---
st.markdown("### 🔎 Filters")
years = sorted(df["Year"].unique())
year_selected = st.selectbox(
    "Select Year",
    years,
    index=len(years) - 1
)
top_n = st.slider(
    "Top N Companies",
    min_value=5,
    max_value=30,
    value=10
)
all_companies = sorted(df["Company"].unique())
selected_companies = st.multiselect(
    "Select Companies for Trend",
    all_companies
)

# Filter dataset
df_filtered = df[df["Year"] == year_selected]

######################################################################################################################

# 1. Top N Companies by Defense Revenue
st.subheader(f"🎞️ Animated Top {top_n} Companies by Defense Revenue (2005–2020)")

# Filter top N companies per year
top_over_time = (
    df.groupby("Year")
    .apply(lambda x: x.nlargest(top_n, "Defense_Revenue_From_A_Year_Ago"))
    .reset_index(drop=True)
)

# Determine max value to fix x-axis
max_revenue = df["Defense_Revenue_From_A_Year_Ago"].max()

fig_top_animated = px.bar(
    top_over_time,
    x="Defense_Revenue_From_A_Year_Ago",
    y="Company",
    color="Country",
    animation_frame="Year",
    orientation="h",
    title=f"Top {top_n} Defense Companies from 2005 to 2020",
    labels={"Defense_Revenue_From_A_Year_Ago": "Defense Revenue"},
    height=600
)

fig_top_animated.update_layout(
    xaxis=dict(range=[0, max_revenue]),
    yaxis={'categoryorder': 'total ascending'},
    margin=dict(t=40, l=0, r=0, b=0),
)

st.plotly_chart(fig_top_animated, use_container_width=True)

######################################################################################################################

# 2. Defense Revenue Trend Over Years
st.subheader("📈 Defense Revenue Trend (2005–2020)")

if selected_companies:
    trend_df = df[df["Company"].isin(selected_companies)]
else:
    trend_df = df[df["Company"].isin(top_over_time["Company"])]

fig_trend = px.line(
    trend_df,
    x="Year",
    y="Defense_Revenue_From_A_Year_Ago",
    color="Company",
    markers=True,
    title="Defense Revenue Trend Over Time",
    labels={"Defense_Revenue_From_A_Year_Ago": "Defense Revenue"},
)
st.plotly_chart(fig_trend, use_container_width=True)

######################################################################################################################

# 3. Sunburst Chart (Filtered by Top Countries and Companies)
st.subheader("🌞 Interactive Sunburst: Country → Company")

col1, col2 = st.columns(2)
with col1:
    num_countries = st.number_input(
        "Number of Top Countries",
        min_value=1,
        max_value=20,
        value=5
    )
with col2:
    num_companies = st.number_input(
        "Number of Top Companies per Country",
        min_value=1,
        max_value=20,
        value=3
    )

# Step 1: Get top N countries by total defense revenue in the selected year
top_countries = (
    df_filtered.groupby("Country")["Defense_Revenue_From_A_Year_Ago"]
    .sum()
    .nlargest(num_countries)
    .index
)

filtered_country_df = df_filtered[df_filtered["Country"].isin(top_countries)]

# Step 2: For each country, get top K companies by defense revenue
sunburst_data = (
    filtered_country_df.groupby(["Country", "Company"])["Defense_Revenue_From_A_Year_Ago"]
    .sum()
    .reset_index()
)

top_company_entries = sunburst_data.groupby("Country").apply(
    lambda x: x.nlargest(num_companies, "Defense_Revenue_From_A_Year_Ago")
).reset_index(drop=True)

# Step 3: Add a "World" level for full-circle path logic
top_company_entries["World"] = "World"

# Step 4: Create a Sunburst chart with limited initial depth
fig_sunburst = px.sunburst(
    top_company_entries,
    path=["World", "Country", "Company"],
    values="Defense_Revenue_From_A_Year_Ago",
    color="Country",
    title="Top Countries and Leading Defense Companies (Sunburst)",
    maxdepth=2
)

fig_sunburst.update_layout(
    margin=dict(t=40, l=0, r=0, b=0),
    sunburstcolorway=px.colors.qualitative.Pastel,
    extendsunburstcolors=True,
)

st.plotly_chart(fig_sunburst, use_container_width=True)

######################################################################################################################################

#4. Animated Bubble Chart
st.subheader("🎥 Animated Bubble Chart: Company Revenue Evolution (2005–2020)")

top_n_bubble = st.slider(
    "Top N Companies per Year (for animation)",
    5, 30, 15
)

# Prepare data: pick top N companies per year by defense revenue
animated_df = (
    df.groupby(["Year", "Company", "Country"], as_index=False)
    .agg({
        "Defense_Revenue_From_A_Year_Ago": "sum",
        "Total Revenue": "sum",
        "%of Revenue from Defence": "mean"
    })
)

# Get top N companies for each year
animated_df["rank"] = animated_df.groupby("Year")["Defense_Revenue_From_A_Year_Ago"]\
    .rank("dense", ascending=False)
animated_df = animated_df[animated_df["rank"] <= top_n_bubble]

# Bubble chart with animation
fig_bubble = px.scatter(
    animated_df,
    x="Total Revenue",
    y="Defense_Revenue_From_A_Year_Ago",
    animation_frame="Year",
    animation_group="Company",
    size="%of Revenue from Defence",
    color="Country",
    hover_name="Company",
    size_max=60,
    title="Company Evolution Over Time (2005–2020)",
    labels={
        "Defense_Revenue_From_A_Year_Ago": "Defense Revenue",
        "Total Revenue": "Total Revenue",
        "%of Revenue from Defence": "% from Defense"
    }
)

fig_bubble.update_layout(margin=dict(t=40, l=0, r=0, b=0))
st.plotly_chart(fig_bubble, use_container_width=True)

######################################################################################################################

# 5. Expandable Raw Data
with st.expander("📄 View Raw Data"):
    st.dataframe(df_filtered)

# Footer
st.markdown("""
---
🔍 Built with Streamlit & Plotly • Interactive Defense Revenue Insights
""")
