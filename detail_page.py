# detail_page.py (Updated for Membership Management and Auth)

import streamlit as st
from database_manager import DatabaseManager
from auth_manager import AuthManager # <-- NEW IMPORT
from typing import Optional, Dict, Any, List
import pandas as pd

# --- Initialize AuthManager and DatabaseManager globally or pass them ---
# For simplicity, we'll initialize them inside the function as they are lightweight
# or pass them around if performance became an issue for many instances.

@st.cache_data(show_spinner="Fetching club details...")
def get_group_data(org_id: str):
    """Fetches the organization and its full roster for the detail page."""
    db_manager = DatabaseManager() # Initialize here for cache scope
    
    # 1. Fetch Organization Data (Header/About Section)
    org_data = db_manager.get_organization_by_id(org_id)
    
    # 2. Fetch Membership Data (Roster Section)
    # This uses the JOIN query to get user details linked to the membership
    roster_data = db_manager.get_memberships_for_org(org_id)
    
    return org_data, roster_data

def show_group_detail():
    """Implements the Group Detail Page wireframe with membership management."""
    
    db_manager = DatabaseManager() # Initialize DatabaseManager
    auth = AuthManager() # Initialize AuthManager

    # Retrieve the ID of the organization selected from the directory page
    org_id = st.session_state.get('selected_org_id')

    if not org_id:
        st.error("Error: No organization selected. Please go back to the Clubs Directory.")
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
        # Show edit button only to authorized users
        user_role = auth.get_user_role()
        is_admin_or_leader = user_role in ['admin', 'faculty', 'club_leader']
        st.button("⚙️ Edit Page", key="edit_btn", disabled=not is_admin_or_leader, 
                  help="Only Club Leaders, Faculty, or Admins can edit this page.")
    
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
    # 3. MEMBERSHIP MANAGEMENT (JOIN/LEAVE BUTTONS)
    # ====================================================================
    st.subheader("Membership")

    if auth.is_logged_in():
        current_user = auth.get_current_user()
        user_id = current_user['id']
        
        # Check user's membership status for this specific organization
        membership_status = db_manager.get_user_org_membership_status(user_id, org_id)

        col1_member_status, col2_member_action = st.columns(2)

        if membership_status:
            col1_member_status.success(f"You are a member ({membership_status['role'].title()}).")
            if col2_member_action.button("Leave Organization", type="secondary", key=f"leave_org_{org_id}"):
                if db_manager.leave_organization(user_id, org_id):
                    st.success("You have left the organization.")
                    st.cache_data.clear() # Clear cache to refresh roster and membership status
                    st.rerun()
                else:
                    st.error("Failed to leave organization. Please try again.") 
        else:
            col1_member_status.info("You are not currently a member.")
            if col2_member_action.button("Join Organization", type="primary", key=f"join_org_{org_id}"):
                if db_manager.join_organization(user_id, org_id):
                    st.success("You have joined the organization as a member.")
                    st.cache_data.clear() # Clear cache to refresh roster and membership status
                    st.rerun()
                else:
                    st.error("Failed to join organization. Please try again.") 
    else:
        st.info("Log in to join or manage your membership in this organization.")

    st.markdown("---")

    # ====================================================================
    # 4. ROSTER SECTION (DISPLAY MEMBERS)
    # ====================================================================
    st.subheader("Club Leadership & Roster")
    
    # Use the fresh roster_raw data
    if roster_raw:
        # Reformat the roster data for display - NOW USING FLATTENED DATA
        roster_formatted = []
        for item in roster_raw:
            # Direct access to the flattened keys
            roster_formatted.append({
                "Role": item.get('membership_role', 'Member').title(), # Access 'membership_role'
                "Name": item.get('full_name', 'Unknown User'),         # Access 'full_name' directly
                "Email": item.get('email', 'N/A'),                     # Access 'email' directly
                "Status": f"Class of {item.get('grad_year')}" if item.get('grad_year') else item.get('membership_role', 'N/A').title()
            })

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
    # 5. ANNOUNCEMENTS AND EVENTS (Future Sprint)
    # ====================================================================
    st.markdown("---")
    st.subheader("Upcoming Events & Announcements (Sprint 3)")
    st.warning("Event and announcement feeds are scheduled for the next development sprint.")
    
    # Button to return to the directory
    if st.button("⬅️ Back to Directory"): # Added an arrow for consistency
        st.session_state.current_page = "directory"
        st.session_state.selected_org_id = None # Clear the selection
        st.rerun()

    # Leader Tools Section (moved to bottom for clarity)
    user_role_global = auth.get_user_role()
    is_leader_or_admin = user_role_global in ['admin', 'faculty', 'club_leader']
    if is_leader_or_admin:
        st.markdown("---")
        st.subheader("Leader Tools")
        st.button("Manage Members (Coming Soon)", disabled=True)