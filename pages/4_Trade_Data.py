import streamlit as st
import pandas as pd
import plotly.express as px

# 1) Full-width layout
st.set_page_config(page_title="Trade Balance Analysis", layout="wide")

# 2) Title & intro
st.title("🌐 Trade Balance Analysis")
st.markdown(
    """
    Explore a country’s annual trade balance, click bars to see key historical events,  
    and find out who India’s top military trade partners are in any selected year.
    """
)

# 3) Popup CSS—centered perfectly
st.markdown("""
<style>
/* Fade-in */
@keyframes fadeIn {0%{opacity:0;transform:translateY(20px)}100%{opacity:1;transform:translateY(0)}}

/* Pop-up containers (in-flow, centered under chart) */
.popup-container, .trade-popup-container {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  max-width: 420px;
  width: 90%;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  margin: 20px auto;            /* center horizontally, in-flow */
  animation: fadeIn 0.4s ease-out;
}

/* Distinct backgrounds */
.popup-container {background: linear-gradient(135deg,#E6F0FA,#FFFFFF);}
.trade-popup-container {background: linear-gradient(135deg,#F0FFF4,#E6FFE6);}

/* Icons */
.popup-container::before, .trade-popup-container::before {
  content: '';
  position: absolute; /* you'll need to add position: relative on the container */
  top: 12px; left: 12px;
  font-size: 24px; opacity: 0.7;
}
.popup-container { position: relative; }
.popup-container::before { content: '📅'; }
.trade-popup-container { position: relative; }
.trade-popup-container::before { content: '🌐'; }

/* Title & text */
.popup-title {
  text-align:center; font-size:20px; font-weight:600; color:#1E3A8A; margin-bottom:12px;
}
.popup-description {
  font-size:14px; color:#2A4365; line-height:1.6; text-align:left;
}

/* Close button */
.close-button {
  display:block; margin:20px auto 0;
  padding:8px 24px; background:#1E3A8A; color:#fff; border:none; border-radius:6px;
  cursor:pointer; font-size:14px;
}
.close-button:hover {background:#145A96;}
</style>
""", unsafe_allow_html=True)

# 4) Load data
trade_df  = pd.read_csv("data/exports_imports_cleaned.csv")
events_df = pd.read_csv("data/trade_events_updated2.csv", encoding="latin-1")

# 5) Init session
if 'show_popup' not in st.session_state:
    st.session_state.update({
        "show_popup": False,
        "popup_content": None,
        "show_trade_popup": False,
        "trade_popup_content": None,
        "selected_year": trade_df["financial_year(start)"].min()
    })

# ─────────────────────────────────────────────────────────────────────────────
# Section 1: Country-wise Trade Balance
st.markdown("---")
st.markdown("### 1️⃣ Country-wise Trade Balance Trend")
col1, col2, col3 = st.columns([1,6,1])
with col2:
    country = st.selectbox(
        "Select a country:",
        sorted(trade_df["country"].unique()),
        help="Click a bar for that year’s event."
    )

ct = trade_df[trade_df["country"]==country].copy()
ct["year"] = ct["financial_year(start)"].astype(int)

fig = px.bar(
    ct, x="year", y="trade_balance",
    color="trade_balance",
    color_continuous_scale=[
        "#D0E4F7", "#A1C9EF", "#72AFE8", "#438FE0", "#176FD8"
    ],
    labels={"trade_balance":"Trade Balance (Mil USD)","year":"Year"},
    title=f"Trade Balance Trend for {country}",
    template="plotly_white"
)

# add big readable text on bars
fig.update_traces(
    texttemplate="%{y:.1f}",                # show the bar value
    textposition="outside",
    textfont=dict(size=12, color="#1E3A8A")
)

fig.update_layout(
    font=dict(family="Helvetica", size=14, color="#333333"),
    title=dict(font=dict(size=24, color="#1E3A8A")),
    xaxis=dict(
        title=dict(text="Year", font=dict(size=16, color="#555555")),
        tickfont=dict(size=12, color="#333333"),
        gridcolor="#EEEEEE",
        zerolinecolor="#DDDDDD"
    ),
    yaxis=dict(
        title=dict(text="Trade Balance (Mil USD)", font=dict(size=16, color="#555555")),
        tickfont=dict(size=12, color="#333333"),
        gridcolor="#EEEEEE",
        zerolinecolor="#DDDDDD"
    ),
    margin=dict(l=60, r=30, t=80, b=50),
    coloraxis_colorbar=dict(
        title="Balance",
        tickfont=dict(size=12, color="#333333"),
        titlefont=dict(size=14, color="#333333")
    )
)
st.plotly_chart(fig, use_container_width=True)
evt = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

