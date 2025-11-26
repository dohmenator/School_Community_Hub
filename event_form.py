# event_form.py

import streamlit as st
from database_manager import DatabaseManager
from datetime import datetime, time, timedelta, timezone
from typing import Dict, Any

def get_org_list_for_dropdown():
    """Fetches a list of all organizations for use in the selection dropdown."""
    db_manager = DatabaseManager()
    # Fetches all orgs, ordered by name
    orgs = db_manager.get_org_directory()
    
    # Create a dictionary mapping Name -> ID (to easily get the ID from the selected Name)
    org_map = {org['name']: org['id'] for org in orgs}
    org_names = sorted(list(org_map.keys()))
    
    return org_names, org_map

def show_event_creation_form():
    """Displays the form for adding a new event."""
    st.header("➕ Add New Event")
    st.markdown("---")
    
    org_names, org_map = get_org_list_for_dropdown()
    db_manager = DatabaseManager()
    
    # Check if we have organizations to host the event
    if not org_names:
        st.warning("Cannot create an event. Please add at least one organization first.")
        return

    with st.form("event_submission_form", clear_on_submit=True):
        
        # --- Form Fields ---
        
        # 1. Title, Description, and Host
        title = st.text_input("Event Title *", max_chars=100)
        description = st.text_area("Description (What will happen?)")
        host_org_name = st.selectbox("Host Organization *", options=org_names)
        
        # 2. Date, Time, and Location
        col_date, col_start_time, col_end_time = st.columns(3)
        
        # Set default date to today, default time to the next full hour
        default_date = datetime.today().date()
        default_time = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).time()
        
        event_date = col_date.date_input("Date *", value=default_date)
        start_time_obj = col_start_time.time_input("Start Time *", value=default_time, step=900) # 15 min increments
        end_time_obj = col_end_time.time_input("End Time", value=None, step=900)
        
        location = st.text_input("Location (e.g., Room 305, Gymnasium)")

        # 3. Optional / Access
        col_access, col_attendees = st.columns(2)
        is_public = col_access.checkbox("Make Publicly Visible?", value=True, help="If unchecked, the event is only visible to organization members.")
        max_attendees = col_attendees.number_input("Max Attendees (Optional)", min_value=0, step=1, value=0)
        if max_attendees == 0:
            max_attendees = None # Send None to database if 0 is selected
            
        # --- Submission ---
        submitted = st.form_submit_button("Submit Event")
        
        if submitted:
            # Data validation
            if not title or not event_date or not start_time_obj:
                st.error("Please fill out all required fields marked with *.")
                return

            # Combine date and time objects to create full datetime objects
            # Note: The Streamlit time object is naive, so we make it UTC-aware for Supabase
            local_start_dt = datetime.combine(event_date, start_time_obj)

            # Convert to UTC and format as ISO 8601 with timezone information
            start_datetime = local_start_dt.replace(tzinfo=timezone.utc).isoformat()
            st.write()
            # End time logic (similar conversion if an end time was provided)
            end_datetime = None
            if end_time_obj:
                local_end_dt = datetime.combine(event_date, end_time_obj)
                end_datetime = local_end_dt.replace(tzinfo=timezone.utc).isoformat()


            # Get the Organization ID from the name selected
            host_org_id = org_map.get(host_org_name)

            # # --- TEMPORARY DEBUG LINE (Keep this for the next test) ---
            # st.write(f"DEBUG: Host Org ID retrieved: {host_org_id}")
            # st.write(f"DEBUG: Start Time sent: {start_datetime}") 
            # st.write(f"DEBUG: End Time sent: {end_datetime}") 
            # # -----------------------------------------------------------

            # Prepare data dictionary
            event_data: Dict[str, Any] = {
                "title": title,
                "description": description,
                "start_time": start_datetime,
                "end_time": end_datetime,
                "location": location,
                "organization_id": host_org_id,
                "is_public": is_public,
                "max_attendees": max_attendees
            }
            
            # Insert data into Supabase
            result = db_manager.add_event(event_data)
            
            if result:
                st.success(f"✅ Event '{title}' added successfully!")
                
                # Clear the event cache and force a rerun to update the calendar table
                try:
                    st.cache_data.clear() 
                except Exception:
                    pass
                
                # After successful submission, switch back to the calendar view
                st.session_state.show_event_form = False
                st.rerun()
            else:
                st.error("❌ Failed to add event. Check your database connection or constraints.")