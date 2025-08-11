"""Weather service integration with fallback behavior."""
import streamlit as st
import json
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any

class WeatherAPI:
    def __init__(self, api_key: str):
        """Initialize WeatherAPI with API key."""
        self.api_key = api_key
        self.use_mock = api_key == "demo"
        self.geocoding_base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.weather_base_url = "https://weather.googleapis.com/v1/forecast"
        if self.use_mock:
            st.info("🌤️ Using sample weather data. Add GOOGLE_API_KEY to secrets for real weather data.")

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

    async def _geocode_location(self, location: str) -> Dict[str, float]:
        """Get coordinates for a location using Google Geocoding API."""
        params = {
            "address": location,
            "key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.geocoding_base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "OK" and data["results"]:
                        location_data = data["results"][0]["geometry"]["location"]
                        return {"lat": location_data["lat"], "lng": location_data["lng"]}
                        
        raise Exception(f"Failed to geocode location: {location}")

    def _parse_google_weather_response(self, data: Dict, start_date: str, days: int) -> List[Dict[str, Any]]:
        """Parse Google Weather API response to our expected format."""
        weather_data = []
        start = datetime.strptime(start_date, "%Y-%m-%d")
        
        # Google Weather API returns forecasts in different format
        # This is a simplified parser - actual API response structure may vary
        forecasts = data.get("forecasts", [])
        
        for i in range(min(days, len(forecasts))):
            current_date = start + timedelta(days=i)
            forecast = forecasts[i] if i < len(forecasts) else forecasts[0]
            
            # Extract weather data from Google's response format
            temperature = forecast.get("temperature", {})
            conditions = forecast.get("condition", {})
            
            weather_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "avg_temp": temperature.get("value", 22.0),
                "min_temp": temperature.get("minimum", 18.0),
                "max_temp": temperature.get("maximum", 26.0),
                "humidity": forecast.get("humidity", {}).get("value", 65.0),
                "precipitation_prob": forecast.get("precipitationProbability", {}).get("value", 20.0),
                "wind_speed": forecast.get("wind", {}).get("speed", {}).get("value", 12.0),
                "conditions": conditions.get("text", "Partly Cloudy")
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
            
            # Calculate number of days
            days = 3
            if start_date and end_date:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                days = (end - start).days + 1
            
            # Get coordinates for the destination
            coordinates = await self._geocode_location(destination)
            
            # Prepare weather API request
            params = {
                "location.latitude": coordinates["lat"],
                "location.longitude": coordinates["lng"],
                "key": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.weather_base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_google_weather_response(data, start_date, days)
                    else:
                        raise Exception(f"Weather API request failed with status {response.status}")
            
        except Exception as e:
            st.warning(f"Weather data retrieval failed: {str(e)}. Using sample data.")
            # Calculate days for fallback
            days = 3
            if start_date and end_date:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                days = (end - start).days + 1
            return self._get_mock_weather_data(start_date, days)
