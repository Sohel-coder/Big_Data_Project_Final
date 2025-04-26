import streamlit as st


st.set_page_config(
    page_title="Acknowledgements",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS
st.markdown(
    """
    <style>
    /* Full-screen app container with centered native-size background */
    .stApp {
        background: url('https://media.istockphoto.com/id/1277600467/photo/silhouette-of-combatants-against-sky.jpg?s=612x612&w=0&k=20&c=oDYkEh1pJo8eyrsgEocHs7tWGM_DfcCigUPsg7XOym4=')
                    no-repeat right center fixed;
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

st.title(headline)
st.markdown("""
""", unsafe_allow_html=False)
st.markdown("""
**The success of this project is attributed to the dedication, expertise, 
and collaborative efforts of all the team members of Group 8**
""", unsafe_allow_html=False)

st.markdown("""
""", unsafe_allow_html=False)
st.markdown("""**Abhijeet Shravansing Rajput**""",unsafe_allow_html=False)
st.markdown("""**Abhinandan Singh Baghel**""",unsafe_allow_html=False)
st.markdown("""**Devansh Dhaval Mehta**""",unsafe_allow_html=False)
st.markdown("""**Divya Sharma**""",unsafe_allow_html=False)
st.markdown("""**Kamal Kant Tripathi**""",unsafe_allow_html=False)
st.markdown("""**Patel Ujjaval Girishbhai**""",unsafe_allow_html=False)
st.markdown("""**Sohel Samirkhan Modi**""",unsafe_allow_html=False)
st.markdown("""**Vihsal Kumar**""",unsafe_allow_html=False)
