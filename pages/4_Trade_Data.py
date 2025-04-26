import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Military Trade Dashboard", layout="wide")

# ----- CSS & SESSION STATE FOR POPUPS -----
st.markdown("""
<style>
.popup-container {
    background: linear-gradient(135deg, #E6F0FA, #FFFFFF);
    border-radius: 10px;
    padding: 20px;
    width: 400px; max-width: 90%;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-top: 20px;
    opacity: 0; animation: fadeIn 0.3s ease-out forwards;
    font-family: 'Arial', sans-serif;
}
.trade-popup-container {
    background: linear-gradient(135deg, #F0FFF4, #FFFFFF);
    border-radius: 10px;
    padding: 20px;
    width: 400px; max-width: 90%;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-top: 20px;
    opacity: 0; animation: fadeIn 0.3s ease-out forwards;
    font-family: 'Arial', sans-serif;
}
@keyframes fadeIn {
    0% { opacity:0; transform:translateY(10px); }
    100% { opacity:1; transform:translateY(0); }
}
.popup-title { font-size:22px; font-weight:bold; color:#1E3A8A; margin-bottom:10px; }
.popup-description { font-size:14px; color:#4B5563; line-height:1.6; }
.trade-info { font-size:16px; color:#1E3A8A; font-weight:bold; margin-top:10px; }
.close-button {
    display:block; margin:20px auto 0; padding:8px 20px;
    background-color:#1E3A8A; color:white; border:none; border-radius:5px;
    cursor:pointer; font-size:14px; transition:background-color 0.3s;
}
.close-button:hover { background-color:#1E40AF; }
</style>
""", unsafe_allow_html=True)

for key in ("show_popup","popup_content","show_trade_popup","trade_popup_content"):
    if key not in st.session_state:
        st.session_state[key] = False if "show" in key else None


# ----- LOAD DATA -----
@st.cache_data
def load_trade():
    df = pd.read_csv("data/exports_imports_cleaned.csv")
    df['year'] = df['financial_year(start)'].astype(int)
    return df

@st.cache_data
def load_events():
    return pd.read_csv("data/trade_events_updated2.csv", encoding="latin-1")

trade_df = load_trade()
events_df = load_events()


# ===== SECTION 1: SINGLE-COUNTRY TRADE BALANCE & POPUP =====
st.header("🛡️ Trade Balance Trend by Country")
country = st.selectbox("Select a country:", sorted(trade_df['country'].unique()))
cd = trade_df[trade_df['country']==country]

fig = px.bar(
    cd, x='year', y='trade_balance',
    color='trade_balance',
    color_continuous_scale=['#E6F0FA','#ADD8E6','#4682B4'],
    labels={'trade_balance':'Trade Balance (Mil USD)','year':'Year'},
    title=f"Trade Balance Trend for {country}"
)
fig.update_layout(plot_bgcolor='#F0F8FF', paper_bgcolor='#F0F8FF', xaxis_tickangle=45, showlegend=False)
fig.update_traces(hovertemplate="<b>Year</b>: %{x}<br><b>Balance</b>: %{y:.2f}M<extra></extra>")

# capture click
chart = st.plotly_chart(fig, use_container_width=True, key="balance_chart")

# mimic click-event handling
if chart:
    # Streamlit doesn't give click API directly; use workaround:
    if st.session_state.get("clicked_year"):
        year = st.session_state.pop("clicked_year")
    else:
        # no click
        year = None

if year:
    row = cd[cd['year']==year]
    if not row.empty:
        tb = row['trade_balance'].iloc[0]
        st.markdown(f"**Year: {year} | Trade Balance: {tb:.2f}M**")
        ev = events_df[(events_df['country']==country)&(events_df['year']==year)]
        if not ev.empty:
            st.session_state.show_popup = True
            st.session_state.popup_content = ev.iloc[0]['event_description']

