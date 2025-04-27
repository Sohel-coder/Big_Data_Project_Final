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
        background-image: url('https://static.vecteezy.com/system/resources/previews/027/103/278/non_2x/silhouette-soldiers-descend-from-helicopter-warning-of-danger-against-a-sunset-background-with-space-for-text-promoting-peace-and-cessation-of-hostilities-free-photo.jpg');
        background-attachment: fixed;
        background-size: cover;
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
st.markdown("""**Vishal Kumar**""",unsafe_allow_html=False)
