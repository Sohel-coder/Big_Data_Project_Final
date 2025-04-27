import streamlit as st
import pandas as pd

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎖️ Art of War – Welcome",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── DATA LOAD ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_strength():
    # adjust path as needed
    return pd.read_csv("data/2024_military_strength_by_country.csv")

military_strength = load_strength()

# ─── GLOBAL STATS ──────────────────────────────────────────────────────────────
total_countries = len(military_strength)
# pick a top power for display
filtered = military_strength.sort_values('pwr_index', ascending=True)
top_power = filtered.iloc[0]['country'] if not filtered.empty else "N/A"

try:
    total_budget = (
        pd.to_numeric(filtered['national_annual_defense_budgets'], errors='coerce')
        .sum()
    )
    formatted_budget = f"${total_budget/1e12:.2f}T"
except:
    formatted_budget = "Data unavailable"

st.markdown(
    """
    <style>
    /* Full-screen war-scene background */
    .stApp {
      background: url('https://as1.ftcdn.net/v2/jpg/08/06/91/92/1000_F_806919202_HHI0NY4rRWARQm8FX12WHFL1gZRGs3jR.jpg')
                  no-repeat center center fixed;
      background-size: cover;
    }
    /* Translucent sidebar (if you ever re-enable it) */
    [data-testid="stSidebar"] {
      background-color: rgba(0, 0, 0, 0.6);
    }
    /* Centered hero text */
    .css-1lcbmhc {
      text-align: center !important;
      padding: 1rem !important;
    }

    /* Theme colors */
    :root {
      --primary-color: #1E3A8A;
      --text-color: white;
      --accent-color: #4F46E5;
    }

    /* Welcome “card” */
    .welcome-container {
      background-color: rgba(0,0,0,0.3);
      border-radius: 15px;
      padding: 2rem;
      margin: 2rem auto;
      max-width: 800px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .welcome-title {
      color: var(--primary-color);
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 1rem;
    }

    .welcome-text {
      color: var(--text-color);
      font-size: 1.2rem;
      line-height: 1.6;
      margin-bottom: 2rem;
    }

    /* Stats grid */
    .stats-container {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px,1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }
    .stat-card {
      background: rgba(0,0,0,0.3);    /* make this translucent */
      padding: 1.5rem;
      border-radius: 10px;
      text-align: center;
      box-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    .stat-value {
      font-size: 2rem;
      font-weight: 700;
      color: var(--primary-color);
      margin-bottom: 0.5rem;
    }
    .stat-label {
      color: var(--text-color);
      font-weight: 500;
    }

    /* Feature grid */
    .feature-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px,1fr));
      gap: 1.5rem;
    }
    .feature-card {
      background: rgba(0,0,0,0.3);    /* make this translucent */
      padding: 1.5rem;
      border-radius: 10px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.8);
      border-left: 4px solid var(--accent-color);
      transition: transform 0.3s ease;
    }
    .feature-card:hover {
      transform: translateY(-5px);
    }
    .feature-title {
      color: var(--primary-color);
      font-size: 1.3rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
    }
    .feature-description {
      color: var(--text-color);
      font-size: 1rem;
      line-height: 1.4;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# ─── WELCOME LAYOUT ────────────────────────────────────────────────────────────
st.markdown('<div class="welcome-container">', unsafe_allow_html=True)

st.markdown(
    '<h1 class="welcome-title">🎖️ Art of War – Military Data Analysis</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="welcome-text">'
    'Explore global defense budgets, military strengths, trade flows, and more—'
    'all in one place.'
    '</p>',
    unsafe_allow_html=True,
)

# Stats
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
    <div class="stat-label">Global Defense Spending</div>
  </div>
''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Features
st.markdown('<h2 style="text-align:center; color:var(--primary-color);">What You Can Explore</h2>', unsafe_allow_html=True)
st.markdown(
    '''
    <div class="feature-grid">
      <div class="feature-card">
        <div class="feature-title">Military Strength</div>
        <div class="feature-description">
          Compare personnel, equipment and power indices across countries.
        </div>
      </div>
      <div class="feature-card">
        <div class="feature-title">Defense Budgets</div>
        <div class="feature-description">
          Track spending trends over time (% of GDP & absolute).
        </div>
      </div>
      <div class="feature-card">
        <div class="feature-title">Trade Data</div>
        <div class="feature-description">
          Visualize arms exports & imports globally.
        </div>
      </div>
      <div class="feature-card">
        <div class="feature-title">2047 Projections</div>
        <div class="feature-description">
          See predicted top military powers based on current trajectories.
        </div>
      </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

# “Get started” button (navigates to main page)
if st.button("🔍 Begin Analysis", use_container_width=True):
    st.experimental_set_query_params(page="Military Strength")

st.markdown('</div>', unsafe_allow_html=True)