if evt:
    pts = evt.get("selection",{}).get("points",[])
    if pts:
        y = int(pts[0]["x"])
        bal = ct.loc[ct["year"]==y, "trade_balance"].iloc[0]
        st.markdown(f"<div style='text-align:center;font-weight:bold;color:#1E3A8A;'>Year: {y} | Balance: {bal:.2f}M USD</div>", unsafe_allow_html=True)

        ev = events_df.query("country==@country & year==@y")
        if not ev.empty:
            st.session_state.show_popup = True
            st.session_state.popup_content = {
                "year": y,
                "desc": ev["event_description"].iloc[0]
            }

if st.session_state.show_popup:
    pc = st.session_state.popup_content
    st.markdown(f"""
    <div class='popup-container'>
      <div class='popup-title'>Historical Event ({pc['year']})</div>
      <div class='popup-description'>{pc['desc']}</div>
      <button class='close-button' onclick="window.location.reload()">Close</button>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Section 2: India’s Top Trading Partners
st.markdown("---")
st.markdown("### 2️⃣ India’s Top Trading Partners by Year")
col1, col2, col3 = st.columns([1,6,1])
with col2:
    year = st.selectbox(
        "Select year:",
        sorted(trade_df["financial_year(start)"].unique()),
        index=sorted(trade_df["financial_year(start)"].unique()).index(st.session_state.selected_year)
    )
    st.session_state.selected_year = year

ty = trade_df[trade_df["financial_year(start)"]==year]
agg = (ty.groupby("country")
       .agg(import_sum=("import","sum"), export_sum=("export","sum"))
       .assign(total=lambda d: d.import_sum+d.export_sum)
       .reset_index())
agg["imports_b"] = agg.import_sum/1000
agg["exports_b"] = agg.export_sum/1000
agg["total_b"]   = agg.total/1000
top6 = agg.nlargest(6,"total")

fig2 = px.scatter(
    top6,
    x="country", y="total_trade_billion",
    size="total_trade_billion",
    color="total_trade_billion",
    color_continuous_scale="Blues",
    size_max=60,
    labels={"total_trade_billion":"Total Trade (B USD)"},
    title=f"Top 6 Trading Partners (FY {year})",
    template="plotly_white"
)

fig2.update_traces(
    marker=dict(line=dict(color="#333333", width=1.5)),
    hovertemplate='<b>%{x}</b><br>Total Trade: %{y:.1f}B<extra></extra>'
)

fig2.update_layout(
    font=dict(family="Helvetica", size=14, color="#333333"),
    title=dict(font=dict(size=24, color="#1E3A8A")),
    xaxis=dict(
        title=dict(text="Country", font=dict(size=16, color="#555555")),
        tickfont=dict(size=12, color="#333333")
    ),
    yaxis=dict(
        title=dict(text="Total Trade (Billion USD)", font=dict(size=16, color="#555555")),
        tickfont=dict(size=12, color="#333333"),
        gridcolor="#EEEEEE",
        zerolinecolor="#DDDDDD"
    ),
    margin=dict(l=60, r=30, t=80, b=50),
    showlegend=False
)

st.plotly_chart(fig2, use_container_width=True)
evt2 = st.plotly_chart(fig2, use_container_width=True, on_select="rerun")

if evt2:
    pts = evt2.get("selection",{}).get("points",[])
    if pts:
        c = pts[0]["x"]
        r = top6[top6.country==c].iloc[0]
        st.session_state.show_trade_popup = True
        st.session_state.trade_popup_content = {
            "c": c,
            "i": r.imports_b,
            "e": r.exports_b,
            "b": r.exports_b - r.imports_b
        }

if st.session_state.show_trade_popup:
    tp = st.session_state.trade_popup_content
    st.markdown(f"""
    <div class='trade-popup-container'>
      <div class='popup-title'>Trade with {tp['c']} (FY {year})</div>
      <div class='popup-description'>
        Imports: ${tp['i']:.2f}B<br>
        Exports: ${tp['e']:.2f}B<br>
        Balance: ${tp['b']:.2f}B
      </div>
      <button class='close-button' onclick="window.location.reload()">Close</button>
    </div>
    """, unsafe_allow_html=True)
