import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

st.set_page_config(page_title="Defence Budget", layout="wide")
st.title("🌍 Global Defence Budget Insights")
st.markdown("Explore patterns and trends in military spending across the globe via the tabs below.")
st.divider()

@st.cache_data
def load_data():
    """Load and validate defence-budget CSV."""
    df = pd.read_csv("data/Cleaned_Defence_Budget.csv")
    years = [str(y) for y in range(1960, 2021)]
    # Essential columns
    if "Country Code" not in df.columns or "Country Name" not in df.columns:
        st.error("Dataset must include 'Country Code' and 'Country Name'.")
        st.stop()
    # Check for missing year columns
    missing = [y for y in years if y not in df.columns]
    if missing:
        st.warning(f"Missing year columns: {', '.join(missing)}")
    # Coerce numeric
    for y in years:
        if y in df.columns:
            df[y] = pd.to_numeric(df[y], errors="coerce")
    return df, years

df, year_columns = load_data()

# Create the three horizontal tabs
tab1, tab2, tab3 = st.tabs([
    "🌐 Global Spending (% of GDP)",
    "📊 Top Spenders vs India",
    "🕰️ Decade Breakdown"
])

# --- Tab 1: Global Military Spending Choropleth Globe ---
with tab1:
    st.header("🌐 Global Military Spending (% of GDP)")
    years_int = sorted([int(y) for y in year_columns if y.isdigit()])
    year = st.slider("Select Year", min_value=years_int[0], max_value=years_int[-1], value=years_int[-1])
    ystr = str(year)
    df_year = df[["Country Name", "Country Code", ystr]].dropna(subset=[ystr])
    if df_year.empty:
        st.warning("No data for that year.")
    else:
        fig = px.choropleth(
            df_year,
            locations="Country Code",
            color=ystr,
            hover_name="Country Name",
            hover_data={ystr:":.2f%"},
            projection="orthographic",
            color_continuous_scale=px.colors.sequential.Blues,
            range_color=(0, df_year[ystr].quantile(0.95)),
            title=f"Defence Spending as % of GDP in {year}"
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=50, b=10),
            geo=dict(bgcolor='rgba(0,0,0,0)', showland=True, landcolor="rgb(217,217,217)")
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"🔝 Top 5 Spenders in {year}")
            top5 = df_year.nlargest(5, ystr).set_index("Country Name")[[ystr]]
            top5.columns = ["Spending (% GDP)"]
            st.dataframe(top5, use_container_width=True)
        with col2:
            st.subheader(f"🔻 Bottom 5 Spenders in {year}")
            bot5 = df_year.nsmallest(5, ystr).set_index("Country Name")[[ystr]]
            bot5.columns = ["Spending (% GDP)"]
            st.dataframe(bot5, use_container_width=True)

# --- Tab 2: Top Spenders vs India ---
with tab2:
    st.header("📊 Top Defence Spenders vs India")
    year = st.slider("Select Year", min_value=years_int[0], max_value=years_int[-1], value=(years_int[0]+years_int[-1])//2, key="tab2_year")
    col = str(year)
    data = df[["Country Name", col]].dropna()
    ranked = data.sort_values(col, ascending=False)
    top10 = ranked.head(10)
    india = data[data["Country Name"]=="India"]
    if not india.empty and "India" not in top10["Country Name"].values:
        top10 = pd.concat([top10, india])
    fig = px.bar(
        top10,
        x=col, y="Country Name",
        orientation="h",
        color=col,
        color_continuous_scale="Plasma",
        title=f"Top 10 Spenders vs India in {year}"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=10,t=50))
    st.plotly_chart(fig, use_container_width=True)

    if not india.empty:
        rank = (ranked[col] > india[col].iloc[0]).sum() + 1
        st.markdown(f"**India’s rank in {year}:** #{rank}")

    st.markdown("---")
    st.subheader(f"Summary Metrics for {year}")
    vals = df[col].dropna()
    avg, med, mn, mx = vals.mean(), vals.median(), vals.min(), vals.max()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average", f"{avg:.2f}%")
    c2.metric("Median", f"{med:.2f}%")
    c3.metric("Minimum", f"{mn:.2f}%")
    c4.metric("Maximum", f"{mx:.2f}%")

    # India’s trend over time
    st.markdown("---")
    india_trend = (
        df[df["Country Name"]=="India"]
        .melt(id_vars="Country Name", value_vars=year_columns, var_name="Year", value_name="PctGDP")
        .dropna()
    )
    if not india_trend.empty:
        fig2 = px.line(india_trend, x="Year", y="PctGDP",
                       title="India's Spending (% GDP) Over Time")
        st.plotly_chart(fig2, use_container_width=True)

