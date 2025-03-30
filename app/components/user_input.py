import streamlit as st
from datetime import datetime, timedelta
import json
from typing import Dict, Any

class UserInputForm:
    @staticmethod
    def show_basic_details():
        """Display form for basic travel details."""
        with st.form("basic_details_form"):
            # Destination
            destination = st.text_input(
                "Destination",
                value=st.session_state.travel_data.get("destination", ""),
                help="Enter the city or location you want to visit"
            )

            # Date Selection
            col1, col2 = st.columns(2)
            min_date = datetime.now().date()
            max_date = min_date + timedelta(days=365)

            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=st.session_state.travel_data.get("start_date", min_date),
                    min_value=min_date,
                    max_value=max_date
                )

            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=st.session_state.travel_data.get("end_date", min_date + timedelta(days=7)),
                    min_value=start_date,
                    max_value=max_date
                )

            # Budget Range
            budget_ranges = [
                "Budget (Under $1000)",
                "Moderate ($1000-$3000)",
                "Luxury ($3000+)"
            ]
            budget = st.selectbox(
                "Budget Range",
                options=budget_ranges,
                index=budget_ranges.index(st.session_state.travel_data.get("budget", budget_ranges[1]))
                if "budget" in st.session_state.travel_data else 1
            )

            submitted = st.form_submit_button("Save & Continue")
            if submitted:
                # Update session state
                st.session_state.travel_data.update({
                    "destination": destination,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "duration": (end_date - start_date).days + 1,
                    "budget": budget
                })
                st.session_state.current_step += 1
                st.rerun()

    @staticmethod
    def show_preferences():
        """Display form for travel preferences."""
        with st.form("preferences_form"):
            # Travel Interests
            interests = [
                "Historical Sites",
                "Museums",
                "Nature & Outdoors",
                "Food & Dining",
                "Shopping",
                "Arts & Culture",
                "Adventure Sports",
                "Relaxation",
                "Nightlife",
                "Local Experiences"
            ]
            selected_interests = st.multiselect(
                "Travel Interests (Select multiple)",
                options=interests,
                default=st.session_state.travel_data.get("interests", []),
                help="Choose activities and experiences you're interested in"
            )

            # Dietary Preferences
            dietary_options = [
                "No Restrictions",
                "Vegetarian",
                "Vegan",
                "Halal",
                "Kosher",
                "Gluten-Free",
                "Other"
            ]
            dietary_prefs = st.multiselect(
                "Dietary Preferences (Select multiple)",
                options=dietary_options,
                default=st.session_state.travel_data.get("dietary_preferences", ["No Restrictions"]),
                help="Select any dietary requirements or preferences"
            )

            # Accommodation Type
            accommodation_types = [
                "Budget Hostel",
                "Mid-range Hotel",
                "Luxury Hotel",
                "Vacation Rental",
                "Boutique Hotel"
            ]
            accommodation = st.selectbox(
                "Preferred Accommodation Type",
                options=accommodation_types,
                index=accommodation_types.index(
                    st.session_state.travel_data.get("accommodation_type", accommodation_types[1])
                ) if "accommodation_type" in st.session_state.travel_data else 1
            )

            # Mobility Concerns
            mobility_concerns = st.text_area(
                "Mobility Concerns or Special Requirements",
                value=st.session_state.travel_data.get("mobility_concerns", ""),
                help="Enter any mobility concerns or special requirements"
            )

            # Additional Preferences
            col1, col2 = st.columns(2)
            with col1:
                preferred_pace = st.slider(
                    "Preferred Pace",
                    min_value=1,
                    max_value=5,
                    value=st.session_state.travel_data.get("preferred_pace", 3),
                    help="1: Very Relaxed, 5: Very Active"
                )

            with col2:
                max_walking_time = st.slider(
                    "Maximum Walking Time (hours/day)",
                    min_value=1,
                    max_value=8,
                    value=st.session_state.travel_data.get("max_walking_time", 4)
                )

            submitted = st.form_submit_button("Save & Continue")
            if submitted:
                if not selected_interests:
                    st.error("Please select at least one interest")
                    return

                # Update session state
                st.session_state.travel_data.update({
                    "interests": selected_interests,
                    "dietary_preferences": dietary_prefs,
                    "accommodation_type": accommodation,
                    "mobility_concerns": mobility_concerns,
                    "preferred_pace": preferred_pace,
                    "max_walking_time": max_walking_time
                })
                st.session_state.current_step += 1
                st.rerun()

    @staticmethod
    def validate_travel_data() -> bool:
        """Validate that all required travel data is present."""
        required_fields = [
            "destination",
            "start_date",
            "end_date",
            "budget",
            "interests"
        ]
        
        return all(field in st.session_state.travel_data 
                  for field in required_fields)