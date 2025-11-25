from dotenv import load_dotenv
import os
from supabase import create_client, Client
from typing import List, Dict, Any, Optional

# Load environment variables from the .env file
load_dotenv() 

# --- Configuration: Loaded from the .env file ---
# These variables must be set in your local .env file
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# ------------------------------------------------

class DatabaseManager:
    """
    Manages all interactions (CRUD operations) with the Supabase database
    using the HTTPS REST API.
    """
    def __init__(self, url: str = SUPABASE_URL, key: str = SUPABASE_KEY):
        # Ensure keys are available before creating the client
        if not url or not key:
            raise ValueError("Supabase URL and Key must be provided or loaded from the .env file.")
            
        self.supabase: Client = create_client(url, key)
        print("DatabaseManager initialized.")

    # ====================================================================
    # USER (CRUD) FUNCTIONS
    # ====================================================================

    def add_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Inserts a new user record and returns the created record."""
        try:
            response = self.supabase.table("users").insert(user_data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error adding user: {e}")
            return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Retrieves all users from the database."""
        response = self.supabase.table("users").select("*").execute()
        return response.data if response.data else []

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single user by their unique email address."""
        try:
            response = (self.supabase.table("users")
                        .select("*")
                        .eq("email", email)
                        .single()
                        .execute())
            return response.data
        except Exception as e:
             # Supabase client often raises an error if single() returns 0 rows
             return None 

    def update_user_role(self, user_id: str, new_role: str) -> Optional[Dict[str, Any]]:
        """Updates the role for a specific user ID."""
        try:
            response = (self.supabase.table("users")
                        .update({"role": new_role})
                        .eq("id", user_id)
                        .execute())
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error updating user role: {e}")
            return None
            
    def delete_user(self, user_id: str) -> bool:
        """Deletes a user record by ID."""
        try:
            self.supabase.table("users").delete().eq("id", user_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    # ====================================================================
    # ORGANIZATION (CRUD) FUNCTIONS
    # ====================================================================

    def add_organization(self, org_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Inserts a new organization record."""
        try:
            response = self.supabase.table("organizations").insert(org_data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error adding organization: {e}")
            return None

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
             return None
             
    def get_org_directory(self) -> List[Dict[str, Any]]:
        """Retrieves all organizations, ordered by name."""
        response = (self.supabase.table("organizations")
                    .select("*")
                    .order("name") 
                    .execute())
        return response.data if response.data else []

    def update_org_description(self, org_id: str, new_description: str) -> Optional[Dict[str, Any]]:
        """Updates the description for a specific organization ID."""
        try:
            response = (self.supabase.table("organizations")
                        .update({"description": new_description})
                        .eq("id", org_id)
                        .execute())
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error updating organization description: {e}")
            return None

    def delete_organization(self, org_id: str) -> bool:
        """Deletes an organization record by ID."""
        try:
            self.supabase.table("organizations").delete().eq("id", org_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting organization: {e}")
            return False

    # ====================================================================
    # MEMBERSHIP (CRUD) FUNCTIONS
    # ====================================================================

    def add_membership(self, user_id: str, organization_id: str, role: str = 'member') -> Optional[Dict[str, Any]]:
        """Links a user to an organization with a specific role."""
        membership_data = {
            "user_id": user_id,
            "organization_id": organization_id,
            "role": role
        }
        try:
            response = self.supabase.table("memberships").insert(membership_data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"❌ Error adding membership: {e}")
            return None

    def get_memberships_for_org(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        Fetches the roster for a given organization.
        Uses a join/embed query to get the full user details.
        """
        response = (self.supabase.table("memberships")
                    .select("role, users(*)") 
                    .eq("organization_id", organization_id)
                    .order("role", desc=True) # Order by role to put leaders first (e.g., president)
                    .execute())
        return response.data if response.data else []

    def get_orgs_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Fetches all organizations a given user belongs to.
        Uses a join/embed query to get the full organization details.
        """
        response = (self.supabase.table("memberships")
                    .select("role, organizations(*)")
                    .eq("user_id", user_id)
                    .execute())
        return response.data if response.data else []

    def update_membership_role(self, membership_id: str, new_role: str) -> Optional[Dict[str, Any]]:
        """Updates the role for an existing membership record."""
        try:
            response = (self.supabase.table("memberships")
                        .update({"role": new_role})
                        .eq("id", membership_id)
                        .execute())
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"❌ Error updating membership role: {e}")
            return None
            
    def remove_membership(self, membership_id: str) -> bool:
        """Deletes a membership record by its ID."""
        try:
            self.supabase.table("memberships").delete().eq("id", membership_id).execute()
            return True
        except Exception as e:
            print(f"❌ Error removing membership: {e}")
            return False