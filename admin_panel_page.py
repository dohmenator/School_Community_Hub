# admin_panel_page.py

import streamlit as st
import pandas as pd
from database_manager import DatabaseManager
from auth_manager import AuthManager
from typing import List, Dict, Any

def add_organization_form(db_manager: DatabaseManager):
    """
    Displays the form for adding a new organization and handles submission.
    """
    st.subheader("➕ Add New Organization")
    
    # 1. Define possible categories (used for the dropdown)
    # This should match your data structure, modify as needed
    org_categories = [
        "Academic",
        "Athletics",
        "Arts & Culture",
        "Community Service",
        "STEM",
        "Student Government",
        "Other"
    ]

    with st.form("add_organization_form", clear_on_submit=True):
        
        # --- Form Fields ---
        name = st.text_input("Organization Name *", max_chars=100)
        description = st.text_area("Description * (What is the mission?)")
        category = st.selectbox("Category *", options=org_categories)
        advisor_name = st.text_input("Faculty Advisor Name *")
        meeting_info = st.text_input("Meeting Info (e.g., Tuesdays at 3:30 PM, Room 101)")
        logo_url = st.text_input("Logo URL (Optional)", help="A direct link to the club's logo or image.")
        is_verified = st.checkbox("Is Officially Verified?", value=False)
        
        add_submitted = st.form_submit_button("Create Organization")

        if add_submitted:
            # 2. Validation
            if not (name and description and advisor_name):
                st.error("Please fill in all required fields marked with *.")
                return
            
            # 3. Prepare Data
            org_data = {
                "name": name,
                "description": description,
                "category": category,
                "advisor_name": advisor_name,
                "meeting_info": meeting_info,
                "logo_url": logo_url if logo_url else None,
                "is_verified": is_verified
            }
            
            # 4. Database Insertion
            result = db_manager.add_organization(org_data)
            
            if result:
                st.success(f"✅ Organization '{name}' created successfully!")
                st.cache_data.clear() # Clear cache to refresh directory
                # We don't need to rerun here, the success message is sufficient
            else:
                st.error(f"❌ Failed to create organization. It might already exist.")
                st.warning("Check the terminal for database errors if this persists.")

# End of new function add_organization_form


