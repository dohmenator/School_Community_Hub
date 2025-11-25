import streamlit as st
import directory_page # Imports the code that defines your Groups Page

# --- Basic App Configuration (Sprint 1: The Skeleton) ---
st.set_page_config(
    page_title="Dohmens School Hub",
    page_icon="🏫",
    layout="wide"
)

# --- Navigation Bar (Simple Placeholder) ---
# In a full Streamlit app, this automatically renders in the sidebar.
st.sidebar.title("Dohmens Hub Navigation")
st.sidebar.markdown("---")
if st.sidebar.button("Home"):
    st.session_state.current_page = "home"
if st.sidebar.button("Clubs Directory"):
    st.session_state.current_page = "directory"
if st.sidebar.button("Master Calendar"):
    st.session_state.current_page = "calendar" # Future Sprint 3

# Initialize page state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# --- Page Routing ---
if st.session_state.current_page == "home":
    st.title("🏫 Welcome to the Dohmens Community Hub!")
    st.markdown("Use the navigation on the left to find clubs and view the calendar.")
    
elif st.session_state.current_page == "directory":
    # This calls the function in directory_page.py to display the directory list
    directory_page.show_directory() 
    
elif st.session_state.current_page == "calendar":
    st.title("📅 Master Calendar (Coming in Sprint 3)")
    st.warning("This page is under construction.")
    