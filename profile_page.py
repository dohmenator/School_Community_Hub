# profile_page.py

import streamlit as st
from auth_manager import AuthManager
from database_manager import DatabaseManager
from typing import Dict, Any, List

def show_profile_page():
    """Displays the current user's profile and memberships."""
    st.title("👤 My Profile")
    st.markdown("---")

    auth = AuthManager()
    db_manager = DatabaseManager()

    current_user = auth.get_current_user()

    if not current_user:
        st.warning("You must be logged in to view your profile.")
        return

    # --- Display User Details ---
    st.subheader("Personal Information")
    st.write(f"**Full Name:** {current_user.get('full_name', 'N/A')}")
    st.write(f"**Email:** {current_user.get('email', 'N/A')}")
    st.write(f"**Role:** {current_user.get('role', 'N/A').replace('_', ' ').title()}") # Format role nicely
    st.write(f"**Graduation Year:** {current_user.get('grad_year', 'N/A')}")
    
    st.markdown("---")

    # --- Display Organization Memberships ---
    st.subheader("My Organization Memberships")

    user_memberships: List[Dict[str, Any]] = db_manager.get_orgs_for_user(current_user['id'])

    if not user_memberships:
        st.info("You are not currently a member of any organization.")
    else:
        # Use Streamlit's expander for each organization
        for membership in user_memberships:
            org_data = membership.get('organizations', {}) # Get the nested organization data
            role_in_org = membership.get('role', 'Member')

            with st.expander(f"**{org_data.get('name', 'Unknown Organization')}** (Your Role: {role_in_org.title()})"):
                st.write(f"**Category:** {org_data.get('category', 'N/A')}")
                st.write(f"**Description:** {org_data.get('description', 'No description provided.')}")
                # Future: Maybe a button to view org detail page, or leave org
                if st.button(f"View {org_data.get('name', 'Organization')} Page", key=f"view_org_{org_data.get('id')}"):
                    st.session_state.current_page = "detail"
                    st.session_state.selected_org_id = org_data.get('id')
                    st.rerun()

    # Placeholder for future functionality (e.g., Edit Profile button)
    st.markdown("---")
    st.button("Edit Profile (Coming Soon)", disabled=True)