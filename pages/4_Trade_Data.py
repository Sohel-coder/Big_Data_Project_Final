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

/* Pop-up containers */
.popup-container, .trade-popup-container {
  position: fixed;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  max-width: 420px;
  width: 90%;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  animation: fadeIn 0.4s ease-out;
  z-index: 9999;
}
/* Distinct backgrounds */
.popup-container {background: linear-gradient(135deg,#E6F0FA,#FFFFFF);}
.trade-popup-container {background: linear-gradient(135deg,#F0FFF4,#E6FFE6);}

/* Icons */
.popup-container::before, .trade-popup-container::before {
  position: absolute; top:12px; left:12px; font-size:24px; opacity:0.7;
}
.popup-container::before {content:'📅';}
.trade-popup-container::before {content:'🌐';}

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
    color_continuous_scale=["#E6F0FA","#ADD8E6","#87CEEB","#4682B4","#1E40AF"],
    labels={"trade_balance":"Balance (M USD)","year":"Year"},
    title=f"Trade Balance Trend for {country}"
)
fig.update_traces(marker_line_color="#333", marker_line_width=1.5, opacity=0.9)
fig.update_layout(plot_bgcolor="#F0F8FF", paper_bgcolor="#F0F8FF",
                  xaxis=dict(tickangle=45), margin=dict(t=60,b=40))

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
    top6, x="country", y="total_b",
    size="total_b", color="country",
    size_max=60, title=f"Top 6 Partners (FY {year})",
    labels={"total_b":"Total Trade (B USD)"},
    color_discrete_sequence=px.colors.sequential.Blues_r
)
fig2.update_traces(marker_line_color="#333", marker_line_width=1.5)
fig2.update_layout(plot_bgcolor="#F0F8FF", paper_bgcolor="#F0F8FF", margin=dict(t=60,b=40))

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
