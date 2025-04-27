import streamlit as st

st.set_page_config(
    page_title="🎖️ Art of War",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS
st.markdown(
    """
    <style>
    /* Full-screen app container with centered native-size background */
    .stApp {
        background: url('https://static.vecteezy.com/system/resources/previews/027/103/278/non_2x/silhouette-soldiers-descend-from-helicopter-warning-of-danger-against-a-sunset-background-with-space-for-text-promoting-peace-and-cessation-of-hostilities-free-photo.jpg')
                    no-repeat center center fixed;
        background-size: cover;  /* show at native resolution, fully visible */
    }

    /* Make sidebar slightly translucent so the background peeks through */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.6);
    }

    /* Right-aligned hero text */
    .css-1lcbmhc {  /* you may need to adjust this selector to match your Streamlit version */
        text-align: center !important;
        padding: 1rem 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Your rest of Home.py content…
st.markdown("<h1>🎖️ Art of War</h1>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="
        position: relative;
        padding: 4rem 2rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        background: linear-gradient(135deg, #0D1B2A 0%, #1B263B 100%);
        ">
      <!-- Semi-transparent overlay card -->
      <div style="
          display: inline-block;
          max-width: 800px;
          background: rgba(255,255,255,0.1);
          backdrop-filter: blur(8px);
          border-radius: 12px;
          padding: 2rem 3rem;
      ">
        <h1 style="
            font-size: 3rem;
            margin-bottom: 0.5rem;
            letter-spacing: 1px;
        ">
          🎖️ Military Data Analysis Platform
        </h1>
        <p style="
            font-size: 1.2rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        ">
          Embark on a journey through the unseen dynamics of global defense.<br>
          Discover the pulse of nations — from soaring defense budgets and military might<br>
          to the intricate webs of trade and alliances. Dive deep into data,<br>
          uncover hidden patterns, and explore the forces shaping our world — all in one place.
        </p>
        <a href="#Defence Budget" style="
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: #FFD700;
            color: #0D1B2A;
            font-weight: bold;
            border-radius: 8px;
            text-decoration: none;
            transition: background 0.3s ease;
        " onmouseover="this.style.background='#FFC300';" onmouseout="this.style.background='#FFD700';">
          🚀 Get Started
        </a>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)
