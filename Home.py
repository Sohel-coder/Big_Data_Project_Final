import streamlit as st

# 1) Page config
st.set_page_config(
    page_title="🎖️ Art of War",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2) Inject CSS for background, transparency & text alignment
st.markdown(
    """
    <style>
    /* ── Full-screen fixed background ── */
    .stApp {
        background: url('https://media.istockphoto.com/id/1287561722/photo/camouflage-cloth-texture-abstract-background-and-texture-for-design.jpg?s=612x612&w=0&k=20&c=MrNR7xi7ZByp3YZkDmDHxcNO6XQzMBM_3MB_Stvc7jw=')
                    no-repeat center center fixed;
        background-size: cover;
    }

    /* ── Sidebar semi-transparent ── */
    section[data-testid="stSidebar"] > div:first-child {
        background-color: rgba(0, 0, 0, 0.5) !important;
    }

    /* ── Page content containers transparent ── */
    .css-1d391kg, /* sidebar content wrapper */
    .css-1outpf7, /* main content wrapper */
    .css-18e3th9 { /* main view container */
        background-color: transparent !important;
    }

    /* ── Right-align everything in the main area ── */
    .css-18e3th9 > div {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center;
        height: 100%;
    }

    /* ── Title styling ── */
    .welcome-title {
        color: #FFD700;
        font-size: 3.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        margin: 0 !important;
    }

    /* ── Subtitle styling ── */
    .welcome-subtitle {
        color: #EEE;
        font-size: 1.2rem;
        line-height: 1.6;
        margin-top: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3) Content
st.markdown(
    """
    <div style="padding:4rem; max-width:600px;">
      <h1 class="welcome-title">🎖️ Art of War</h1>
      <p class="welcome-subtitle">
        Welcome to the Military Data Analysis Platform!<br>
        Explore global defence budgets, military strengths, trade flows, and more—all in one place.
      </p>
    </div>
    """,
    unsafe_allow_html=True
)
