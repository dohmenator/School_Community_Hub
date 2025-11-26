# auth_manager.py

import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

# --- Supabase Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class AuthManager:
    """
    Manages user authentication with Supabase, including login, logout,
    and session handling in a Streamlit-compatible way.
    """
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            st.error("Supabase URL and Key must be set in .env file.")
            st.stop()
            
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Initialize session state for user and authentication
        if 'user' not in st.session_state:
            st.session_state['user'] = None
        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False
        if 'auth_error' not in st.session_state:
            st.session_state['auth_error'] = None

    def sign_up(self, email, password, full_name, grad_year, role="student"):
        """Registers a new user with email, password, and additional profile data."""
        try:
            # 1. Supabase Auth: Create the user account
            auth_response = self.supabase.auth.sign_up(
                {"email": email, "password": password}
            )

            if auth_response.user:
                user_id = auth_response.user.id
                
                # 2. Insert additional profile data into our 'users' table
                # Ensure 'users' table is created with full_name, grad_year, role
                user_data = {
                    "id": user_id, # Link profile to auth user ID
                    "email": email,
                    "full_name": full_name,
                    "grad_year": grad_year,
                    "role": role # Default role
                }
                # Use the DatabaseManager to add this, for now directly integrate to avoid circular imports
                profile_response = self.supabase.table("users").insert(user_data).execute()

                if profile_response.data:
                    st.session_state['user'] = profile_response.data[0]
                    st.session_state['logged_in'] = True
                    st.session_state['auth_error'] = None
                    return True
                else:
                    # If profile insert fails, consider deleting the auth user if possible (complex)
                    st.session_state['auth_error'] = "Failed to create user profile."
                    return False
            else:
                st.session_state['auth_error'] = auth_response.json().get('error_description', 'Unknown sign-up error')
                return False
        except Exception as e:
            st.session_state['auth_error'] = f"Sign-up failed: {e}"
            return False

    def sign_in(self, email, password):
        """Logs in an existing user and retrieves their profile."""
        try:
            auth_response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if auth_response.user:
                # Fetch the full user profile from our 'users' table
                # We expect the 'id' in 'users' to match auth_response.user.id
                profile_response = (self.supabase.table("users")
                                    .select("*")
                                    .eq("id", auth_response.user.id)
                                    .single()
                                    .execute())
                
                if profile_response.data:
                    st.session_state['user'] = profile_response.data
                    st.session_state['logged_in'] = True
                    st.session_state['auth_error'] = None
                    return True
                else:
                    st.session_state['auth_error'] = "User profile not found after login."
                    return False
            else:
                st.session_state['auth_error'] = auth_response.json().get('error_description', 'Unknown sign-in error')
                return False
        except Exception as e:
            st.session_state['auth_error'] = f"Sign-in failed: {e}"
            return False

    def sign_out(self):
        """Logs out the current user."""
        try:
            self.supabase.auth.sign_out()
            st.session_state['user'] = None
            st.session_state['logged_in'] = False
            st.session_state['auth_error'] = None
            return True
        except Exception as e:
            st.session_state['auth_error'] = f"Logout failed: {e}"
            return False

    def is_logged_in(self):
        """Checks if a user is currently logged in."""
        return st.session_state['logged_in']

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Returns the current logged-in user's profile data."""
        return st.session_state['user']

    def get_user_role(self) -> Optional[str]:
        """Returns the role of the current logged-in user."""
        user = self.get_current_user()
        return user.get('role') if user else None