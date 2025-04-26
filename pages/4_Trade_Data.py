import streamlit as st
import pandas as pd
import plotly.express as px

# 1) Page config: true full-width
st.set_page_config(page_title="Trade Balance Analysis", layout="wide")
st.title("🌐 Trade Balance Analysis")
st.markdown(
    """
    Dive into the trade balances of countries over time, explore historical events,  
    and see who India’s top military trade partners are in any given year.  
    """
)

# 2) Custom CSS
st.markdown("""
<style>
/* Animations */
@keyframes fadeIn { 0% {opacity:0; transform:translateY(20px);} 100% {opacity:1; transform:translateY(0);} }
@keyframes pulse  { 0% {transform:scale(1);} 50% {transform:scale(1.05);} 100% {transform:scale(1);} }
@keyframes wave   { 0% {background-position:0% 50%;} 50% {background-position:100% 50%;} 100% {background-position:0% 50%;} }

/* Light grey background */
body { background-color: #F5F5F5; font-family: 'Helvetica', sans-serif; }

/* Center container */
.stApp { max-width:1200px; margin:0 auto; padding:20px; }

/* Popups */
.popup-container, .trade-popup-container {
  background-size:200% 200%;
  animation: fadeIn 0.5s ease-out forwards, wave 8s infinite;
  border-radius:15px; padding:20px; max-width:450px; margin:20px auto;
  box-shadow:0 8px 16px rgba(0,0,0,0.2);
  position:relative;
}
.popup-container { background: linear-gradient(135deg,#E6F0FA,#FFFFFF); }
.trade-popup-container { background: linear-gradient(135deg,#F0FFF4,#E6FFE6); }

/* Icons */
.popup-container::before { content:'📅'; position:absolute; top:10px; left:10px; font-size:24px; opacity:0.7; }
.trade-popup-container::before { content:'🌐'; position:absolute; top:10px; left:10px; font-size:24px; opacity:0.7; }

/* Titles */
.popup-title { text-align:center; font-size:22px; font-weight:bold; color:#1E3A8A; margin-bottom:10px; }
.popup-description { font-size:14px; color:#2A4365; line-height:1.6; text-align:justify; }

/* Trade Info below bar chart */
.trade-info { text-align:center; font-size:16px; color:#1E3A8A; font-weight:bold; margin-top:10px; }

/* Close button */
.close-button {
  display:block; margin:20px auto 0; padding:8px 20px;
  background:linear-gradient(90deg,#3B82F6,#60A5FA);
  color:#fff; border:none; border-radius:25px; cursor:pointer;
  font-size:14px; animation:pulse 1.5s infinite;
}
.close-button:hover { background:linear-gradient(90deg,#1E40AF,#3B82F6); transform:scale(1.05); }
</style>
""", unsafe_allow_html=True)

# 3) Load data
trade_df = pd.read_csv("exports_imports_cleaned.csv")
events_df = pd.read_csv("trade_events_updated2.csv", encoding="latin-1")

# 4) Session state init
if "show_popup" not in st.session_state:
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
st.markdown("### 📈 1. Country-wise Trade Balance Trend")
col1, col2, col3 = st.columns([1,6,1])
with col2:
    country = st.selectbox(
        "Select a Country",
        options=sorted(trade_df["country"].unique()),
        index=0,
        help="Pick a country to see its yearly trade balance."
    )

# prepare and plot
ct = trade_df[trade_df["country"]==country].copy()
ct["year"] = ct["financial_year(start)"].astype(int)

fig = px.bar(
    ct, x="year", y="trade_balance",
    color="trade_balance",
    color_continuous_scale=[
        "#E6F0FA","#ADD8E6","#87CEEB","#4682B4","#1E40AF"
    ],
    labels={"trade_balance":"Trade Balance (Mil USD)","year":"Year"},
    title=f"Trade Balance Trend for {country}"
)
fig.update_traces(
    marker_line_color="#333333",
    marker_line_width=1.5,
    opacity=0.9,
    hovertemplate="<b>Year</b>: %{x}<br><b>Balance</b>: %{y:.2f}M<extra></extra>"
)
fig.update_layout(
    plot_bgcolor="#F0F8FF", paper_bgcolor="#F0F8FF",
    xaxis=dict(tickangle=45), margin=dict(t=60,b=40)
)

