import streamlit as st

st.set_page_config(page_title="Polybius", layout="wide")

# load css file 
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("Style/Home.css")

# home page layout and button styling
st.markdown("""
    <style>
    .stButton>button {
        border: none;
        border-bottom: 1px solid grey;
        padding: 10px 0; 
        width: 60%;  /* responsiveness */
        max-width: 300px;  
        margin: 10px auto;  
        display: block; 
    }

    @media (max-width: 768px) {
        .stButton>button {
            width: 80%;  
        }
    }

    @media (max-width: 480px) {
        .stButton>button {
            width: 100%;  
        }
    }
    </style>
""", unsafe_allow_html=True)  

# using columns for layout 
col1, col2, col3 = st.columns(3)

with col1:
    pass

# content in center column
with col2:
    st.markdown("<h1 style='text-align: center;'>POLYBIUS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: grey;'>The Employment Platform</h3>", unsafe_allow_html=True)
    
    if st.button("LOGIN"):
        st.switch_page("pages/Login.py")
    if st.button("CREATE NEW ACCOUNT"):
        st.switch_page("pages/Register.py")

with col3:
    pass

# Footer Section
st.markdown("""
    <div style="text-align: center; color: grey; margin-top: 80px;">
        <p>POLYBIUS is an all-in-one employment platform for job seekers and employers of all types. Our state-of-the-art services include:</p>
        <p>Resume Creation and Assistance &nbsp; | &nbsp; Automated Job Matching &nbsp; | &nbsp; Job Listing Aggregation &nbsp; | &nbsp; Personalized Candidate Lineup &nbsp; | &nbsp; Candidate Evaluations</p>
    </div>
""", unsafe_allow_html=True)