import streamlit as st

def add_custom_css():
    st.markdown(
        """
        <style>
        .custom-subheader {
            color: grey;        
            font-size: 18px;     
            margin-bottom: 0px;  
        }

        h1, h2, h3, h4, h5, h6 {
            margin-top: -20px;
            margin-bottom: -35px; 
        }

        .stTextInput {
            width: 300px; 
        }

        </style>
        """,
        unsafe_allow_html=True
    )

add_custom_css()

# temporary hard coded company data for ui display
def get_company_data():
    return {
        "name": "Google",
        "industry": "Software Development",
        "website": "https://about.google",
        "logo": "https://lh3.googleusercontent.com/COxitqgJr1sJnIDe8-jiKhxDx1FrYbtRHKJ9z_hELisAlapwE9LUPh6fcXIfb5vwpbMl4xl9H9TRFPc5NOO8Sb3VSgIBrfRYvW6cUA",
        "mission": "To organize the world’s information and make it universally accessible and useful. Google emphasizes focus on organizing vast amounts of information and making it available to everyone, which has guided their development of search engines, cloud computing, advertising technologies, and more.",
        "values": {
            "Focus on the user": "Focus on the user and all else will follow.",
            "Do one thing well": "It’s best to do one thing really, really well.",
            "Fast is better": "Fast is better than slow.",
            "No evil": "You can make money without doing evil.",
            "Always more info": "There’s always more information out there."
        },
        "headquarters": "Googleplex - Mountain View, California, USA"
    }

# get company data
company = get_company_data()

#---------------------------COMPANY DATA---------------------------------

# Display company logo 
st.image(company["logo"], width=100) 

# columns for layout 
col1, col2 = st.columns([3, 1])

with col1:
    # Display company data
    st.header(company["name"])
    st.markdown(f'<div class="custom-subheader">{company["industry"]}</div>', unsafe_allow_html=True)
    st.write(f"[{company['website']}]({company['website']})")

with col2:
    job_title = st.text_input("", placeholder="Enter Job Title                                             ⚲")
                                                                                 
 


st.subheader("Company Overview")


st.write("**Mission:**")
st.write(company["mission"])


st.write("**Values:**")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.write(f" **{list(company['values'].keys())[0]}**")
    st.write(f"  {list(company['values'].values())[0]}")

with col2:
    st.write(f" **{list(company['values'].keys())[1]}**")
    st.write(f"  {list(company['values'].values())[1]}")

with col3:
    st.write(f" **{list(company['values'].keys())[2]}**")
    st.write(f"  {list(company['values'].values())[2]}")

with col4:
    st.write(f" **{list(company['values'].keys())[3]}**")
    st.write(f"  {list(company['values'].values())[3]}")

with col5:
    st.write(f" **{list(company['values'].keys())[4]}**")
    st.write(f"  {list(company['values'].values())[4]}")


st.write("**Global Headquarters**")
st.write(company["headquarters"])


st.markdown('</div>', unsafe_allow_html=True)