import streamlit as st
import pandas as pd
import plotly.express as px

# Custom CSS for popups and styling
st.markdown("""
<style>
.popup-container {
    background: linear-gradient(135deg, #E6F0FA, #FFFFFF);
    border-radius: 10px;
    padding: 20px;
    width: 400px;
    max-width: 90%;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-top: 20px;
    opacity: 0;
    animation: fadeIn 0.3s ease-out forwards;
    font-family: 'Arial', sans-serif;
}
.trade-popup-container {
    background: linear-gradient(135deg, #F0FFF4, #FFFFFF);
    border-radius: 10px;
    padding: 20px;
    width: 400px;
    max-width: 90%;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-top: 20px;
    opacity: 0;
    animation: fadeIn 0.3s ease-out forwards;
    font-family: 'Arial', sans-serif;
}
@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
}
.popup-title {
    font-size: 22px;
    font-weight: bold;
    color: #1E3A8A;
    margin-bottom: 10px;
}
.popup-description {
    font-size: 14px;
    color: #4B5563;
    line-height: 1.6;
}
.trade-info {
    font-size: 16px;
    color: #1E3A8A;
    font-weight: bold;
    margin-top: 10px;
}
.close-button {
    display: block;
    margin: 20px auto 0;
    padding: 8px 20px;
    background-color: #1E3A8A;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s;
}
.close-button:hover {
    background-color: #1E40AF;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for both popups
if 'show_popup' not in st.session_state:
    st.session_state['show_popup'] = False
if 'popup_content' not in st.session_state:
    st.session_state['popup_content'] = None
if 'show_trade_popup' not in st.session_state:
    st.session_state['show_trade_popup'] = False
if 'trade_popup_content' not in st.session_state:
    st.session_state['trade_popup_content'] = None

# Load data
trade_df = pd.read_csv("data/exports_imports_cleaned.csv")
events_df = pd.read_csv("data/trade_events_updated2.csv", encoding="latin-1")

# --- Single Country Trend Section ---
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.header("Select a Country")
    selected_country = st.selectbox(
        "", 
        options=sorted(trade_df["country"].unique()), 
        index=0,
        help="Choose a country to view its trade balance trends"
    )

country_trade_df = trade_df[trade_df['country'] == selected_country].copy()
country_trade_df['year'] = country_trade_df['financial_year(start)'].astype(int)

st.subheader(f"Trade Balance Trend for {selected_country}")
fig = px.bar(
    country_trade_df,
    x='year',
    y='trade_balance',
    color='trade_balance',
    color_continuous_scale=['#E6F0FA','#ADD8E6','#87CEEB','#4682B4','#1E40AF'],
    labels={'trade_balance':'Trade Balance (Mil USD)','year':'Year'},
    title=f"Trade Balance Trend for {selected_country}"
)
fig.update_traces(
    marker_line_color='#333333',
    marker_line_width=1.5,
    opacity=0.9,
    hovertemplate='<b>Year</b>: %{x}<br><b>Trade Balance</b>: %{y:.2f}M<extra></extra>'
)
fig.update_layout(
    xaxis=dict(title='Year',tickangle=45),
    yaxis=dict(title='Trade Balance (Mil USD)',zeroline=True,gridcolor='#E0E0E0'),
    plot_bgcolor='#F0F8FF',paper_bgcolor='#F0F8FF',title_font_size=20,
    showlegend=False,margin=dict(l=50,r=50,t=60,b=60)
)

# render & capture clicks
event = st.plotly_chart(fig, use_container_width=True, key="trade_balance_chart", on_select="rerun")
if event:
    pts = event.get("selection",{}).get("points",[])
    if pts:
        year_clicked = int(pts[0]["x"])
        tr = country_trade_df[country_trade_df['year']==year_clicked]
        if not tr.empty:
            bal = tr['trade_balance'].iloc[0]
            st.markdown(f"<div class='trade-info'>Year: {year_clicked} | Trade Balance: {bal:.2f}M</div>", unsafe_allow_html=True)
            er = events_df[(events_df['country']==selected_country)&(events_df['year']==year_clicked)]
            if not er.empty:
                st.session_state['show_popup']=True
                st.session_state['popup_content']={
                    'year':year_clicked,
                    'description':er['event_description'].iloc[0]
                }

if st.session_state['show_popup'] and st.session_state['popup_content']:
    c = st.session_state['popup_content']
    st.markdown(f"""
    <div class='popup-container'>
      <div class='popup-title'>Historical Event ({c['year']})</div>
      <div class='popup-description'>{c['description']}</div>
    </div>
    """,unsafe_allow_html=True)
    if st.button("Close Popup",key="close_popup_btn"):
        st.session_state['show_popup']=False
        st.session_state['popup_content']=None
        st.rerun()

if not st.session_state['show_popup']:
    st.markdown("<style>.popup-container { display: none; }</style>", unsafe_allow_html=True)

# --- India's Top Trading Partners Bubble ---
trade_2021 = trade_df[trade_df['financial_year(start)']==2021]
summary = trade_2021.groupby('country').agg({'import':'sum','export':'sum'}).reset_index()
summary['total_trade']=summary['import']+summary['export']
summary['imports_billion']=summary['import']/1000
summary['exports_billion']=summary['export']/1000
summary['trade_balance_billion']=summary['exports_billion']-summary['imports_billion']
top6 = summary.sort_values('total_trade',ascending=False).head(6)

st.subheader("India's Top Trading Partners (FY 2021)")
fig2 = px.scatter(
    top6, x='country', y='total_trade_billion', size='total_trade_billion',
    color='country', color_discrete_sequence=px.colors.sequential.Blues_r,
    title="India's Top Trading Partners (FY 2021)", size_max=60,
    hover_data=['imports_billion','exports_billion']
)
fig2.update_traces(
    marker=dict(line=dict(color='#333333',width=1.5)),
    hovertemplate='<b>%{x}</b><br>Total Trade: %{y:.2f}B<extra></extra>'
)
fig2.update_layout(
    xaxis=dict(title='Country'), yaxis=dict(title='Total Trade (Billion USD)'),
    plot_bgcolor='#F0F8FF',paper_bgcolor='#F0F8FF',title_font_size=20,showlegend=False
)

bubble_event = st.plotly_chart(fig2, use_container_width=True, key="bubble_chart", on_select="rerun")
if bubble_event:
    pts = bubble_event.get("selection",{}).get("points",[])
    if pts:
        cty = pts[0]["x"]
        r = top6[top6['country']==cty].iloc[0]
        st.session_state['show_trade_popup']=True
        st.session_state['trade_popup_content']={
            'country':cty,
            'imports':r['imports_billion'],
            'exports':r['exports_billion'],
            'trade_balance':r['trade_balance_billion']
        }

if st.session_state['show_trade_popup'] and st.session_state['trade_popup_content']:
    t = st.session_state['trade_popup_content']
    st.markdown(f"""
    <div class='trade-popup-container'>
      <div class='popup-title'>Trade Details with {t['country']} (FY 2021)</div>
      <div class='popup-description'>
        Imports: ${t['imports']:.2f}B<br>
        Exports: ${t['exports']:.2f}B<br>
        Trade Balance: ${t['trade_balance']:.2f}B
      </div>
    </div>
    """,unsafe_allow_html=True)
    if st.button("Close Trade Popup",key="close_trade_popup_btn"):
        st.session_state['show_trade_popup']=False
        st.session_state['trade_popup_content']=None
        st.rerun()

if not st.session_state['show_trade_popup']:
    st.markdown("<style>.trade-popup-container { display: none; }</style>", unsafe_allow_html=True)

# --- Comparative Analysis Section ---
st.markdown("---")
st.subheader("Comparative Analysis: Exports & Imports Over Time")

countries = sorted(trade_df['country'].unique())
num = st.slider("Number of countries to compare", 2, 5, 2)
default = ['United States','China']
selected = st.multiselect(
    "Select countries",
    options=countries,
    default=[c for c in default if c in countries][:num]
)

if len(selected) < 2:
    st.warning("Pick at least 2 countries!")
else:
    comp = trade_df[trade_df['country'].isin(selected)].copy()
    comp['year'] = comp['financial_year(start)'].astype(int)
    # Exports
    fig_exp = px.line(
        comp, x='year', y='export', color='country',
        markers=True,
        title="Exports Over Time",
        labels={'export':'Exports (Mil USD)','year':'Year'}
    )
    fig_exp.update_layout(plot_bgcolor='#F0F8FF',paper_bgcolor='#F0F8FF')
    st.plotly_chart(fig_exp, use_container_width=True)
    # Imports
    fig_imp = px.line(
        comp, x='year', y='import', color='country',
        markers=True,
        title="Imports Over Time",
        labels={'import':'Imports (Mil USD)','year':'Year'}
    )
    fig_imp.update_layout(plot_bgcolor='#F0F8FF',paper_bgcolor='#F0F8FF')
    st.plotly_chart(fig_imp, use_container_width=True)
