import streamlit as st
import pandas as pd
import plotly.express as px

# ─── 1) Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Trade Balance Analysis",
    layout="wide",
)

# ─── 2) Header & Intro ──────────────────────────────────────────────────────────
st.title("🌐 Trade Balance Analysis")
st.markdown(
    """
    Dive into country-wise trade balances over time, explore historical events,  
    and discover India's top military trade partners for any selected year.
    """
)

# ─── 3) Simple CSS (align to second page style) ──────────────────────────────────
st.markdown("""
<style>
.stApp { max-width:1200px; margin:0 auto; padding:20px; font-family:Helvetica, sans-serif; }
.tab-header { font-size:20px; font-weight:bold; margin-bottom:10px; color:#1E3A8A; }
.chart-container { background:#F9FAFB; padding:10px; border-radius:8px; }
</style>
""", unsafe_allow_html=True)

# ─── 4) Load data ────────────────────────────────────────────────────────────────
trade_df  = pd.read_csv("data/exports_imports_cleaned.csv")
events_df = pd.read_csv("data/trade_events_updated2.csv", encoding="latin-1")

# ─── 5) Session state defaults ──────────────────────────────────────────────────
if "selected_year" not in st.session_state:
    st.session_state.selected_year = int(trade_df["financial_year(start)"].min())

# ─── 6) Tabs setup ───────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs([
    "📈 Country Trade Balance",
    "🌍 India's Top Partners by Year"
])

# ─── Tab 1: Country-wise Trade Balance ───────────────────────────────────────────
with tab1:
    st.markdown("<div class='tab-header'>1. Country-wise Trade Balance Trend</div>", unsafe_allow_html=True)

    # select country
    country = st.selectbox(
        "Select a Country",
        options=sorted(trade_df["country"].unique()),
        help="Pick a country to see its yearly trade balance."
    )

    # prepare data
    df_ct = trade_df[trade_df["country"] == country].copy()
    df_ct["year"] = df_ct["financial_year(start)"].astype(int)

    # plot
    fig1 = px.bar(
        df_ct, x="year", y="trade_balance",
        color="trade_balance",
        color_continuous_scale=["#E6F0FA","#ADD8E6","#87CEEB","#4682B4","#1E40AF"],
        labels={"trade_balance":"Trade Balance (M USD)","year":"Year"},
        title=f"Trade Balance Trend for {country}"
    )
    fig1.update_layout(
        plot_bgcolor="#F9FAFB", paper_bgcolor="#F9FAFB",
        margin=dict(t=50,b=25), xaxis_tickangle=45
    )

    st.plotly_chart(fig1, use_container_width=True)

    # click → popup info
    click1 = st.plotly_chart(fig1, use_container_width=True, key="chart1", on_select="rerun")
    if click1:
        pts = click1.get("selection",{}).get("points",[])
        if pts:
            yr = int(pts[0]["x"])
            bal = df_ct.loc[df_ct["year"]==yr, "trade_balance"].iloc[0]
            st.markdown(f"**Year:** {yr}  |  **Trade Balance:** {bal:.2f}M")

            ev = events_df.query("country == @country and year == @yr")
            if not ev.empty:
                st.markdown(f"> 📅 **Event ({yr}):** {ev['event_description'].iloc[0]}")

# ─── Tab 2: India’s Top Trading Partners ────────────────────────────────────────
with tab2:
    st.markdown("<div class='tab-header'>2. India's Top Trading Partners by Year</div>", unsafe_allow_html=True)

    # select year
    year = st.selectbox(
        "Select Year",
        options=sorted(trade_df["financial_year(start)"].unique().astype(int)),
        index=sorted(trade_df["financial_year(start)"].unique().astype(int)).index(st.session_state.selected_year),
        key="year_sel",
        help="Pick a year to see India’s leading partners."
    )
    st.session_state.selected_year = year

    # aggregate
    df_ty = trade_df[trade_df["financial_year(start)"] == year]
    agg = (
        df_ty.groupby("country")
             .agg(import_sum=("import","sum"), export_sum=("export","sum"))
             .assign(total_trade=lambda d: d.import_sum + d.export_sum)
             .reset_index()
    )
    agg["total_trade_billion"] = agg["total_trade"] / 1000
    top6 = agg.nlargest(6, "total_trade")

    # bubble
    fig2 = px.scatter(
        top6, x="country", y="total_trade_billion", size="total_trade_billion",
        color="country", size_max=60,
        labels={"total_trade_billion":"Total Trade (B USD)"},
        title=f"Top 6 Trading Partners (FY {year})",
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig2.update_layout(
        plot_bgcolor="#F9FAFB", paper_bgcolor="#F9FAFB",
        margin=dict(t=50,b=25)
    )

    st.plotly_chart(fig2, use_container_width=True)

    # click → popup
    click2 = st.plotly_chart(fig2, use_container_width=True, key="chart2", on_select="rerun")
    if click2:
        pts = click2.get("selection",{}).get("points",[])
        if pts:
            cty = pts[0]["x"]
            row = top6[top6.country == cty].iloc[0]
            im = row.import_sum/1000
            ex = row.export_sum/1000
            bal = (row.export_sum - row.import_sum)/1000
            st.markdown(f"""
            **Partner:** {cty}  
            Imports: {im:.2f}B USD  
            Exports: {ex:.2f}B USD  
            **Balance:** {bal:.2f}B USD
            """)

# ─── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data sources: exports_imports_cleaned.csv & trade_events_updated2.csv")
