import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from PIL import Image
import base64
import os
import plotly.express as px
import plotly.graph_objects as go
import country_converter as coco

st.set_page_config(page_title="Trade Data", layout="wide")

st.title("Military Trade Data Analysis")

st.write("""
This section provides insights into the military trade data of various countries, including exports, imports, and trade balances.
You can analyze the data for a single country or compare multiple countries.
""")


# Helper function to ensure dataframes are Arrow-compatible
def make_arrow_compatible(df):
    """Convert all columns to string to avoid Arrow conversion issues."""
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Convert all non-numeric columns to string
    for col in df_copy.columns:
        if df_copy[col].dtype == 'object':
            df_copy[col] = df_copy[col].astype(str)
        # For numeric columns containing mixed data, also convert to string
        elif col != 'Year' and col != 'Metric':
            try:
                # Try to format numbers nicely
                df_copy[col] = df_copy[col].apply(
                    lambda x: "{:,}".format(int(x)) if isinstance(x, (int, float)) and abs(x) >= 1 and not pd.isna(x)
                    else (f"{x:.2f}" if isinstance(x, (int, float)) and not pd.isna(x) 
                          else ("N/A" if pd.isna(x) else str(x)))
                )
            except:
                # If that fails, just convert to string
                df_copy[col] = df_copy[col].astype(str)
    
    return df_copy



# Load datasets
@st.cache_data
def load_data():
    exports_imports = pd.read_csv("data/exports_imports_cleaned.csv")
    return exports_imports

exports_imports = load_data()

    
# Add option for single country analysis or comparative analysis
analysis_type = st.radio("Select Analysis Type:", ["Single Country Analysis", "Comparative Analysis"])

if analysis_type == "Single Country Analysis":
    # Show data summary
    st.subheader("Data Overview")
    st.dataframe(make_arrow_compatible(exports_imports.head(10)))
    
    # Select country for analysis
    countries = sorted(exports_imports['country'].unique().tolist())
    selected_country = st.selectbox("Select a country:", countries)
    
    # Filter data for the selected country
    country_data = exports_imports[exports_imports['country'] == selected_country]
    
    if not country_data.empty:
        st.subheader(f"Military Trade Analysis for {selected_country}")
        
        # Get time range for which we have data
        years = sorted(country_data['financial_year(end)'].unique().tolist())
        
        # Create time series data
        trade_data = []
        for _, row in country_data.iterrows():
            year = row['financial_year(end)']
            exports = row['export'] if pd.notna(row['export']) else 0
            imports = row['import'] if pd.notna(row['import']) else 0
            
            trade_data.append({
                'Year': year,
                'Exports (USD millions)': exports,
                'Imports (USD millions)': imports,
                'Trade Balance (USD millions)': exports - imports
            })
        
        trade_df = pd.DataFrame(trade_data)
        
        # Create multiline chart for exports and imports
        st.subheader(f"Military Exports and Imports Trend for {selected_country}")
        
        # Create figure with dual y-axis
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Plot exports
        ax1.plot(trade_df['Year'], trade_df['Exports (USD millions)'], 'b-', marker='o', linewidth=2, label='Exports')
        ax1.plot(trade_df['Year'], trade_df['Imports (USD millions)'], 'r-', marker='s', linewidth=2, label='Imports')
        
        # Set labels and title
        ax1.set_xlabel('Year')
        ax1.set_ylabel('USD Millions')
        ax1.tick_params(axis='y')
        ax1.grid(True, alpha=0.3)
        plt.xticks(trade_df['Year'], rotation=45)
        plt.title(f"Military Exports and Imports for {selected_country}")
        plt.legend(loc='upper left')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Display trade balance chart
        st.subheader(f"Trade Balance for {selected_country}")
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        bars = sns.barplot(x='Year', y='Trade Balance (USD millions)', data=trade_df, ax=ax2)
        
        # Add value labels
        for i, bar in enumerate(bars.patches):
            ax2.text(
                bar.get_x() + bar.get_width()/2.,
                bar.get_height() + 0.5 if bar.get_height() >= 0 else bar.get_height() - 50,
                f"${trade_df['Trade Balance (USD millions)'].iloc[i]:.1f}M",
                ha='center',
                va='bottom' if bar.get_height() >= 0 else 'top'
            )
        
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.title(f"Military Trade Balance for {selected_country}")
        plt.tight_layout()
        st.pyplot(fig2)
        
        # Display stats
        total_exports = trade_df['Exports (USD millions)'].sum()
        total_imports = trade_df['Imports (USD millions)'].sum()
        overall_balance = total_exports - total_imports
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Exports", f"${total_exports:,.0f}M")
        col2.metric("Total Imports", f"${total_imports:,.0f}M")
        col3.metric("Overall Balance", f"${overall_balance:,.0f}M", 
                    delta="Surplus" if overall_balance > 0 else "Deficit")
        
        # Display recent data table
        st.subheader("Year-by-Year Data")
        st.dataframe(make_arrow_compatible(trade_df), use_container_width=True)
