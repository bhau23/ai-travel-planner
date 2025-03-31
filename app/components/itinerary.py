import streamlit as st
from datetime import datetime
import json
import pandas as pd
from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px

class ItineraryDisplay:
    @staticmethod
    def show_itinerary(itinerary: Dict[str, Any], weather_data: List[Dict[str, Any]]):
        """Display the complete travel itinerary with weather information."""
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Day-by-Day Plan", "Weather Forecast", "Summary"])

        with tab1:
            ItineraryDisplay._show_daily_plans(itinerary, weather_data)

        with tab2:
            ItineraryDisplay._show_weather_forecast(weather_data)

        with tab3:
            ItineraryDisplay._show_summary(itinerary)

    @staticmethod
    def _show_daily_plans(itinerary: Dict[str, Any], weather_data: List[Dict[str, Any]]):
        """Display day-by-day itinerary with weather information."""
        for day_plan in itinerary['daily_plans']:
            # Create expandable section for each day
            with st.expander(
                f"Day {day_plan['day']} - {day_plan['date']}", 
                expanded=day_plan['day'] == 1
            ):
                # Display weather information for the day
                weather = next(
                    (w for w in weather_data if w['date'] == day_plan['date']), 
                    None
                )
                if weather:
                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("Temperature", f"{weather['avg_temp']:.1f}°C")
                    with cols[1]:
                        st.metric("Conditions", weather['conditions'])
                    with cols[2]:
                        st.metric("Humidity", f"{weather['humidity']:.0f}%")
                    with cols[3]:
                        st.metric("Rain Chance", f"{weather['precipitation_prob']:.0f}%")

                # Display activities timeline
                ItineraryDisplay._show_activities_timeline(day_plan['activities'], day_plan['day'])
                
                # Display daily budget and notes
                st.info(f"Daily Budget: {day_plan['daily_budget']}")
                if day_plan['notes']:
                    st.markdown("**Notes:**")
                    st.markdown(day_plan['notes'])

    @staticmethod
    def _show_activities_timeline(activities: List[Dict[str, Any]], day_number: int):
        """Display activities in a timeline format."""
        # Create a Gantt chart-like timeline
        fig = go.Figure()

        # Define color scheme for different activity types
        colors = {
            'activity': '#FF9999',
            'meal': '#99FF99',
            'transport': '#9999FF'
        }

        # Convert activities to DataFrame for easier handling
        activities_df = pd.DataFrame(activities)
        activities_df['start_time'] = pd.to_datetime(activities_df['time'], format='%H:%M').dt.time
        activities_df['duration_hours'] = activities_df['duration'].str.extract(r'(\d+)').astype(float)

        # Add activities to timeline
        for idx, activity in activities_df.iterrows():
            start_time = datetime.combine(datetime.today(), activity['start_time'])
            end_time = start_time + pd.Timedelta(hours=activity['duration_hours'])

            fig.add_trace(go.Scatter(
                x=[start_time, end_time],
                y=[idx, idx],
                mode='lines',
                line=dict(color=colors.get(activity['type'], '#CCCCCC'), width=20),
                name=activity['description'],
                text=f"{activity['description']}<br>{activity['location']}<br>{activity['cost']}",
                hoverinfo='text'
            ))

        # Update layout
        fig.update_layout(
            title='Daily Timeline',
            xaxis_title='Time',
            showlegend=False,
            height=200 + (len(activities) * 30),
            margin=dict(l=0, r=0, t=30, b=0)
        )

        # Generate unique key using day number and first activity time
        timeline_key = f"timeline_day{day_number}_{activities[0]['time']}"
        st.plotly_chart(fig, use_container_width=True, key=timeline_key)

        # Display activities as cards
        for activity in activities:
            with st.container():
                cols = st.columns([3, 1, 1])
                with cols[0]:
                    st.markdown(f"**{activity['time']} - {activity['description']}**")
                    st.markdown(f"📍 {activity['location']}")
                with cols[1]:
                    st.markdown(f"⏱️ {activity['duration']}")
                with cols[2]:
                    st.markdown(f"💰 {activity['cost']}")

    @staticmethod
    def _show_weather_forecast(weather_data: List[Dict[str, Any]]):
        """Display detailed weather forecast."""
        if not weather_data:
            st.warning("No weather data available.")
            return

        # Convert to DataFrame for easier handling
        weather_df = pd.DataFrame(weather_data)
        
        # Create temperature trend chart
        temp_fig = go.Figure()

        temp_fig.add_trace(go.Scatter(
            x=weather_df['date'],
            y=weather_df['max_temp'],
            name='Max Temp',
            line=dict(color='#FF9999')
        ))
        temp_fig.add_trace(go.Scatter(
            x=weather_df['date'],
            y=weather_df['min_temp'],
            name='Min Temp',
            line=dict(color='#9999FF')
        ))

        temp_fig.update_layout(
            title='Temperature Trend',
            xaxis_title='Date',
            yaxis_title='Temperature (°C)',
            height=400
        )

        st.plotly_chart(temp_fig, use_container_width=True, key="weather_temp_trend")

        # Display daily weather details
        for idx, weather in weather_df.iterrows():
            with st.expander(f"Weather for {weather['date']}", expanded=False):
                cols = st.columns(4)
                with cols[0]:
                    st.metric("Avg Temp", f"{weather['avg_temp']:.1f}°C")
                with cols[1]:
                    st.metric("Conditions", weather['conditions'])
                with cols[2]:
                    st.metric("Wind Speed", f"{weather['wind_speed']:.1f} m/s")
                with cols[3]:
                    st.metric("Rain Chance", f"{weather['precipitation_prob']:.0f}%")

    @staticmethod
    def _show_summary(itinerary: Dict[str, Any]):
        """Display trip summary and general information."""
        # Display total budget
        st.metric("Total Budget", itinerary['total_budget'])

        # Display general tips
        st.markdown("### Travel Tips")
        for tip in itinerary['general_tips']:
            st.markdown(f"- {tip}")

        # Display emergency contacts
        st.markdown("### Emergency Contacts")
        contacts = itinerary['emergency_contacts']
        cols = st.columns(len(contacts))
        for col, (service, number) in zip(cols, contacts.items()):
            with col:
                st.metric(service.title(), number)

        # Add download button for itinerary
        st.download_button(
            label="Download Itinerary",
            data=ItineraryDisplay._generate_itinerary_pdf(itinerary),
            file_name="travel_itinerary.pdf",
            mime="application/pdf"
        )

    @staticmethod
    def _generate_itinerary_pdf(itinerary: Dict[str, Any]) -> bytes:
        """Generate a PDF version of the itinerary."""
        # TODO: Implement PDF generation using reportlab
        # For now, return a simple JSON string
        return json.dumps(itinerary, indent=2).encode('utf-8')