# Home.py
import streamlit as st

# wide layout, collapsed by default
st.set_page_config(
    page_title="🎖️ Art of War",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# inject all our custom CSS
st.markdown(
    """
    <style>
    /* ── Full-screen background ── */
    .stApp {
        background: url('https://media.istockphoto.com/id/690203250/photo/us-army-ranger-close-up.jpg?s=612x612&w=0&k=20&c=jBkQ9AV1WgjcJ4PChNVelJ6LY8SpVxe-uQDD2NjLdsE=')
                    no-repeat center center fixed;
        background-size: cover;    /* fill without tiling or distortion */
    }

    /* ── Semi-transparent sidebar ── */
    [data-testid="stSidebar"] > div:first-child {
        background-color: rgba(0, 0, 0, 0.4) !important;
    }

    /* ── Title styling ── */
    .welcome-title {
        color: #FFD700;
        font-size: 4rem;
        font-weight: 700;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        margin-bottom: 1rem;
    }

    /* ── Subtitle styling ── */
    .welcome-subtitle {
        color: #EEE;
        font-size: 1.2rem;
        line-height: 1.6;
        margin-bottom: 2rem;
    }

    /* ── Navigation list styling ── */
    .nav-list {
        list-style: none;
        padding-left: 0;
    }
    .nav-list li {
        margin: 0.5rem 0;
        font-size: 1.1rem;
        color: #FFF;
        padding-left: 1.5rem;
        position: relative;
    }
    .nav-list li:before {
        content: "⚔️";
        position: absolute;
        left: 0;
    }
    .nav-list li:hover {
        color: #FFD700;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# (optional) an overlay if you want extra dimming:
# st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)

# right-aligned content container
st.markdown('<div style="text-align:right; padding:4rem 2rem;">', unsafe_allow_html=True)

# title & subtitle
st.markdown(
    '<h1 class="welcome-title">🎖️ Art of War</h1>', unsafe_allow_html=True
)
st.markdown(
    '<p class="welcome-subtitle">'
    'Welcome to the Military Data Analysis Platform!<br>'
    'Explore global defence budgets, military strengths, trade flows, and more—all in one place.'
    '</p>',
    unsafe_allow_html=True,
)

st.markdown('</div>', unsafe_allow_html=True)