# --- Tab 3: Decade‐Wise Breakdown ---
# --- Tab 3: Decade‐Wise Breakdown ---
with tab3:
    st.header("🕰️ Decade‐Wise Defence Investment Breakdown")
    country = st.selectbox("Select a country", df["Country Name"].unique())
    selected = df[df["Country Name"] == country]

    # Prepare sunburst data
    sunburst_data = []
    root_avg = selected[year_columns].mean(axis=1).values[0]
    sunburst_data.append({
        "id": "1960–2020", "label": "1960–2020", "parent": "", "Spending": root_avg
    })

    for decade_start in range(1960, 2020, 10):
        decade_label = f"{decade_start}s"
        years = [str(y) for y in range(decade_start, decade_start + 10)]
        decade_avg = selected[years].mean(axis=1).values[0]
        sunburst_data.append({
            "id": decade_label, "label": decade_label, "parent": "1960–2020", "Spending": decade_avg
        })
        for year in years:
            year_value = selected[year].values[0]
            sunburst_data.append({
                "id": year, "label": year, "parent": decade_label, "Spending": year_value
            })

    df_sunburst = pd.DataFrame(sunburst_data)

    st.subheader(f"🧭 Defense Spending Sunburst (1960–2020) – {country}")
    fig = px.sunburst(
    df_sunburst,
    names="label",
    parents="parent",
    values="Spending",
    color="Spending",
    color_continuous_scale="Blues",
    custom_data=["label"]  # 👈 This line makes 'label' available in click events
    )

    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    from streamlit_plotly_events import plotly_events
    selected_event = plotly_events(fig, click_event=True, key="sunburst")
    



    # Determine year range based on click
    if selected_event and "customdata" in selected_event[0]:
        clicked_label = selected_event[0]["customdata"][0]  # 👈 Safely extract the label from the click
        if clicked_label == "1960–2020":
            years = [str(y) for y in range(1960, 2021)]
            title_label = "1960–2020"
        elif clicked_label.isdigit() and int(clicked_label) % 10 == 0:
            # Treat as decade start (e.g., 1980, 1990)
            decade_start = int(clicked_label)
            years = [str(y) for y in range(decade_start, decade_start + 10)]
            title_label = f"{decade_start}s"
        elif clicked_label.isdigit():
            # Treat as specific year
            years = [clicked_label]
            title_label = clicked_label
    else:
        # Fallback to full range
        years = [str(y) for y in range(1960, 2021)]
        title_label = "1960–2020"

    
    # Prepare radial data
    trend_df = selected[years].T.reset_index()
    trend_df.columns = ["Year", "Spending"]
    trend_df["Year"] = trend_df["Year"].astype(int)

    st.markdown(f"### 📊 {title_label} Average: **{trend_df['Spending'].mean():.2f}%** of GDP")

    if trend_df.empty or trend_df["Spending"].isna().all():
        st.warning(f"⚠️ No valid data available to render radial chart for **{title_label}**.")
    else:
        st.subheader("🌀 Year-wise Defense Spending (Radial View)")
        angles = np.linspace(0, 2 * np.pi, len(trend_df), endpoint=False)
        radii = trend_df["Spending"].values
        labels = trend_df["Year"].astype(str).tolist()

        fig_radial, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
        bars = ax.bar(angles, radii, width=0.45, bottom=0.0,
                      color=plt.cm.viridis(radii / max(radii)), edgecolor="black")

        ax.set_xticks([])
        ax.set_yticklabels([])

        for angle, label in zip(angles, labels):
            ax.plot([angle, angle], [0, max(radii) + 1], color="gray", linewidth=0.5, linestyle="--")
            rotation = np.degrees(angle)
            alignment = 'left'
            if 90 < rotation < 270:
                rotation += 180
                alignment = 'right'
            ax.text(angle, max(radii) + 1.5, label,
                    rotation=rotation,
                    ha=alignment,
                    va='center',
                    fontsize=9,
                    rotation_mode='anchor')

        fig_radial.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        st.image(buf)
        plt.close()

