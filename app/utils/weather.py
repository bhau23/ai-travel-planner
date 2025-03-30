"""Weather service integration with fallback behavior."""
import streamlit as st
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

def get_mock_weather_data(start_date: str, num_days: int = 3) -> List[Dict[str, Any]]:
    """Generate mock weather data for testing."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    weather_data = []
    
    for i in range(num_days):
        current_date = start + timedelta(days=i)
        weather_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "avg_temp": 22.0,
            "min_temp": 18.0,
            "max_temp": 26.0,
            "humidity": 65.0,
            "precipitation_prob": 20.0,
            "wind_speed": 12.0,
            "conditions": "Partly Cloudy"
        })
    
    return weather_data

def get_weather_forecast(destination: str, start_date: str, num_days: int = 3) -> List[Dict[str, Any]]:
    """Get weather forecast data with fallback to mock data."""
    try:
        api_key = st.secrets.get("WEATHER_API_KEY")
        
        if not api_key:
            st.info("🌤️ Using sample weather data. Add WEATHER_API_KEY to secrets for real weather information.")
            return get_mock_weather_data(start_date, num_days)
            
        # TODO: Implement actual weather API integration
        # For now, return mock data
        return get_mock_weather_data(start_date, num_days)
        
    except Exception as e:
        st.warning(f"Weather data retrieval failed: {str(e)}. Using sample data.")
        return get_mock_weather_data(start_date, num_days)