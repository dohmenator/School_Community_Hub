# database_manager.py (COMPREHENSIVE HARMONIZED VERSION)

from dotenv import load_dotenv
import os
from supabase import create_client, Client
from typing import List, Dict, Any, Optional
from datetime import datetime # Still needed for event logic if dates are manipulated here

# Load environment variables from the .env file
load_dotenv()

# --- Configuration: Loaded from the .env file ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# ------------------------------------------------

class DatabaseManager:
    """
    Manages all interactions (CRUD operations) with the Supabase database
    using the HTTPS REST API.
    """
    def __init__(self, url: str = SUPABASE_URL, key: str = SUPABASE_KEY):
        if not url or not key:
            raise ValueError("Supabase URL and Key must be provided or loaded from the .env file.")
            
        self.supabase: Client = create_client(supabase_url=url, supabase_key=key)
        # print("DatabaseManager initialized.") # Only for debugging, can remove later

    # ====================================================================
    # USER PROFILE FUNCTIONS (Mapping to public.users table)
    # = These functions are used for managing user-specific data and roles.
    # ====================================================================

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a user's profile from the public.users table by user_id."""
        try:
            response = self.supabase.table("users").select("*").eq("id", user_id).single().execute()
            return response.data
        except Exception as e:
            # print(f"Error fetching user profile for {user_id}: {e}") # Debugging
            return None

    def create_user_profile(self, user_id: str, email: str, full_name: str, grad_year: int, role: str) -> bool:
        """Creates a new user profile in the public.users table."""
        try:
            # Check if profile already exists to prevent duplicates during concurrent signups
            existing_profile = self.get_user_profile(user_id)
            if existing_profile:
                # print(f"Profile for {email} already exists, skipping creation.") # Debugging
                return True # Consider it a success if it already exists
                
            response = self.supabase.table("users").insert({
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "grad_year": grad_year,
                "role": role
            }).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error creating user profile for {email}: {e}")
            return False

    def get_all_users_with_profiles(self) -> List[Dict[str, Any]]:
        """Fetches all user profiles from the public.users table."""
        try:
            response = self.supabase.table("users").select("*").order("full_name").execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching all user profiles: {e}")
            return []

    def update_user_role(self, user_id: str, new_role: str) -> bool:
        """Updates the role of a specific user in the public.users table."""
        try:
            response = (self.supabase.table("users")
                        .update({"role": new_role})
                        .eq("id", user_id)
                        .execute())
            return bool(response.data) # Return bool for success/failure
        except Exception as e:
            print(f"Error updating role for user {user_id}: {e}")
            return False

    # ====================================================================
    # ORGANIZATION FUNCTIONS (Mapping to public.organizations table)
    # ====================================================================

    def get_org_directory(self) -> List[Dict[str, Any]]:
        """Retrieves all organizations, ordered by name, for the directory page."""
        try:
            response = (self.supabase.table("organizations")
                        .select("*")
                        .order("name")
                        .execute())
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching organization directory: {e}")
            return []

    def get_organization_by_id(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single organization by its ID."""
        try:
            response = (self.supabase.table("organizations")
                        .select("*")
                        .eq("id", org_id)
                        .single()
                        .execute())
            return response.data
        except Exception as e:
            # Supabase client often raises an error if single() returns 0 rows
            # print(f"Error fetching organization {org_id}: {e}") # Debugging
            return None
            
    def add_organization(self, org_data: Dict[str, Any]) -> bool: # Changed return to bool for consistency
        """Inserts a new organization record."""
        try:
            response = self.supabase.table("organizations").insert(org_data).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error adding organization: {e}")
            return False

    # (Other org functions like update_org_description, delete_organization can stay if you use them)

    # ====================================================================
    # MEMBERSHIP FUNCTIONS (Mapping to public.memberships table)
    # ====================================================================

    def get_orgs_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Fetches all organizations a given user belongs to, with organization details.
        """
        try:
            response = (self.supabase.table("memberships")
                        .select("role, organizations!inner(id, name, category, description)") # Join to get full org data
                        .eq("user_id", user_id)
                        .execute())
            
            # Flatten the nested organization data for easier use
            if response.data:
                flattened_data = []
                for membership in response.data:
                    org_info = membership.get('organizations', {})
                    if org_info:
                        flattened_data.append({
                            'membership_role': membership.get('role'),
                            'org_id': org_info.get('id'),
                            'org_name': org_info.get('name'),
                            'org_category': org_info.get('category'),
                            'org_description': org_info.get('description')
                        })
                return flattened_data
            return []
        except Exception as e:
            print(f"Error fetching organizations for user {user_id}: {e}")
            return []

    def get_memberships_for_org(self, org_id: str) -> List[Dict[str, Any]]:
        """
        Fetches the roster for a given organization, including user details.
        """
        try:
            response = (self.supabase.table("memberships")
                        .select("role, users!inner(id, full_name, email, grad_year)") # Join to get user details
                        .eq("organization_id", org_id)
                        .order("role", desc=True) # Order by role to put leaders first
                        .execute())

            # Flatten the nested user data for easier use
            if response.data:
                flattened_data = []
                for membership in response.data:
                    user_info = membership.get('users', {})
                    if user_info:
                        flattened_data.append({
                            'membership_role': membership.get('role'),
                            'user_id': user_info.get('id'),
                            'full_name': user_info.get('full_name'),
                            'email': user_info.get('email'),
                            'grad_year': user_info.get('grad_year')
                        })
                return flattened_data
            return []
        except Exception as e:
            print(f"Error fetching memberships for organization {org_id}: {e}")
            return []

    def get_user_org_membership_status(self, user_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        """
        Checks if a user is a member of a specific organization and returns the membership record if found.
        """
        try:
            response = (self.supabase.table("memberships")
                        .select("*")
                        .eq("user_id", user_id)
                        .eq("organization_id", org_id)
                        .single()
                        .execute())
            return response.data
        except Exception as e:
            # print(f"Error checking membership status for user {user_id} in org {org_id}: {e}") # Debugging
            return None # Return None if no record or an error occurs

    def join_organization(self, user_id: str, org_id: str, role: str = "member") -> bool:
        """Adds a user as a member to an organization."""
        try:
            existing_membership = self.get_user_org_membership_status(user_id, org_id)
            if existing_membership:
                # print("You are already a member of this organization.") # Debugging
                return False # Indicate that it was not 'joined' because already a member

            response = (self.supabase.table("memberships")
                        .insert({"user_id": user_id, "organization_id": org_id, "role": role})
                        .execute())
            return bool(response.data)
        except Exception as e:
            print(f"Error joining organization {org_id} for user {user_id}: {e}")
            return False

    def leave_organization(self, user_id: str, org_id: str) -> bool:
        """Removes a user's membership from an organization."""
        try:
            response = (self.supabase.table("memberships")
                        .delete()
                        .eq("user_id", user_id)
                        .eq("organization_id", org_id)
                        .execute())
            return bool(response.data)
        except Exception as e:
            print(f"Error leaving organization {org_id} for user {user_id}: {e}")
            return False
            
    # (Other membership functions like update_membership_role, remove_membership can stay if you use them)

    # ====================================================================
    # EVENT FUNCTIONS (Mapping to public.events table)
    # ====================================================================

    def add_event(self, event_data: Dict[str, Any]) -> bool: # Changed return to bool for consistency
        """Inserts a new event record."""
        try:
            response = self.supabase.table("events").insert(event_data).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error adding event: {e}")
            return False

    def get_all_events(self, include_private: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieves all public events, optionally including private ones,
        and flattens organization details for Streamlit display.
        """
        try:
            query = self.supabase.table("events").select("*, organizations(name, category)")
            
            if not include_private:
                query = query.eq("is_public", True)
                
            response = query.order("start_time", desc=False).execute()
            
            # Flatten the data structure slightly for easier use in Streamlit
            if response.data:
                flattened_data = []
                for event in response.data:
                    # Pull the organization name and category up to the top level
                    if event.get('organizations'):
                        event['organization_name'] = event['organizations']['name']
                        event['organization_category'] = event['organizations']['category']
                    # Remove the nested organization data (optional, but good for cleanliness)
                    event.pop('organizations', None)
                    flattened_data.append(event)
                return flattened_data
            
            return []
        except Exception as e:
            print(f"Error fetching all events: {e}")
            return []

    # (Other event functions like get_events_for_organization, delete_event can stay if you use them)