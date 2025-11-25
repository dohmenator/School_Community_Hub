# detail_page.py

import streamlit as st
# Imports the DatabaseManager from your new separate file
from database_manager import DatabaseManager
from typing import Optional, Dict, Any, List
import pandas as pd

@st.cache_data(show_spinner="Fetching club details...")
def get_group_data(org_id: str):
    """Fetches the organization and its full roster for the detail page."""
    db_manager = DatabaseManager()
    
    # 1. Fetch Organization Data (Header/About Section)
    org_data = db_manager.get_organization_by_id(org_id)
    
    # 2. Fetch Membership Data (Roster Section)
    # This uses the JOIN query to get user details linked to the membership
    roster_data = db_manager.get_memberships_for_org(org_id)
    
    return org_data, roster_data

def show_group_detail():
    """Implements the Group Detail Page wireframe."""
    
    # Retrieve the ID of the organization selected from the directory page
    org_id = st.session_state.get('selected_org_id')

    if not org_id:
        st.error("Error: No organization selected.")
        st.session_state.current_page = "directory"
        st.rerun()
        return

    # Fetch all data using the cached function
    org, roster_raw = get_group_data(org_id)
    
    if not org:
        st.error(f"Organization with ID {org_id} not found.")
        st.session_state.current_page = "directory"
        st.rerun()
        return

    # ====================================================================
    # 1. HEADER AND BASIC INFO
    # ====================================================================
    col_title, col_edit = st.columns([5, 1])
    
    with col_title:
        st.title(org.get('name', 'Group Name N/A'))
        st.caption(f"Category: **{org.get('category', 'Uncategorized')}**")

    # Placeholder for future "Edit" button
    with col_edit:
        st.button("⚙️ Edit Page", key="edit_btn", disabled=True, help="Requires user authentication (Sprint 4)")
    
    st.markdown("---")

    # ====================================================================
    # 2. ABOUT AND CONTACT SECTION
    # ====================================================================
    st.subheader("About Us")
    st.info(org.get('description', 'No detailed description available.'))
    
    col_meeting, col_advisor = st.columns(2)
    
    with col_meeting:
        st.markdown("**📅 Meeting Information:**")
        st.markdown(org.get('meeting_info', 'Not yet scheduled.'))

    with col_advisor:
        st.markdown("**🧑‍🏫 Faculty Advisor:**")
        st.markdown(org.get('advisor_name', 'TBD'))
        
    st.markdown("---")

    # ====================================================================
    # 3. ROSTER SECTION (MEMBERSHIP LOGIC)
    # ====================================================================
    st.subheader("Club Leadership & Roster")
    
    if roster_raw:
        # Reformat the roster data for display
        roster_formatted = []
        for item in roster_raw:
            # The user details are nested inside the 'users' key due to the Supabase join
            user = item.get('users', {})
            roster_formatted.append({
                "Role": item.get('role', 'Member').title(), 
                "Name": user.get('full_name', 'Unknown User'),
                "Email": user.get('email', 'N/A'),
                "Status": f"Class of {user.get('grad_year')}" if user.get('grad_year') else user.get('role', 'N/A').title()
            })

        # Convert to Pandas DataFrame for nice display
        roster_df = pd.DataFrame(roster_formatted)
        
        # Display the roster table
        st.dataframe(roster_df, 
                     use_container_width=True, 
                     hide_index=True,
                     column_order=("Role", "Name", "Status"), # Order the columns for presentation
                     column_config={
                         "Email": st.column_config.Column(label="Email (Admin View)", disabled=True) # Hide email by default
                     }
                    )
    else:
        st.info("The roster is currently empty.")

    # ====================================================================
    # 4. ANNOUNCEMENTS AND EVENTS (Future Sprint)
    # ====================================================================
    st.markdown("---")
    st.subheader("Upcoming Events & Announcements (Sprint 3)")
    st.warning("Event and announcement feeds are scheduled for the next development sprint.")
    
    # Button to return to the directory
    if st.button("Back to Directory"):
        st.session_state.current_page = "directory"
        st.session_state.selected_org_id = None # Clear the selection
        st.rerun()