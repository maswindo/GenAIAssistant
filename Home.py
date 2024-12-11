import streamlit as st
import atexit

# Set page config to have a title
st.set_page_config(page_title="Home", layout="centered")

# Apply custom styles
st.markdown("""
    <style>
        body {
            text-align: center;
            font-family: Arial, sans-serif;
        }
        h1 {
            font-size: 4rem;
            font-weight: bold;
        }
        p {
            color: grey;
            font-size: 1.25rem;
        }
        
    </style>
    """, unsafe_allow_html=True)

# Display the header
st.markdown("<h1>Gen-AI based multimodel user profile generator</h1>", unsafe_allow_html=True)

# Sub-header with emoji
st.markdown("<p>We use Generative AI and advanced data analytics to help you unlock your full career potential.</p>", unsafe_allow_html=True)

# Create button
if st.button('Get Started'):
    st.switch_page("pages/Register.py")
if st.button('Login'):
    st.switch_page("pages/Login.py")

def clear_cache_on_exit():
    print("Clearing Cache...")
    st.cache_data.clear()

atexit.register(clear_cache_on_exit)