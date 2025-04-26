import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns

st.set_page_config(page_title="Defense Companies Analysis", layout="wide")

st.title("Defense Companies Analysis")
st.markdown(
    """
    This section provides insights into the world's leading defense companies, their revenue trends,
    and market positions over time.
    """
)


# Load defense companies dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/defence_companies_from_2005_final.csv")

defense_companies = load_data()

st.markdown(
    """
    This section provides insights into the world's leading defense companies, their revenue trends, 
    and market positions over time.
    """
)

try:
    # Most recent data
    latest_year = defense_companies['Year'].max()
    latest_data = defense_companies[defense_companies['Year'] == latest_year]

    # Selection
    st.subheader("Select Companies for Analysis")
    companies = sorted(defense_companies['Company'].unique())
    countries = sorted(defense_companies['Country'].unique())
    col1, col2 = st.columns(2)
    with col1:
        selected_companies = st.multiselect(
            "Select companies:", options=companies,
            default=latest_data.nlargest(3, 'Defense_Revenue_From_A_Year_Ago')['Company'].tolist()
        )
    with col2:
        selected_countries = st.multiselect(
            "Filter by country:", options=countries, default=[]
        )
    # Filter
    data = defense_companies.copy()
    if selected_companies:
        data = data[data['Company'].isin(selected_companies)]
    if selected_countries:
        data = data[data['Country'].isin(selected_countries)]

    if data.empty:
        st.warning("No data for selected criteria.")
    else:
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "Revenue Analysis", "Historical Trends", "Geographic Distribution", "Defense Revenue Share"
        ])

        with tab1:
            top10 = latest_data if not selected_companies else latest_data[latest_data['Company'].isin(selected_companies)]
            fig = px.bar(
                top10, x='Defense_Revenue_From_A_Year_Ago', y='Company', orientation='h',
                color='Country', title=f'Defense Revenue by Company ({latest_year})'
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = px.line(
                data, x='Year', y='Defense_Revenue_From_A_Year_Ago',
                color='Company', title='Historical Revenue Trends'
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            geo = latest_data.groupby('Country')['Defense_Revenue_From_A_Year_Ago'].sum().reset_index()
            fig = px.pie(
                geo, values='Defense_Revenue_From_A_Year_Ago', names='Country',
                title='Geographic Distribution of Defense Revenue'
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab4:
            fig = px.scatter(
                latest_data, x='Total Revenue', y='Defense_Revenue_From_A_Year_Ago',
                size='%of Revenue from Defence', color='Country', hover_name='Company',
                title='Defense vs Total Revenue Share'
            )
            st.plotly_chart(fig, use_container_width=True)

        # Company-specific metrics
        if selected_companies:
            st.subheader("Company-Specific Metrics")
            cols = st.columns(min(len(selected_companies), 3))
            for i, comp in enumerate(selected_companies):
                row = latest_data[latest_data['Company']==comp].iloc[0]
                with cols[i]:
                    st.metric(comp, f"${row['Defense_Revenue_From_A_Year_Ago']:,.0f}M",
                              f"{row['%of Revenue from Defence']:.1f}% of total")
                    st.write(f"Country: {row['Country']}")

except Exception as e:
    st.error(f"Error loading defense companies data: {e}")