else:  # Comparative Analysis
    st.subheader("Compare Military Trade Data Between Countries")
    
    # Get list of all countries
    countries = sorted(exports_imports['country'].unique().tolist())
    
    # Allow user to select number of countries to compare
    num_countries = st.slider("Number of countries to compare:", min_value=2, max_value=5, value=2)
    
    # Create multiselect for countries with default values for major countries
    default_countries = []
    major_countries = ['United States', 'Russia', 'China', 'France', 'Germany', 'United Kingdom', 'Israel', 'Italy']
    
    for country in major_countries:
        if country in countries and len(default_countries) < num_countries:
            default_countries.append(country)
    
    # Fill with other countries if needed
    while len(default_countries) < num_countries and len(default_countries) < len(countries):
        for country in countries:
            if country not in default_countries:
                default_countries.append(country)
                break
    
    # Create multiselect for countries
    selected_countries = st.multiselect(
        "Select countries to compare:",
        options=countries,
        default=default_countries[:num_countries]
    )
    
    # Check if we have the right number of countries selected
    if len(selected_countries) < 2:
        st.warning("Please select at least 2 countries for comparison.")
    elif len(selected_countries) > 5:
        st.warning("Please select at most 5 countries for comparison.")
    else:
        # Prepare data for selected countries
        comparison_data = []
        
        for country in selected_countries:
            country_data = exports_imports[exports_imports['country'] == country]
            
            if not country_data.empty:
                # Get export and import data for each year
                for _, row in country_data.iterrows():
                    year = row['financial_year(end)']
                    exports = row['export'] if pd.notna(row['export']) else 0
                    imports = row['import'] if pd.notna(row['import']) else 0
                    
                    comparison_data.append({
                        'Country': country,
                        'Year': year,
                        'Exports (USD millions)': exports,
                        'Imports (USD millions)': imports,
                        'Trade Balance (USD millions)': exports - imports
                    })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
            # Group the data for analysis
            total_by_country = comparison_df.groupby('Country').agg({
                'Exports (USD millions)': 'sum',
                'Imports (USD millions)': 'sum'
            }).reset_index()
            
            total_by_country['Trade Balance (USD millions)'] = total_by_country['Exports (USD millions)'] - total_by_country['Imports (USD millions)']
            total_by_country['Net Exporter'] = total_by_country['Trade Balance (USD millions)'] > 0
            
            # Use a color palette based on number of countries
            if len(selected_countries) <= 3:
                palette = "Set1"
            else:
                palette = "Set2"
            
            # Create export comparison chart
            st.subheader("Military Exports Comparison")
            fig1, ax1 = plt.subplots(figsize=(12, 6))
            sns.lineplot(
                data=comparison_df, 
                x='Year', 
                y='Exports (USD millions)', 
                hue='Country',
                marker='o',
                palette=palette,
                ax=ax1
            )
            plt.title('Military Exports Comparison')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.legend(title="Country", bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            st.pyplot(fig1)
            
            # Create import comparison chart
            st.subheader("Military Imports Comparison")
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            sns.lineplot(
                data=comparison_df, 
                x='Year', 
                y='Imports (USD millions)', 
                hue='Country',
                marker='o',
                palette=palette,
                ax=ax2
            )
            plt.title('Military Imports Comparison')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.legend(title="Country", bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            st.pyplot(fig2)
            
            # Display total metrics
            st.subheader("Overall Trade Summary")
            
            # Create metrics for each country
            metrics_cols = st.columns(len(selected_countries))
            for i, country in enumerate(selected_countries):
                country_summary = total_by_country[total_by_country['Country'] == country]
                if not country_summary.empty:
                    with metrics_cols[i]:
                        exports = country_summary['Exports (USD millions)'].iloc[0]
                        imports = country_summary['Imports (USD millions)'].iloc[0]
                        balance = country_summary['Trade Balance (USD millions)'].iloc[0]
                        status = "Surplus" if balance > 0 else "Deficit"
                        
                        st.metric(f"{country}", f"${balance:,.0f}M", status)
                        st.write(f"Exports: ${exports:,.0f}M")
                        st.write(f"Imports: ${imports:,.0f}M")
            
            # Create comparison bar chart
            st.subheader("Total Military Trade Balance")
            
            fig3, ax3 = plt.subplots(figsize=(12, 6))
            bars = sns.barplot(
                x='Country', 
                y='Trade Balance (USD millions)', 
                data=total_by_country,
                palette=palette,
                ax=ax3
            )
            
            # Add value labels
            for i, bar in enumerate(bars.patches):
                ax3.text(
                    bar.get_x() + bar.get_width()/2.,
                    bar.get_height() + 100 if bar.get_height() >= 0 else bar.get_height() - 100,
                    f"${total_by_country['Trade Balance (USD millions)'].iloc[i]:,.0f}M",
                    ha='center',
                    va='bottom' if bar.get_height() >= 0 else 'top'
                )
            
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            plt.grid(True, alpha=0.3)
            plt.title('Total Military Trade Balance by Country')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig3)
            
            # Create stacked bar chart for exports vs imports
            st.subheader("Exports vs Imports by Country")
            
            # Reshape data for stacked bar chart
            stacked_data = []
            for _, row in total_by_country.iterrows():
                stacked_data.append({
                    'Country': row['Country'],
                    'Type': 'Exports',
                    'Amount (USD millions)': row['Exports (USD millions)']
                })
                stacked_data.append({
                    'Country': row['Country'],
                    'Type': 'Imports',
                    'Amount (USD millions)': row['Imports (USD millions)']
                })
            
            stacked_df = pd.DataFrame(stacked_data)
            
            fig4, ax4 = plt.subplots(figsize=(12, 6))
            sns.barplot(
                x='Country', 
                y='Amount (USD millions)', 
                hue='Type',
                data=stacked_df,
                palette=['forestgreen', 'indianred'],
                ax=ax4
            )
            plt.title('Military Exports vs Imports by Country')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45, ha='right')
            plt.legend(title="")
            plt.tight_layout()
            st.pyplot(fig4)
            
            # Create heatmap for year-by-year exports
            if len(selected_countries) >= 2:
                st.subheader("Year-by-Year Export Comparison")
                
                # Create pivot table for heatmap
                export_pivot = comparison_df.pivot(index='Country', columns='Year', values='Exports (USD millions)')
                
                # Create heatmap
                fig5, ax5 = plt.subplots(figsize=(14, len(selected_countries) * 0.8))
                
                # Format values for display
                annotations = export_pivot.map(lambda x: f'${x:,.0f}M' if pd.notna(x) and x != 0 else 'No data')
                
                # Create the heatmap
                heatmap = sns.heatmap(
                    export_pivot, 
                    annot=annotations, 
                    fmt='', 
                    cmap='YlGnBu',
                    linewidths=.5, 
                    ax=ax5
                )
                plt.title('Military Exports by Country and Year (USD millions)')
                plt.tight_layout()
                st.pyplot(fig5)
        else:
            st.write("No trade data available for the selected countries.")
