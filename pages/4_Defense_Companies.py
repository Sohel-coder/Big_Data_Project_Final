import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Defense Revenue Insights", layout="wide")

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

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/updated_defense_companies_2005_2020.csv")  # Update path if needed

df = load_data()

# Define all companies
all_companies = sorted(df["Company"].unique())

st.title("💼 Defense Companies Analysis (2005–2020)")

# --- In-Page Filters ---
st.markdown("### 🔎 Filter")

# Removed the selectbox for year
# Get the latest year from the data as default
year_selected = df["Year"].max()

top_n = st.slider(
    "Top N Countries",
    min_value=5,
    max_value=30,
    value=10
)

# Filter top N companies per year
top_over_time = (
    df.groupby("Year")
    .apply(lambda x: x.nlargest(top_n, "Defense_Revenue_From_A_Year_Ago"))
    .reset_index(drop=True)
)

######################################Module-01################################################################################
#@Module-01
# 1. Top N Countries by Defense Revenue
st.subheader(f"🎞️ Animated Top {top_n} Countries by Defense Revenue (2005–2020)")

# Filter data to select top N countries by defense revenue each year
top_countries_over_time = (
    df.groupby(["Year", "Country"])["Defense_Revenue_From_A_Year_Ago"]
    .sum()
    .reset_index()
    .sort_values(by=["Year", "Defense_Revenue_From_A_Year_Ago"], ascending=[True, False])
)

# For each year, select the top N countries by defense revenue
top_countries_over_time = (
    top_countries_over_time.groupby("Year")
    .apply(lambda x: x.head(top_n))
    .reset_index(drop=True)
)

# Determine the maximum defense revenue to fix x-axis range across years
max_revenue = top_countries_over_time["Defense_Revenue_From_A_Year_Ago"].max()

# Create an animated bar chart showing the top N countries by defense revenue each year
fig_top_animated_countries = px.bar(
    top_countries_over_time,
    x="Defense_Revenue_From_A_Year_Ago",
    y="Country",
    color="Country",
    animation_frame="Year",
    orientation="h",
    title=f"Top {top_n} Countries by Defense Revenue from 2005 to 2020",
    labels={"Defense_Revenue_From_A_Year_Ago": "Defense Revenue"},
    height=600
)

fig_top_animated_countries.update_layout(
    xaxis=dict(range=[0, max_revenue]),
    yaxis={'categoryorder': 'total ascending'},
    margin=dict(t=40, l=0, r=0, b=0),
)

st.plotly_chart(fig_top_animated_countries, use_container_width=True)


# 2. Total number of companies per country year-wise (animated bar chart)

st.subheader(f"🎞️ Animated Total Number of Companies by Country (2005–2020)")

# Group the data by year and country and count the number of unique companies
company_count = (
    df.groupby(["Year", "Country"])["Company"]
    .nunique()
    .reset_index()
    .sort_values(by=["Year", "Company"], ascending=[True, False])
)

# For each year, select the top N countries based on the number of companies
top_companies_count = (
    company_count.groupby("Year")
    .apply(lambda x: x.head(top_n))
    .reset_index(drop=True)
)

# Create an animated bar chart showing the total number of companies for each country year-wise
fig_company_count = px.bar(
    top_companies_count,
    x="Company",
    y="Country",
    color="Country",
    animation_frame="Year",
    orientation="h",
    title="Total Number of Companies by Country (2005–2020)",
    labels={"Company": "Number of Companies"},
    height=600
)

# Update layout for better presentation
fig_company_count.update_layout(
    xaxis=dict(range=[0, top_companies_count["Company"].max()]),
    yaxis={'categoryorder': 'total ascending'},
    margin=dict(t=40, l=0, r=0, b=0),
)

# Display the animated bar chart
st.plotly_chart(fig_company_count, use_container_width=True)

#########################Module-02#############################################################################################
#@Module-02

selected_companies = st.multiselect(
    "Select Companies for Trend",
    all_companies
)

# Filter dataset
df_filtered = df[df["Year"] == year_selected]

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

#####################################Module-03#################################################################################
#@Module-03

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

######################################Module-04################################################################################################
#@Module-04

# Animated Bubble Chart
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
# Expandable Raw Data
with st.expander("📄 View Raw Data"):
    st.dataframe(df_filtered)

# Footer
st.markdown(""" 
--- 
🔍 Built with Streamlit & Plotly • Interactive Defense Revenue Insights 
""")
