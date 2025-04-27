import streamlit as st
import pandas as pd

# ——— Load the one dataset we need for stats ———
@st.cache_data
def load_data():
    return pd.read_csv("data/2024_military_strength_by_country.csv")

military_strength = load_data()

# ——— Page config ———
st.set_page_config(page_title="Art of War – Welcome", layout="wide")

# ——— Welcome-page CSS ———
st.markdown("""
<style>
    .welcome-container {
        background: linear-gradient(rgba(255,255,255,0.95), rgba(255,255,255,0.95)),
                    url('https://www.armyrecognition.com/images/stories/north_america/united_states/military_equipment/uh-60_black_hawk/UH-60_Black_Hawk_United_States_US_American_army_aviation_helicopter_001.jpg');
        background-size: cover;
        background-position: center;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .welcome-title {
        color: #1a237e;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .welcome-text {
        color: #333;
        font-size: 1.2rem;
        line-height: 1.6;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px,1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    .stat-card {
        background: rgba(255,255,255,0.9);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a237e;
        margin-bottom: 0.5rem;
    }
    .stat-label {
        color: #555;
        font-size: 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ——— Compute statistics ———
st.markdown('<div class="welcome-container">', unsafe_allow_html=True)
st.markdown('<h1 class="welcome-title">Military Data Analysis Platform</h1>', unsafe_allow_html=True)
st.markdown('<p class="welcome-text">Explore global military strengths, budgets, and trends through interactive analysis.</p>', unsafe_allow_html=True)

total_countries = military_strength['country'].nunique()
filtered = military_strength.sort_values('pwr_index').query("country != 'Afghanistan'")
top_power = filtered.iloc[0]['country'] if not filtered.empty else "N/A"

try:
    total_budget = filtered['national_annual_defense_budgets'].dropna().astype(float).sum()
    formatted_budget = f"${total_budget/1e12:.2f}T"
except:
    formatted_budget = "Unavailable"

# ——— Stats cards ———
st.markdown('<div class="stats-container">', unsafe_allow_html=True)
st.markdown(f'''
    <div class="stat-card">
      <div class="stat-value">{total_countries}</div>
      <div class="stat-label">Countries Analyzed</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{top_power}</div>
      <div class="stat-label">Top Military Power</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{formatted_budget}</div>
      <div class="stat-label">Total Defense Spending</div>
    </div>
''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
