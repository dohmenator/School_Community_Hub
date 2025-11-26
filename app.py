# app.py (Updated for Auth)

import streamlit as st
import directory_page 
import detail_page 
import calendar_page 
import auth_manager
from datetime import datetime
import profile_page

# --- Initialize AuthManager ---
auth = auth_manager.AuthManager()

# --- Basic App Configuration ---
st.set_page_config(
    page_title="Dohmens School Hub",
    page_icon="🏫",
    layout="wide"
)

# --- Navigation Bar ---
st.sidebar.title("Dohmens Hub Navigation")
st.sidebar.markdown("---")

# Conditional navigation based on login status
if auth.is_logged_in():
    st.sidebar.write(f"Welcome, {auth.get_current_user().get('full_name', 'User')}!")
    if st.sidebar.button("Home"):
        st.session_state.current_page = "home"
    if st.sidebar.button("Clubs Directory"):
        st.session_state.current_page = "directory"
    if st.sidebar.button("Master Calendar"):
        st.session_state.current_page = "calendar" 
    if st.sidebar.button("My Profile"):
        st.session_state.current_page = "profile"
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", type="secondary"):
        auth.sign_out()
        st.session_state.current_page = "home" # Redirect to home after logout
        st.rerun()
else: # Not logged in
    st.sidebar.markdown("Please log in to access full features.")
    st.sidebar.markdown("---")
    # Login Form in Sidebar
    with st.sidebar.form("login_form"):
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        login_submitted = st.form_submit_button("Login")

        if login_submitted:
            if auth.sign_in(email, password):
                st.success("Logged in successfully!")
                st.session_state.current_page = "home" # Redirect after successful login
                st.rerun()
            else:
                st.error(st.session_state['auth_error']) # Display specific error

    st.sidebar.markdown("---")
    if st.sidebar.button("Create Account"):
        st.session_state.current_page = "signup"
    
# Initialize page state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# --- Main Content Area ---
if st.session_state.current_page == "home":
    st.title("🏫 Welcome to the Dohmens Community Hub!")
    if not auth.is_logged_in():
        st.info("Log in or create an account to access the full features.")
    else:
        st.markdown("Use the navigation on the left to find clubs, view the calendar, or manage your profile.")
    
elif st.session_state.current_page == "directory":
    directory_page.show_directory() 
    
elif st.session_state.current_page == "detail":
    detail_page.show_group_detail()
    
elif st.session_state.current_page == "calendar":
    calendar_page.show_calendar()

elif st.session_state.current_page == "signup":
    st.title("Sign Up for the Dohmens Community Hub")
    st.markdown("---")
    with st.form("signup_form"):
        st.subheader("Create Your Account")
        new_email = st.text_input("Email *", key="signup_email")
        new_password = st.text_input("Password *", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password *", type="password", key="confirm_password")
        full_name = st.text_input("Full Name *", key="signup_full_name")
        grad_year = st.number_input("Graduation Year (e.g., 2025)", min_value=1900, max_value=2100, step=1, value=datetime.now().year + 4, key="signup_grad_year")
        
        signup_submitted = st.form_submit_button("Create Account")

        if signup_submitted:
            if not (new_email and new_password and confirm_password and full_name):
                st.error("Please fill in all required fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                if auth.sign_up(new_email, new_password, full_name, grad_year):
                    st.success("Account created successfully! You are now logged in.")
                    st.session_state.current_page = "home" # Redirect after successful signup
                    st.rerun()
                else:
                    st.error(st.session_state['auth_error'])

elif st.session_state.current_page == "profile":
    profile_page.show_profile_page()

else:
    st.error("Page not found.")


