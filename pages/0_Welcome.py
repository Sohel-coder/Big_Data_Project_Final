import streamlit as st
st.set_page_config(page_title="Welcome to the Art of War", layout="wide")

import pandas as pd

@st.cache_data
def load_strength():
    return pd.read_csv("data/2024_military_strength_by_country.csv")

military_strength = load_strength()

# ——— Custom CSS ———
st.markdown("""
<style>
  /* Hero section */
  .welcome-container {
    position: relative;
    background: linear-gradient(rgba(255,255,255,0.9), rgba(255,255,255,0.9)),
                url('https://www.armyrecognition.com/images/stories/north_america/united_states/military_equipment/uh-60_black_hawk/UH-60_Black_Hawk_United_States_US_American_army_aviation_helicopter_001.jpg')
                center/cover no-repeat;
    border-radius: 12px;
    padding: 3rem;
    margin-bottom: 2rem;
    box-shadow: 0 6px 18px rgba(0,0,0,0.2);
  }
  .welcome-title {
    font-size: 3rem;
    color: #1E3A8A;
    font-weight: 700;
    text-align: center;
    margin-bottom: 1rem;
  }
  .welcome-text {
    font-size: 1.2rem;
    color: #333;
    text-align: center;
    max-width: 800px;
    margin: 0 auto 2rem;
    line-height: 1.6;
  }

  /* Stats cards */
  .stats-container {
    display: grid;
    grid-template-columns: repeat(auto-fit,minmax(200px,1fr));
    gap: 1rem;
    margin: 2rem 0;
  }
  .stat-card {
    background: #fff;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform .2s;
  }
  .stat-card:hover {
    transform: translateY(-4px);
  }
  .stat-value {
    font-size: 2.2rem;
    color: #1E3A8A;
    font-weight: 700;
    margin-bottom: .5rem;
  }
  .stat-label {
    font-size: 1rem;
    color: #555;
    font-weight: 500;
  }

  /* Feature grid */
  .feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit,minmax(240px,1fr));
    gap: 1.5rem;
    margin: 3rem 0;
  }
  .feature-card {
    background: #fff;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transition: transform .2s;
    border-left: 4px solid #4F46E5;
  }
  .feature-card:hover {
    transform: translateY(-4px);
  }
  .feature-title {
    font-size: 1.2rem;
    color: #4F46E5;
    font-weight: 600;
    margin-bottom: .5rem;
  }
  .feature-desc {
    font-size: 0.95rem;
    color: #444;
    line-height: 1.4;
  }

  /* Button */
  .get-started {
    display: block;
    background: linear-gradient(135deg,#4F46E5,#1E40AF);
    color: #fff !important;
    text-align: center;
    padding: .75rem 2rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1.1rem;
    margin: 2rem auto 0;
    width: 200px;
    cursor: pointer;
    transition: background .2s;
    text-decoration: none;
  }
  .get-started:hover {
    background: linear-gradient(135deg,#1E40AF,#4F46E5);
  }
</style>
""", unsafe_allow_html=True)

# ——— Hero ———
st.markdown('<div class="welcome-container">', unsafe_allow_html=True)
st.markdown('<h1 class="welcome-title">Military Data Analysis Platform</h1>', unsafe_allow_html=True)
st.markdown('''
  <p class="welcome-text">
    Explore comprehensive analysis of global military powers, defense budgets, and international trade data
    through interactive visualizations and detailed comparisons.
  </p>
''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ——— Compute stats ———
total_countries = military_strength['country'].nunique()
fs = military_strength.query("country != 'Afghanistan'").sort_values('pwr_index')
top_power = fs.iloc[0]['country'] if not fs.empty else "N/A"
try:
    total_budget = fs['national_annual_defense_budgets'].astype(float).sum()
    formatted_budget = f"${total_budget/1e12:.2f}T"
except:
    formatted_budget = "Unavailable"

# ——— Stats cards ———
st.markdown('<div class="stats-container">', unsafe_allow_html=True)
for val, label in [
    (total_countries, "Countries Analyzed"),
    (top_power, "Top Military Power"),
    (formatted_budget, "Global Defense Spending")
]:
    st.markdown(f'''
      <div class="stat-card">
        <div class="stat-value">{val}</div>
        <div class="stat-label">{label}</div>
      </div>
    ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ——— Feature grid ———
st.markdown('<h2 style="text-align:center;color:#1E3A8A;margin-top:2rem;">What You Can Do</h2>', unsafe_allow_html=True)
st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
for title, desc in [
    ("Military Strength Comparison",
     "Compare personnel, equipment & power index across countries."),
    ("Defense Budget Trends",
     "Visualize military spend as % of GDP over time."),
    ("Defense Companies",
     "Analyze top contractors & their market share."),
    ("Trade Data",
     "Explore global arms export/import flows."),
    ("2047 Forecast",
     "See projected top military powers by mid-century.")
]:
    st.markdown(f'''
      <div class="feature-card">
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{desc}</div>
      </div>
    ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ——— Get Started button ———
if st.button("Begin Analysis"):
    st.experimental_set_query_params(page="strength")
