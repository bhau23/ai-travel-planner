"""Weather service integration with fallback behavior."""
import streamlit as st
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

class WeatherAPI:
    def __init__(self, api_key: str):
        """Initialize WeatherAPI with API key."""
        self.api_key = api_key
        self.use_mock = api_key == "demo"
        if self.use_mock:
            st.info("🌤️ Using sample weather data. Add OPENWEATHER_API_KEY to secrets for real weather data.")

    def _get_mock_weather_data(self, start_date: str, days: int = 3) -> List[Dict[str, Any]]:
        """Generate mock weather data for testing."""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        weather_data = []
        
        for i in range(days):
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

    async def get_forecast(
        self, 
        destination: str, 
        start_date: str, 
        end_date: str = None
    ) -> List[Dict[str, Any]]:
        """Get weather forecast data with fallback to mock data."""
        try:
            if self.use_mock:
                days = 3
                if start_date and end_date:
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                    end = datetime.strptime(end_date, "%Y-%m-%d")
                    days = (end - start).days + 1
                return self._get_mock_weather_data(start_date, days)
            
            # TODO: Implement actual OpenWeather API integration
            # For now, use mock data even with real API key
            days = 3
            if start_date and end_date:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                days = (end - start).days + 1
            return self._get_mock_weather_data(start_date, days)
            
        except Exception as e:
            st.warning(f"Weather data retrieval failed: {str(e)}. Using sample data.")
            return self._get_mock_weather_data(start_date, 3)
