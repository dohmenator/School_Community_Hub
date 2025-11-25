# calendar_page.py

import streamlit as st
import pandas as pd
from database_manager import DatabaseManager
from datetime import datetime
from typing import List, Dict, Any

# --- Data Fetching ---

@st.cache_data(show_spinner="Loading Master Calendar events...")
def get_calendar_events():
    """Fetches all public events from the database."""
    db_manager = DatabaseManager()
    # get_all_events() uses a join to bring in organization name and category
    return db_manager.get_all_events(include_private=False)

# --- Page Rendering ---

def show_calendar():
    """Implements the Master Calendar Page wireframe."""
    st.title("🗓️ Dohmens Master Calendar")
    
    # Fetch Data
    event_data = get_calendar_events()
    
    if not event_data:
        st.info("There are no upcoming events scheduled at this time.")
        return

    # 1. Data Processing for Display
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


    # 2. Filter Bar (Uses Streamlit's built-in filtering for dataframes)
    st.markdown("---")
    st.subheader("Upcoming Events")
    
    # Use st.dataframe with experimental_use_container_width=True for filtering
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        # Display only the most relevant columns
        column_order=["title", "Time", "location", "Organization", "Category"],
        column_config={
            "title": st.column_config.TextColumn("Event Title"),
            "Time": st.column_config.TextColumn("Date & Time"),
            "location": st.column_config.TextColumn("Location"),
            "Organization": st.column_config.TextColumn("Hosted By"),
            "Category": st.column_config.TextColumn("Type"),
            # Exclude other columns from display
            "start_time": None, "end_time": None, "organization_name": None, 
            "organization_category": None, "id": None, "created_at": None,
            "is_public": None, "description": None, "organization_id": None
        }
    )

    # Future Sprint 4: Button to add event (requires auth)
    st.markdown("---")
    st.button("➕ Add New Event", key="add_event_btn", disabled=True, help="Requires user authentication (Sprint 4)")