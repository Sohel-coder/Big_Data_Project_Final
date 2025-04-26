import streamlit as st
import pandas as pd
import plotly.express as px

# 1) Page config: use full width
st.set_page_config(page_title="Trade Balance Analysis", layout="wide")

# 2) App title and intro
st.title("🌐 Trade Balance Analysis")
st.markdown(
    """
    #### Dive into global trade balances  
    Explore a country’s trade surplus/deficit over time, discover key historical events,  
    and see who India’s top military trade partners are in any given year.
    """
)

# 3) Custom CSS for styling & animations
st.markdown("""
<style>
/* …your existing CSS from fadeIn through popup-container.show… */
</style>
""", unsafe_allow_html=True)

# 4) Load data
trade_df  = pd.read_csv("data/exports_imports_cleaned.csv")
events_df = pd.read_csv("data/trade_events_updated2.csv", encoding="latin-1")

# 5) Initialize session state
if 'show_popup' not in st.session_state:
    st.session_state.update({
        "show_popup": False,
        "popup_content": None,
        "show_trade_popup": False,
        "trade_popup_content": None,
        "selected_year": trade_df["financial_year(start)"].min()
    })

# ─────────────────────────────────────────────────────────────────────────────
# 📊 Section 1: Country-wise Trade Balance Trend
st.markdown("---")
st.markdown("### 1️⃣ Country-wise Trade Balance Trend")
st.markdown(
    """
    Select any country to see how its **trade balance** (exports minus imports)
    has evolved over the years. Click on any bar to reveal a major historical event
    that shaped that year’s trade outcome.
    """
)

col1, col2, col3 = st.columns([1,6,1])
with col2:
    country = st.selectbox(
        "🔽 Pick a country:",
        options=sorted(trade_df["country"].unique()),
        help="Choose a country to view its yearly trade balance."
    )

ct = trade_df[trade_df["country"] == country].copy()
ct["year"] = ct["financial_year(start)"].astype(int)

fig = px.bar(
    ct, x="year", y="trade_balance",
    color="trade_balance",
    color_continuous_scale=[
        "#E6F0FA","#ADD8E6","#87CEEB","#4682B4","#1E40AF"
    ],
    labels={"trade_balance":"Trade Balance (M USD)","year":"Year"},
    title=f"📈 Trade Balance Trend for {country}"
)
fig.update_traces(
    marker_line_color="#333333",
    marker_line_width=1.5,
    opacity=0.9,
    hovertemplate="<b>Year</b>: %{x}<br><b>Balance</b>: %{y:.2f}M<extra></extra>"
)
fig.update_layout(
    plot_bgcolor="#F0F8FF", 
    paper_bgcolor="#F0F8FF",
    xaxis=dict(tickangle=45),
    margin=dict(t=60,b=40)
)

evt = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

if evt:
    pts = evt.get("selection",{}).get("points",[])
    if pts:
        y_clicked = int(pts[0]["x"])
        val = ct.loc[ct["year"]==y_clicked,"trade_balance"].iloc[0]
        st.markdown(f"<div class='trade-info'>**Year:** {y_clicked} | **Trade Balance:** {val:.2f}M USD</div>", unsafe_allow_html=True)

        evrow = events_df.query("country==@country & year==@y_clicked")
        if not evrow.empty:
            st.session_state.show_popup = True
            st.session_state.popup_content = {
                "year": y_clicked,
                "description": evrow["event_description"].iloc[0]
            }

if st.session_state.show_popup and st.session_state.popup_content:
    pc = st.session_state.popup_content
    st.markdown(f"""
    <div class='popup-container show'>
      <div class='popup-title'>Historical Event ({pc['year']})</div>
      <div class='popup-description'>{pc['description']}</div>
      <button class='close-button'>Close</button>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("<style>.popup-container { display: none; }</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 🌍 Section 2: India’s Top Trading Partners by Year
st.markdown("---")
st.markdown("### 2️⃣ India’s Top Trading Partners by Year")
st.markdown(
    """
    Choose a year to see which countries ranked highest in **total military trade** with India
    (imports + exports). Hover or click any bubble for exact figures.
    """
)

col1, col2, col3 = st.columns([1,6,1])
with col2:
    year = st.selectbox(
        "🔽 Pick a year:",
        options=sorted(trade_df["financial_year(start)"].unique()),
        index=sorted(trade_df["financial_year(start)"].unique()).index(st.session_state.selected_year),
        key="yr",
        help="Choose a year to see India’s top partners."
    )
    st.session_state.selected_year = year

ty = trade_df[trade_df["financial_year(start)"] == year]
agg = (
    ty.groupby("country")
      .agg(import_sum=("import","sum"), export_sum=("export","sum"))
      .assign(total_trade=lambda d: d.import_sum + d.export_sum)
      .reset_index()
)
agg["imports_billion"] = agg.import_sum / 1000
agg["exports_billion"] = agg.export_sum / 1000
agg["total_trade_billion"] = agg.total_trade / 1000
top6 = agg.nlargest(6, "total_trade")

fig2 = px.scatter(
    top6,
    x="country", y="total_trade_billion", size="total_trade_billion",
    color="country", size_max=60,
    labels={"total_trade_billion":"Total Trade (B USD)"},
    title=f"💼 Top 6 Trading Partners (FY {year})",
    color_discrete_sequence=px.colors.sequential.Blues_r
)
fig2.update_traces(
    marker=dict(line=dict(color="#333333", width=1.5)),
    hovertemplate="<b>%{x}</b><br>Total Trade: %{y:.1f}B USD<extra></extra>"
)
fig2.update_layout(
    plot_bgcolor="#F0F8FF",
    paper_bgcolor="#F0F8FF",
    margin=dict(t=60,b=40)
)

evt2 = st.plotly_chart(fig2, use_container_width=True, on_select="rerun")

if evt2:
    pts = evt2.get("selection",{}).get("points",[])
    if pts:
        c = pts[0]["x"]
        row = top6[top6.country==c].iloc[0]
        st.session_state.show_trade_popup = True
        st.session_state.trade_popup_content = {
            "country": c,
            "imports": row.imports_billion,
            "exports": row.exports_billion,
            "balance": row.exports_billion - row.imports_billion
        }

if st.session_state.show_trade_popup and st.session_state.trade_popup_content:
    tp = st.session_state.trade_popup_content
    st.markdown(f"""
    <div class='trade-popup-container show'>
      <div class='popup-title'>Trade with {tp['country']} (FY {year})</div>
      <div class='popup-description'>
        Imports: **${tp['imports']:.2f}B**<br>
        Exports: **${tp['exports']:.2f}B**<br>
        Balance: **${tp['balance']:.2f}B**
      </div>
      <button class='close-button'>Close</button>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("<style>.trade-popup-container { display: none; }</style>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Data sources: Military exports/imports CSV & historical events CSV. © Your Organization")
