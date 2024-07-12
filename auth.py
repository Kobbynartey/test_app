import streamlit as st
from PIL import Image
import os
from app import chat_interface

# CSS styles
css = """
<style>
body {
    font-family: Arial, sans-serif;
}
.stButton > button {
    width: 100%;
    border-radius: 20px;
    background-color: #FF4B4B;
    color: white;
    border: none;
    padding: 10px 0;
}
.stTextInput > div > div > input {
    border-radius: 20px;
}
.google-button {
    background-color: white !important;
    color: black !important;
    border: 1px solid #ccc !important;
}
.centered {
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
"""

def welcome_page():
    st.markdown("<h1 style='text-align: center;'>Maverick Chatbot</h1>", unsafe_allow_html=True)
    
    image_path = "get_started.png"
    
    if os.path.exists(image_path):
        image = Image.open(image_path)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image(image, width=300, use_column_width=True)
    else:
        st.error(f"Image not found at path: {image_path}")
    
    if st.button("Get Started"):
        st.session_state.page = 'login'
        st.rerun()

def login_page():
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>Welcome to<br>Maverick Chatbot</h1>", unsafe_allow_html=True)
    
    st.text_input("Email Address")
    st.text_input("Password", type="password")
    
    if st.button("Sign In"):
        st.success("Logged in successfully!")
        st.session_state.authenticated = True
        st.rerun()
    
    st.markdown("<div style='text-align: center;'>Don't have an account? <a href='#' onclick='navigateToRegister()'>Register</a></div>", unsafe_allow_html=True)
    
    # JavaScript to handle navigation
    st.markdown("""
    <script>
    function navigateToRegister() {
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'register'}, '*');
    }
    </script>
    """, unsafe_allow_html=True)

def register_page():
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>Welcome to<br>Maverick Chatbot</h1>", unsafe_allow_html=True)
    
    st.text_input("Email Address")
    st.text_input("Password", type="password")
    
    if st.button("Register"):
        st.success("Registered successfully!")
    
    st.markdown("<div style='text-align: center;'>Already have an account? <a href='#' onclick='navigateToLogin()'>Login</a></div>", unsafe_allow_html=True)
    
    # JavaScript to handle navigation
    st.markdown("""
    <script>
    function navigateToLogin() {
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'login'}, '*');
    }
    </script>
    """, unsafe_allow_html=True)

def auth_main():
    st.set_page_config(page_title="Maverick Chatbot")
    st.markdown(css, unsafe_allow_html=True)

    if 'page' not in st.session_state:
        st.session_state.page = 'welcome'
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # Handle navigation from JavaScript
    if st.session_state.get('streamlit:setComponentValue') == 'register':
        st.session_state.page = 'register'
        del st.session_state['streamlit:setComponentValue']
    elif st.session_state.get('streamlit:setComponentValue') == 'login':
        st.session_state.page = 'login'
        del st.session_state['streamlit:setComponentValue']

    if st.session_state.authenticated:
        chat_interface()
    else:
        if st.session_state.page == 'welcome':
            welcome_page()
        elif st.session_state.page == 'login':
            login_page()
        elif st.session_state.page == 'register':
            register_page()

if __name__ == "__main__":
    auth_main()