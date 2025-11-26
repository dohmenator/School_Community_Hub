# profile_page.py (Corrected for harmonized database_manager.py)

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
            # Access flattened data directly from the membership dictionary
            org_id = membership.get('org_id')
            org_name = membership.get('org_name', 'Unknown Organization')
            org_category = membership.get('org_category', 'N/A')
            org_description = membership.get('org_description', 'No description provided.')
            role_in_org = membership.get('membership_role', 'Member')

            # Ensure a unique key, even if org_id is somehow None (though it shouldn't be with proper data)
            # We'll use a combination of user_id and org_id for absolute uniqueness
            unique_key_suffix = f"{current_user['id']}_{org_id}" if org_id else f"{current_user['id']}_{org_name}_{role_in_org}_fallback"

            with st.expander(f"**{org_name}** (Your Role: {role_in_org.title()})"):
                st.write(f"**Category:** {org_category}")
                st.write(f"**Description:** {org_description}")
                
                # Only show the button if we have a valid org_id to link to
                if org_id:
                    if st.button(f"View {org_name} Page", key=f"view_org_page_{unique_key_suffix}"):
                        st.session_state.current_page = "detail"
                        st.session_state.selected_org_id = org_id
                        st.rerun()
                else:
                    st.warning("Could not retrieve organization details for this membership.")


    # Placeholder for future functionality (e.g., Edit Profile button)
    st.markdown("---")
    st.button("Edit Profile (Coming Soon)", disabled=True)