# render & capture clicks
evt = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

# handle click → show popup
if evt:
    pts = evt.get("selection",{}).get("points",[])
    if pts:
        y_clicked = int(pts[0]["x"])
        val = ct.loc[ct["year"]==y_clicked,"trade_balance"].iloc[0]
        st.markdown(f"<div class='trade-info'>Year: {y_clicked} | Trade Balance: {val:.2f}M</div>", unsafe_allow_html=True)

        evrow = events_df.query("country==@country & year==@y_clicked")
        if not evrow.empty:
            st.session_state.show_popup = True
            st.session_state.popup_content = {
                "year": y_clicked,
                "description": evrow["event_description"].iloc[0]
            }

# popup markup
if st.session_state.show_popup and st.session_state.popup_content:
    pc = st.session_state.popup_content
    st.markdown(f"""
    <div class='popup-container show'>
      <div class='popup-title'>Historical Event ({pc['year']})</div>
      <div class='popup-description'>{pc['description']}</div>
      <button class='close-button' onclick="window.parent.postMessage({{'closePopup':true}}, '*')">Close</button>
    </div>""", unsafe_allow_html=True)

# clear if closed
st.experimental_set_query_params()  # hack to reset on rerun

# ─────────────────────────────────────────────────────────────────────────────
# 📊 Section 2: Top Trading Partners by Year
st.markdown("---")
st.markdown("### 🌍 2. India’s Top Trading Partners by Year")
col1, col2, col3 = st.columns([1,6,1])
with col2:
    year = st.selectbox(
        "Select Year",
        options=sorted(trade_df["financial_year(start)"].unique()),
        index=sorted(trade_df["financial_year(start)"].unique()).index(st.session_state.selected_year),
        key="yr",
        help="Pick a year to see India’s top partners."
    )
    st.session_state.selected_year = year

# aggregate & bubble
ty = trade_df[trade_df["financial_year(start)"]==year]
agg = (
    ty.groupby("country")
      .agg(import_sum=("import","sum"), export_sum=("export","sum"))
      .assign(total_trade=lambda d: d.import_sum+d.export_sum)
      .reset_index()
)
agg["imports_billion"] = agg.import_sum/1000
agg["exports_billion"] = agg.export_sum/1000
agg["total_trade_billion"] = agg.total_trade/1000
top6 = agg.nlargest(6, "total_trade")

fig2 = px.scatter(
    top6, x="country", y="total_trade_billion", size="total_trade_billion",
    color="country", size_max=60, labels={"total_trade_billion":"Total Trade (B USD)"},
    title=f"Top 6 Trading Partners (FY {year})",
    color_discrete_sequence=px.colors.sequential.Blues_r
)
fig2.update_traces(
    marker=dict(line=dict(color="#333333", width=1.5)),
    hovertemplate="<b>%{x}</b><br>Total Trade: %{y:.1f}B<extra></extra>"
)
fig2.update_layout(plot_bgcolor="#F0F8FF",paper_bgcolor="#F0F8FF",margin=dict(t=60,b=40))

evt2 = st.plotly_chart(fig2, use_container_width=True, on_select="rerun")

# handle clicks → show trade popup
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
            "balance": row.exports_billion-row.imports_billion
        }

if st.session_state.show_trade_popup and st.session_state.trade_popup_content:
    tp = st.session_state.trade_popup_content
    st.markdown(f"""
    <div class='trade-popup-container show'>
      <div class='popup-title'>Trade with {tp['country']} (FY {year})</div>
      <div class='popup-description'>
        Imports: ${tp['imports']:.2f}B<br>
        Exports: ${tp['exports']:.2f}B<br>
        Balance: ${tp['balance']:.2f}B
      </div>
      <button class='close-button'>Close</button>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data sources: Export/Import CSV & historical events CSV. © Your Organization")
