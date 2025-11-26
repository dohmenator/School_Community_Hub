# admin_panel_page.py

import streamlit as st
import pandas as pd
from database_manager import DatabaseManager
from auth_manager import AuthManager
from typing import List, Dict, Any

def show_admin_panel_page():
    """
    Displays the Admin Panel, allowing admin users to manage users and organizations.
    """
    st.title("⚙️ Admin Panel")
    st.markdown("---")

    auth = AuthManager()
    db_manager = DatabaseManager()

    current_user_id = auth.get_current_user().get('id')
    current_user_role = auth.get_user_role()

    # --- Authorization Check ---
    if current_user_role != 'admin': # Only 'admin' role can access the full panel
        st.error("Access Denied: You must be an administrator to view this page.")
        if st.button("Go to Home"):
            st.session_state.current_page = "home"
            st.rerun()
        return

    st.success(f"Welcome, Admin ({auth.get_current_user().get('full_name')})! Manage your school hub below.")
    st.markdown("---")

    # ====================================================================
    # 1. User Management Section
    # ====================================================================
    st.subheader("👨‍💻 User Management")
    st.info("View and change user roles. Changing a user's role will affect their permissions.")

    all_users: List[Dict[str, Any]] = db_manager.get_all_users_with_profiles()

    if not all_users:
        st.warning("No users found in the system.")
        return

    # Create a DataFrame for display and easy manipulation
    users_df = pd.DataFrame(all_users)
    users_df = users_df[['id', 'full_name', 'email', 'role', 'grad_year']] # Select and order columns
    users_df.rename(columns={'id': 'User ID', 'full_name': 'Full Name', 'email': 'Email', 
                             'role': 'Current Role', 'grad_year': 'Grad Year'}, inplace=True)
    
    # Define possible roles for the dropdown
    possible_roles = ['student', 'club_leader', 'faculty', 'admin']

    with st.form("user_role_form"):
        st.dataframe(users_df, hide_index=True, use_container_width=True) # Display all users

        st.markdown("---")
        st.write("### Change User Role")
        
        # Dropdown to select user
        user_to_change_id = st.selectbox(
            "Select User to Update Role:",
            options=users_df['User ID'],
            format_func=lambda user_id: f"{users_df[users_df['User ID'] == user_id]['Full Name'].iloc[0]} ({users_df[users_df['User ID'] == user_id]['Email'].iloc[0]})"
        )
        
        # Dropdown to select new role
        new_role = st.selectbox(
            "Select New Role:",
            options=possible_roles,
            index=possible_roles.index(users_df[users_df['User ID'] == user_to_change_id]['Current Role'].iloc[0]) # Default to current role
        )

        update_role_submitted = st.form_submit_button("Update Role")

        if update_role_submitted:
            if user_to_change_id == current_user_id and new_role != 'admin':
                st.error("Admin cannot demote themselves from 'admin' role through this panel.")
            else:
                if db_manager.update_user_role(user_to_change_id, new_role):
                    st.success(f"Role for {users_df[users_df['User ID'] == user_to_change_id]['Full Name'].iloc[0]} updated to '{new_role}'.")
                    st.cache_data.clear() # Clear cache to refresh UI
                    st.rerun()
                else:
                    st.error("Failed to update user role. Please try again.")
    
    st.markdown("---")

    # ====================================================================
    # 2. Organization Management Section (Coming in next step)
    # ====================================================================
    st.subheader("🏛️ Organization Management")
    st.info("Manage clubs and organizations (Add, Edit, Delete).")
    st.button("Add New Organization (Coming Soon)", disabled=True)
    st.button("View/Edit Organizations (Coming Soon)", disabled=True)