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

# Load data first
trade_df = pd.read_csv("data/exports_imports_cleaned.csv")
events_df = pd.read_csv("data/trade_events_updated2.csv", encoding="latin-1")

# Initialize session state for both popups and selected year
if 'show_popup' not in st.session_state:
    st.session_state['show_popup'] = False
if 'popup_content' not in st.session_state:
    st.session_state['popup_content'] = None
if 'show_trade_popup' not in st.session_state:
    st.session_state['show_trade_popup'] = False
if 'trade_popup_content' not in st.session_state:
    st.session_state['trade_popup_content'] = None
if 'selected_year' not in st.session_state:
    st.session_state['selected_year'] = sorted(trade_df['financial_year(start)'].unique())[0]  # Default to first year

# Centered Country Selection
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.header("Select a Country")
    selected_country = st.selectbox("", options=sorted(trade_df["country"].unique()), index=0, help="Choose a country to view its trade balance trends")

# Filter trade data for selected country and add a 'year' column
country_trade_df = trade_df[trade_df['country'] == selected_country].copy()
country_trade_df['year'] = country_trade_df['financial_year(start)'].astype(int)

# Bar Chart: Trade Balance Over Time
st.subheader(f"Trade Balance Trend for {selected_country}")
fig = px.bar(
    country_trade_df,
    x='year',
    y='trade_balance',
    color='trade_balance',
    color_continuous_scale=['#E6F0FA', '#ADD8E6', '#87CEEB', '#4682B4', '#1E40AF'],  # Blue gradient
    labels={'trade_balance': 'Trade Balance (Mil USD)', 'year': 'Year'},
    title=f"Trade Balance Trend for {selected_country}"
)
fig.update_traces(
    marker_line_color='#333333',
    marker_line_width=1.5,
    opacity=0.9,
    hovertemplate='<b>Year</b>: %{x}<br><b>Trade Balance</b>: %{y:.2f}M<extra></extra>'
)
fig.update_layout(
    xaxis=dict(
        title='Year',
        tickangle=45,
        title_font=dict(size=14, color='#333333'),
        tickfont=dict(size=12, color='#333333')
    ),
    yaxis=dict(
        title='Trade Balance (Mil USD)',
        title_font=dict(size=14, color='#333333'),
        tickfont=dict(size=12, color='#333333'),
        zeroline=True,
        zerolinecolor='#333333',
        gridcolor='#E0E0E0'
    ),
    plot_bgcolor='#F0F8FF',
    paper_bgcolor='#F0F8FF',
    title_font_size=20,
    font=dict(color='#333333', size=12),
    margin=dict(l=50, r=50, t=60, b=60),
    showlegend=False
)

# Render bar chart with click event capture
event = st.plotly_chart(fig, use_container_width=True, key="trade_balance_chart", on_select="rerun")

# Handle click events for the bar chart and display historical event popup
if event:
    points = event.get("selection", {}).get("points")
    if points:
        year_clicked = int(points[0]["x"])
        trade_row = country_trade_df[country_trade_df['year'] == year_clicked]
        if not trade_row.empty:
            trade_balance = trade_row['trade_balance'].iloc[0]
            st.markdown(f"<div class='trade-info'>Year: {year_clicked} | Trade Balance: {trade_balance:.2f}M</div>", unsafe_allow_html=True)

            event_row = events_df[(events_df['country'] == selected_country) & (events_df['year'] == year_clicked)]
            if not event_row.empty:
                event_description = event_row['event_description'].iloc[0]
                st.session_state['show_popup'] = True
                st.session_state['popup_content'] = {
                    'year': year_clicked,
                    'description': event_description
                }