if st.session_state.show_popup:
    desc = st.session_state.popup_content
    st.markdown(f"""
    <div class='popup-container'>
      <div class='popup-title'>Historical Event ({year})</div>
      <div class='popup-description'>{desc}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Close Popup"):
        st.session_state.show_popup = False


st.markdown("---")


# ===== SECTION 2: COMPARATIVE EXPORTS & IMPORTS =====
st.header("📊 Compare Countries’ Exports & Imports")
num = st.slider("Number of countries to compare:", 2, 5, 2)
defaults = ["United States","China","Russia","India"]
sel = []
for c in defaults:
    if c in trade_df['country'].unique() and len(sel)<num:
        sel.append(c)
while len(sel)<num:
    for c in trade_df['country'].unique():
        if c not in sel:
            sel.append(c)
            break

countries = st.multiselect("Select countries:", sorted(trade_df['country'].unique()), default=sel)
if 2 <= len(countries) <= 5:
    comp = trade_df[trade_df['country'].isin(countries)]
    # Exports line
    fig_exp = px.line(
        comp, x='year', y='export', color='country', markers=True,
        labels={'export':'Exports (Mil USD)','year':'Year'},
        title="Exports Over Time"
    )
    fig_exp.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig_exp, use_container_width=True)
    # Imports line
    fig_imp = px.line(
        comp, x='year', y='import', color='country', markers=True,
        labels={'import':'Imports (Mil USD)','year':'Year'},
        title="Imports Over Time"
    )
    fig_imp.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig_imp, use_container_width=True)

    summary = (
        comp.groupby('country')
            .agg(Exports=('export','sum'), Imports=('import','sum'))
            .assign(Balance=lambda d: d.Exports - d.Imports)
            .reset_index()
    )
    st.subheader("Overall Trade Balances")
    cols = st.columns(len(summary))
    for col,row in zip(cols,summary.itertuples()):
        status = "Surplus" if row.Balance>=0 else "Deficit"
        col.metric(row.country, f"${row.Balance:,.0f}M", status)
else:
    st.warning("Select between 2 and 5 countries.")
    
st.markdown("---")


# ===== SECTION 3: INDIA’S TOP-10 PARTNERS WITH TRADE POPUP =====
st.header("🌐 India’s Top-10 Trading Partners")
yr = st.selectbox("Select FY year:", sorted(trade_df['year'].unique()))
ind = trade_df[(trade_df['country']=='India') & (trade_df['year']==yr)]
# assume partner column is 'partner'
sum_ind = (
    ind.groupby('partner')
       .agg(Imports=('import','sum'), Exports=('export','sum'))
       .assign(Total=lambda d: d.Imports+d.Exports)
       .reset_index()
)
top10 = sum_ind.nlargest(10,'Total')

fig_bub = px.scatter(
    top10, x='partner', y='Total', size='Total', color='Total',
    labels={'partner':'Country','Total':'Total Trade (Mil USD)'},
    title=f"India’s Top-10 Partners (FY {yr})",
    color_continuous_scale='Blues'
)
fig_bub.update_layout(xaxis_tickangle=45)
fig_bub.update_traces(hovertemplate="<b>%{x}</b><br>Total: %{y:.2f}M<extra></extra>")

chart2 = st.plotly_chart(fig_bub, use_container_width=True, key="bubble_chart")

# handle bubble clicks
if chart2:
    if st.session_state.get("clicked_partner"):
        p = st.session_state.pop("clicked_partner")
    else:
        p = None

if p:
    r = sum_ind[sum_ind['partner']==p].iloc[0]
    st.session_state.show_trade_popup = True
    st.session_state.trade_popup_content = {
        'partner':p,
        'imports':r.Imports/1000,   # convert to B USD
        'exports':r.Exports/1000,
        'balance':(r.Exports-r.Imports)/1000
    }

if st.session_state.show_trade_popup:
    c = st.session_state.trade_popup_content
    st.markdown(f"""
    <div class='trade-popup-container'>
      <div class='popup-title'>Trade Details with {c['partner']} (FY {yr})</div>
      <div class='popup-description'>
        Imports: ${c['imports']:.3f}B<br>
        Exports: ${c['exports']:.3f}B<br>
        Balance: ${c['balance']:.3f}B
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Close Trade Popup"):
        st.session_state.show_trade_popup = False