def view_edit_organizations_section(db_manager: DatabaseManager):
    """
    Displays all organizations, allows selection for editing, and handles updates/deletions.
    """
    st.subheader("🔎 View and Edit Organizations")

    all_orgs = db_manager.get_org_directory()

    if not all_orgs:
        st.warning("No organizations found yet. Use the '➕ Add New' tab to create one.")
        return

    orgs_df = pd.DataFrame(all_orgs)
    display_columns = ['id', 'name', 'category', 'advisor_name', 'is_verified', 'created_at']
    orgs_df = orgs_df[display_columns]
    orgs_df.rename(columns={'id': 'Org ID', 'name': 'Name', 'category': 'Category', 
                            'advisor_name': 'Advisor', 'is_verified': 'Verified', 
                            'created_at': 'Created At'}, inplace=True)
    
    st.dataframe(orgs_df, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.write("### Select Organization to Edit or Delete")
    
    selected_org_id = st.selectbox(
        "Select Organization:",
        options=orgs_df['Org ID'],
        format_func=lambda org_id: f"{orgs_df[orgs_df['Org ID'] == org_id]['Name'].iloc[0]} (ID: {org_id})"
    )

    selected_org_details = next((org for org in all_orgs if org['id'] == selected_org_id), None)

    if selected_org_details:
        st.markdown(f"#### Editing '{selected_org_details['name']}'")
        
        org_categories = [
            "Academic", "Athletics", "Arts & Culture", "Community Service", 
            "STEM", "Student Government", "Other"
        ]

        # Initialize session state for delete confirmation if not present
        if f'confirm_delete_{selected_org_id}' not in st.session_state:
            st.session_state[f'confirm_delete_{selected_org_id}'] = False

        with st.form(f"edit_organization_form_{selected_org_id}"): 
            name = st.text_input("Organization Name *", max_chars=100, value=selected_org_details['name'])
            description = st.text_area("Description *", value=selected_org_details['description'])
            category = st.selectbox(
                "Category *", 
                options=org_categories, 
                index=org_categories.index(selected_org_details['category']) if selected_org_details['category'] in org_categories else 0
            )
            advisor_name = st.text_input("Faculty Advisor Name *", value=selected_org_details['advisor_name'])
            meeting_info = st.text_input("Meeting Info", value=selected_org_details['meeting_info'])
            logo_url = st.text_input("Logo URL (Optional)", value=selected_org_details['logo_url'])
            is_verified = st.checkbox("Is Officially Verified?", value=selected_org_details['is_verified'])

            col1, col2 = st.columns(2)
            with col1:
                update_submitted = st.form_submit_button("Update Organization")
            with col2:
                # This button *sets a state* to show the confirmation, it doesn't delete directly
                request_delete = st.form_submit_button("Delete Organization", type="secondary") 
            
            # --- Handle Update ---
            if update_submitted:
                st.session_state[f'confirm_delete_{selected_org_id}'] = False # Hide confirmation if updating
                if not (name and description and advisor_name):
                    st.error("Please fill in all required fields marked with *.")
                    return
                
                updated_org_data = {
                    "name": name,
                    "description": description,
                    "category": category,
                    "advisor_name": advisor_name,
                    "meeting_info": meeting_info,
                    "logo_url": logo_url if logo_url else None,
                    "is_verified": is_verified
                }
                
                result = db_manager.update_organization(selected_org_id, updated_org_data)
                
                if result:
                    st.success(f"✅ Organization '{name}' updated successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update organization '{name}'.")
            
            # --- Handle Delete Request ---
            if request_delete:
                # Set session state to true to show the confirmation button outside the form
                st.session_state[f'confirm_delete_{selected_org_id}'] = True
                st.rerun() # Rerun to display the confirmation outside the form


        # --- Delete Confirmation (OUTSIDE the form context) ---
        if st.session_state[f'confirm_delete_{selected_org_id}']:
            st.warning(f"Are you sure you want to delete '{selected_org_details['name']}'? This action cannot be undone.", icon="⚠️")
            
            # Now, this is a regular st.button and is NOT inside the form
            col_confirm_del, col_cancel_del = st.columns(2)
            with col_confirm_del:
                if st.button(f"Confirm Delete '{selected_org_details['name']}'", key=f"final_confirm_delete_{selected_org_id}", type="primary"): # New key
                    result = db_manager.delete_organization(selected_org_id)
                    if result:
                        st.success(f"🗑️ Organization '{selected_org_details['name']}' deleted successfully!")
                        st.session_state[f'confirm_delete_{selected_org_id}'] = False # Reset confirmation state
                        st.cache_data.clear() 
                        st.rerun() 
                    else:
                        st.error(f"❌ Failed to delete organization '{selected_org_details['name']}'.")
            with col_cancel_del:
                if st.button("Cancel Delete", key=f"cancel_delete_{selected_org_id}", type="secondary"):
                    st.session_state[f'confirm_delete_{selected_org_id}'] = False # Hide confirmation
                    st.rerun()

# End of view_edit_organizations_section


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
    possible_roles = ['student', 'club_leader', 'faculty', 'teacher', 'admin']

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


    # Inside show_admin_panel_page() in admin_panel_page.py

    # ... (After the User Management Section) ...

    # ====================================================================
    # 2. Organization Management Section
    # ====================================================================
    st.subheader("🏛️ Organization Management")
    st.info("Manage clubs and organizations (Add, Edit, Delete).")
    
    # Use a tab structure to separate Add and View/Edit (future)
    add_tab, view_tab = st.tabs(["➕ Add New", "🔎 View/Edit All"]) # <--- Make sure "Coming Soon" is removed here too!
    
    with add_tab:
        add_organization_form(db_manager)

    with view_tab:
        # st.warning("The ability to view, edit, and delete existing organizations is scheduled for the next mini-sprint.") # <-- COMMENT OUT OR DELETE THIS LINE
        view_edit_organizations_section(db_manager) # <-- This is the one we want to run