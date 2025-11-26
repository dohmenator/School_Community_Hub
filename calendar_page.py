# calendar_page.py (Updated)

import streamlit as st
import pandas as pd
from database_manager import DatabaseManager
from datetime import datetime
from typing import List, Dict, Any
import event_form # <-- 1. NEW IMPORT

# --- Data Fetching ---
@st.cache_data(show_spinner="Loading Master Calendar events...")
def get_calendar_events():
    """Fetches all public events from the database."""
    db_manager = DatabaseManager()
    return db_manager.get_all_events(include_private=False)

# --- Page Rendering ---

def show_calendar():
    """Implements the Master Calendar Page wireframe."""
    st.title("🗓️ Dohmens Master Calendar")
    
    # 1. State for showing the form
    if 'show_event_form' not in st.session_state:
        st.session_state.show_event_form = False

    # 2. Button and Form Logic
    # If the form state is active, show the form and the 'Back' button
    if st.session_state.show_event_form:
        if st.button("⬅️ Back to Calendar"):
            st.session_state.show_event_form = False
            st.rerun()
        event_form.show_event_creation_form() # <-- Display the new form
        return # STOP HERE so the calendar list doesn't show with the form

    # 3. Calendar Display Logic (Runs if show_event_form is False)
    
    # Button to open the form
    if st.button("➕ Add New Event"):
        st.session_state.show_event_form = True
        st.rerun()
        
    # Fetch Data
    event_data = get_calendar_events()
    
    if not event_data:
        st.info("There are no upcoming events scheduled at this time.")
        return

    # 4. Data Processing for Display
    df = pd.DataFrame(event_data)
    # Convert timestamps to local datetime objects and format them
    df['start_time'] = pd.to_datetime(df['start_time']).dt.strftime('%m/%d/%Y %I:%M %p')
    df['end_time'] = df['end_time'].apply(
        lambda x: pd.to_datetime(x).strftime('%I:%M %p') if pd.notnull(x) else 'TBD'
    )
    
    # Combine start/end times for a single display column
    df['Time'] = df['start_time'] + df['end_time'].apply(lambda x: f" - {x}" if x != 'TBD' else "")
    
    # Combine Org Name and Category for filtering
    df['Organization'] = df['organization_name']
    df['Category'] = df['organization_category']


    # 5. Filter and Display Table
    st.markdown("---")
    st.subheader("Upcoming Events")
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_order=["title", "Time", "location", "Organization", "Category"],
        column_config={
            "title": st.column_config.TextColumn("Event Title"),
            "Time": st.column_config.TextColumn("Date & Time"),
            "location": st.column_config.TextColumn("Location"),
            "Organization": st.column_config.TextColumn("Hosted By"),
            "Category": st.column_config.TextColumn("Type"),
            "start_time": None, "end_time": None, "organization_name": None, 
            "organization_category": None, "id": None, "created_at": None,
            "is_public": None, "description": None, "organization_id": None
        }
    )