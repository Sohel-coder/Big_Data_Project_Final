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
    country = st.selectbox("Select Country", df["Country Name"].unique(), key="tab3_country")
    sel = df[df["Country Name"]==country]

    # Build sunburst data
    sun = []
    # Root node
    total = sel[year_columns].sum(axis=1).iloc[0]
    avg_all = sel[year_columns].mean(axis=1).iloc[0]
    sun.append(dict(
        id="1960–2020",
        label="1960–2020",
        parent="",
        Spending=total,
        ColorMetric=avg_all
    ))

    # Decades + years
    for start in range(1960, 2020, 10):
        dec_label = f"{start}s"
        yrs = [str(y) for y in range(start, start+10)]
        vals = sel[yrs].sum(axis=1).iloc[0]
        avg_d = sel[yrs].mean(axis=1).iloc[0]
        # Decade slice
        sun.append(dict(
            id=dec_label,
            label=dec_label,
            parent="1960–2020",
            Spending=vals,
            ColorMetric=avg_d
        ))
        # Individual years (will be hidden until drilldown)
        for y in yrs:
            year_val = sel[y].iloc[0]
            sun.append(dict(
                id=str(y),
                label=str(y),
                parent=dec_label,
                Spending=year_val,
                ColorMetric=year_val
            ))

    df_sun = pd.DataFrame(sun)

    st.subheader(f"Sunburst: {country} (1960–2020)")
    fig_sb = px.sunburst(
        df_sun,
        names="label",
        parents="parent",
        values="Spending",
        color="ColorMetric",
        color_continuous_scale="Blues",
        branchvalues="total"
    )

    # 🔥 ONLY SHOW ROOT + DECADES AT FIRST
    fig_sb.update_traces(maxdepth=1)

    fig_sb.update_layout(
        margin=dict(t=10, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_sb, use_container_width=True)

    st.markdown("---")
    st.subheader("Radial Bar: Year‐wise Spending")
    decade_opts = ["1960–2020"] + [f"{s}s" for s in range(1960, 2020, 10)]
    choice = st.selectbox("Choose Decade", decade_opts)
    if choice == "1960–2020":
        years = year_columns
    else:
        s = int(choice[:4])
        years = [str(y) for y in range(s, s+10)]

    trend = sel[years].T.reset_index()
    trend.columns = ["Year", "Spending"]
    trend["Year"] = trend["Year"].astype(int)

    # Radial bar chart
    angles = np.linspace(0, 2*np.pi, len(trend), endpoint=False)
    radii = trend["Spending"].values
    fig_r, ax = plt.subplots(
        figsize=(7, 7),
        subplot_kw=dict(polar=True)
    )
    bars = ax.bar(
        angles,
        radii,
        width=2*np.pi/len(radii),
        color=plt.cm.viridis(radii/radii.max()),
        edgecolor="black"
    )
    ax.set_xticks([])
    ax.set_yticks([])
    for a, lbl in zip(angles, trend["Year"].astype(str)):
        ax.text(
            a,
            radii.max() * 1.05,
            lbl,
            rotation=np.degrees(a),
            ha='center',
            va='center',
            fontsize=8
        )
    plt.tight_layout()
    st.pyplot(fig_r)
    plt.close()

    avg_dec = trend["Spending"].mean()
    st.markdown(f"**Average spending in {choice}:** {avg_dec:.2f}% of GDP")
