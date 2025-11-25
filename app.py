# app.py (Updated)

import streamlit as st
import directory_page 
import detail_page # <-- NEW: Import the detail page module

# --- Basic App Configuration ---
st.set_page_config(
    page_title="Dohmens School Hub",
    page_icon="🏫",
    layout="wide"
)

# --- Navigation Bar ---
st.sidebar.title("Dohmens Hub Navigation")
st.sidebar.markdown("---")
if st.sidebar.button("Home"):
    st.session_state.current_page = "home"
if st.sidebar.button("Clubs Directory"):
    st.session_state.current_page = "directory"
if st.sidebar.button("Master Calendar"):
    st.session_state.current_page = "calendar" 

# Initialize page state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# --- Page Routing ---
if st.session_state.current_page == "home":
    st.title("🏫 Welcome to the Dohmens Community Hub!")
    st.markdown("Use the navigation on the left to find clubs and view the calendar.")
    
elif st.session_state.current_page == "directory":
    directory_page.show_directory() 
    
elif st.session_state.current_page == "detail": # <-- NEW: Route to the detail page
    detail_page.show_group_detail()
    
elif st.session_state.current_page == "calendar":
    st.title("📅 Master Calendar (Coming in Sprint 3)")
    st.warning("This page is under construction.")