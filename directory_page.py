import streamlit as st
from typing import List, Dict, Any, Optional
# IMPORT FROM YOUR NEW FILE: 
# This line assumes you created database_manager.py and put the class there.
from database_manager import DatabaseManager 

# --- Data Fetching and Caching ---

@st.cache_data
def get_data_for_directory():
    """Initializes DB Manager and fetches data, caching the result."""
    # DatabaseManager now initializes and loads config from .env file inside its __init__
    db_manager = DatabaseManager() 
    
    # We only need the get_org_directory method for this page
    return db_manager.get_org_directory()

# --- Page Rendering ---

def show_directory():
    """Implements the Groups Page (Directory List) wireframe."""
    st.title("📚 Clubs, Teams, and Organizations Directory")
    
    # 1. Fetch Data
    org_data = get_data_for_directory()
    
    if not org_data:
        st.info("No organizations found in the database yet.")
        return

    # 2. Search Bar and Category Filters (Top Row)
    col1, col2 = st.columns([3, 1])
    
    # Create the set of unique categories for filtering
    # If a club has no category, it will appear as None/null, so we handle that:
    all_categories = sorted(list(set(org.get('category') for org in org_data if org.get('category'))))
    
    # Search Bar
    search_query = col1.text_input("Search Clubs by Name", key="search").lower()
    
    # Category Filter Dropdown
    selected_category = col2.selectbox("Filter by Category", 
                                        options=['All'] + all_categories, 
                                        key="filter")

    # 3. Filter Logic
    filtered_orgs = []
    for org in org_data:
        # Filter by category (Handles potential None category)
        category_match = (selected_category == 'All') or (org.get('category') == selected_category)
        
        # Filter by search query
        search_match = search_query in org['name'].lower()
        
        if category_match and search_match:
            filtered_orgs.append(org)
            
    # 4. Display the Directory List (Grid Layout for Cards)
    st.markdown("---")
    
    # Use st.columns to create a card-like grid (e.g., 3 columns)
    cols = st.columns(3)
    
    if not filtered_orgs:
        st.info("No clubs match your current filter and search criteria.")
    
    for index, org in enumerate(filtered_orgs):
        col = cols[index % 3] # Cycle through the three columns
        
        with col:
            # Organization Card Wireframe Implementation
            with st.container(border=True): # Gives the card a distinct border
                
                # Title
                st.subheader(f"🌐 {org['name']}")
                
                # Category Tag 
                st.caption(f"Category: **{org.get('category', 'N/A')}**")
                
                # Verification Status
                if org.get('is_verified'):
                    st.success("✅ Officially Verified", icon="⭐")
                
                # Brief Description (Show only the first 100 characters)
                description_snippet = org.get('description', 'No description provided.')
                st.markdown(f"**Description:** {description_snippet[:100]}{'...' if len(description_snippet) > 100 else ''}")
                
                # Link to Detail Page 
                if st.button(f"View Profile", key=f"btn_{org['id']}"):
                    # Sets the state to switch to the Detail Page
                    st.session_state.selected_org_id = org['id']
                    st.session_state.current_page = "detail" 
                    st.rerun()