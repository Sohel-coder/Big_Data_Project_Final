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
        background: url('https://media.istockphoto.com/id/1287083951/photo/full-length-portrait-of-an-army-soldier-in-full-military-gear-helmet-glasses-and-mask.jpg?s=612x612&w=0&k=20&c=t7a2Bg6n90dHFZjtpLHxgzl3rVrrdEPL2i9hQZ9rluc=')
                    no-repeat center center fixed;
        background-size: contain;  /* show at native resolution, fully visible */
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
    "<p>Welcome to the Military Data Analysis Platform!<br>"
    "Explore : <br>"
    "Global defence budgets <br>" 
    "Military strengths <br>"
    Trade flows and more all in one place.</p>",
    
    unsafe_allow_html=True
)