# Display historical event popup
if st.session_state['show_popup'] and st.session_state['popup_content']:
    popup_content = st.session_state['popup_content']
    st.markdown(
        f"""
        <div class='popup-container'>
            <div class='popup-title'>Historical Event ({popup_content['year']})</div>
            <div class='popup-description'>{popup_content['description']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Close Popup", key="close_popup_btn"):
        st.session_state['show_popup'] = False
        st.session_state['popup_content'] = None
        st.rerun()

# Clear historical popup on rerun if not triggered
if not st.session_state['show_popup']:
    st.markdown("<style>.popup-container { display: none; }</style>", unsafe_allow_html=True)

# Year selection dropdown
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.subheader("Select Year")
    selected_year = st.selectbox("", options=sorted(trade_df['financial_year(start)'].unique()), index=sorted(trade_df['financial_year(start)'].unique()).index(st.session_state['selected_year']), key="year_select", help="Choose a year to view top trading partners")
    st.session_state['selected_year'] = selected_year  # Update session state

# Filter trade data for selected year and calculate dynamic trade partners
trade_year_df = trade_df[trade_df['financial_year(start)'] == st.session_state['selected_year']]
trade_summary = trade_year_df.groupby('country').agg({
    'import': 'sum',
    'export': 'sum'
}).reset_index()
trade_summary['total_trade'] = trade_summary['import'] + trade_summary['export']
trade_summary['imports_billion'] = trade_summary['import'] / 1000  # Convert to billion USD
trade_summary['exports_billion'] = trade_summary['export'] / 1000  # Convert to billion USD
trade_summary['total_trade_billion'] = trade_summary['total_trade'] / 1000  # Convert to billion USD
trade_summary['trade_balance_billion'] = trade_summary['exports_billion'] - trade_summary['imports_billion']
top_n = 6
trade_partners_df = trade_summary.sort_values(by='total_trade', ascending=False).head(top_n)

# Bubble Chart: Top Trading Partners for Selected Year
st.subheader(f"India's Top Trading Partners (FY {st.session_state['selected_year']})")
fig_bubble = px.scatter(
    trade_partners_df,
    x='country',
    y='total_trade_billion',
    size='total_trade_billion',
    color='country',
    color_discrete_sequence=px.colors.sequential.Blues_r,  # Blue color scheme
    title=f"India's Top Trading Partners (FY {st.session_state['selected_year']})",
    size_max=60,
    hover_data=['total_trade_billion']
)
fig_bubble.update_traces(
    marker=dict(line=dict(color='#333333', width=1.5)),
    hovertemplate='<b>%{x}</b><br>Total Trade: $%{y}B<extra></extra>'
)
fig_bubble.update_layout(
    xaxis=dict(
        title='Country',
        title_font=dict(size=14, color='#333333'),
        tickfont=dict(size=12, color='#333333')
    ),
    yaxis=dict(
        title='Total Trade (Billion USD)',
        title_font=dict(size=14, color='#333333'),
        tickfont=dict(size=12, color='#333333'),
        gridcolor='#E0E0E0'
    ),
    plot_bgcolor='#F0F8FF',
    paper_bgcolor='#F0F8FF',
    title_font_size=20,
    font=dict(color='#333333', size=12),
    margin=dict(l=50, r=50, t=60, b=60),
    showlegend=True
)

# Render bubble chart with click event capture
bubble_event = st.plotly_chart(fig_bubble, use_container_width=True, key="bubble_chart", on_select="rerun")

# Handle click events for the bubble chart and display trade popup
if bubble_event:
    points = bubble_event.get("selection", {}).get("points")
    if points:
        country_clicked = points[0]["x"]
        trade_row = trade_partners_df[trade_partners_df['country'] == country_clicked]
        if not trade_row.empty:
            st.session_state['show_trade_popup'] = True
            st.session_state['trade_popup_content'] = {
                'country': country_clicked,
                'imports': trade_row['imports_billion'].iloc[0],
                'exports': trade_row['exports_billion'].iloc[0],
                'trade_balance': trade_row['trade_balance_billion'].iloc[0]
            }

# Display trade details popup
if st.session_state['show_trade_popup'] and st.session_state['trade_popup_content']:
    trade_popup_content = st.session_state['trade_popup_content']
    st.markdown(
        f"""
        <div class='trade-popup-container'>
            <div class='popup-title'>Trade Details with {trade_popup_content['country']} (FY {st.session_state['selected_year']})</div>
            <div class='popup-description'>
                Imports: ${trade_popup_content['imports']}B<br>
                Exports: ${trade_popup_content['exports']}B<br>
                Trade Balance: ${trade_popup_content['trade_balance']}B
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Close Trade Popup", key="close_trade_popup_btn"):
        st.session_state['show_trade_popup'] = False
        st.session_state['trade_popup_content'] = None
        st.rerun()

# Clear trade popup on rerun if not triggered
if not st.session_state['show_trade_popup']:
    st.markdown("<style>.trade-popup-container { display: none; }</style>", unsafe_allow_html=True)
