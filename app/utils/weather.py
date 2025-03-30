import aiohttp
from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio

class WeatherAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.session = None
        
    async def _ensure_session(self):
        """Ensure an aiohttp session exists."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            self.session = None
        
    def _generate_mock_forecast(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Generate mock weather data when API is unavailable."""
        try:
            mock_forecast = []
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days + 1
            
            import random
            conditions = ['Clear', 'Partly Cloudy', 'Cloudy', 'Light Rain', 'Sunny']
            
            for i in range(days):
                current_date = start + timedelta(days=i)
                mock_forecast.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'avg_temp': random.uniform(20, 28),
                    'min_temp': random.uniform(15, 20),
                    'max_temp': random.uniform(25, 30),
                    'conditions': random.choice(conditions),
                    'humidity': random.uniform(40, 80),
                    'wind_speed': random.uniform(2, 15),
                    'precipitation_prob': random.uniform(10, 40)
                })
            
            return mock_forecast
            
        except Exception as e:
            return []

    async def get_forecast(self, destination: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get weather forecast for the destination during the travel period."""
        if not destination or not start_date or not end_date:
            return self._generate_mock_forecast(start_date, end_date)

        try:
            await self._ensure_session()
            
            # First, get coordinates for the destination
            coords = await self._get_coordinates(destination)
            
            # Get forecast data
            forecast = await self._fetch_forecast(coords['lat'], coords['lon'])
            
            # Filter and format forecast data for the travel period
            return await self._process_forecast(forecast, start_date, end_date)
            
        except Exception as e:
            import streamlit as st
            st.warning(f"Error fetching weather data: {str(e)}. Using mock weather data.")
            return self._generate_mock_forecast(start_date, end_date)
    
    async def _get_coordinates(self, city: str) -> Dict[str, float]:
        """Get latitude and longitude for a city."""
        try:
            await self._ensure_session()
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                return {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon']
                }
            
        except aiohttp.ClientError as e:
            raise Exception(f"Error getting coordinates for {city}: {str(e)}")
    
    async def _fetch_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch 7-day weather forecast data."""
        try:
            await self._ensure_session()
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
            
        except aiohttp.ClientError as e:
            raise Exception(f"Error fetching forecast data: {str(e)}")
    
    async def _process_forecast(self, forecast_data: Dict[str, Any],
                              start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Process and filter forecast data for the travel period."""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days + 1
            
            processed_forecast = []
            current_date = start
            
            for _ in range(days):
                date_str = current_date.strftime('%Y-%m-%d')
                
                # Filter forecast data for current date
                day_data = [
                    item for item in forecast_data['list']
                    if item['dt_txt'].startswith(date_str)
                ]
                
                if day_data:
                    # Calculate daily summary
                    temps = [item['main']['temp'] for item in day_data]
                    conditions = [item['weather'][0]['main'] for item in day_data]
                    
                    # Create daily forecast summary
                    daily_forecast = {
                        'date': date_str,
                        'avg_temp': sum(temps) / len(temps),
                        'min_temp': min(temps),
                        'max_temp': max(temps),
                        'conditions': max(set(conditions), key=conditions.count),
                        'humidity': sum(item['main']['humidity'] for item in day_data) / len(day_data),
                        'wind_speed': sum(item['wind']['speed'] for item in day_data) / len(day_data),
                        'precipitation_prob': await self._calculate_precipitation_prob(day_data)
                    }
                    
                    processed_forecast.append(daily_forecast)
                
                current_date += timedelta(days=1)
            
            return processed_forecast
            
        except Exception as e:
            raise Exception(f"Error processing forecast data: {str(e)}")
    
    async def _calculate_precipitation_prob(self, day_data: List[Dict[str, Any]]) -> float:
        """Calculate precipitation probability from forecast data."""
        try:
            rain_count = sum(1 for item in day_data
                            if any(w['main'] in ['Rain', 'Snow']
                                 for w in item['weather']))
            return (rain_count / len(day_data)) * 100 if day_data else 0
            
        except Exception:
            return 0.0

    async def get_weather_recommendations(self, weather_data: Dict[str, Any]) -> List[str]:
        """Generate weather-based recommendations."""
        recommendations = []
        
        avg_temp = weather_data['avg_temp']
        conditions = weather_data['conditions']
        precip_prob = weather_data['precipitation_prob']
        
        # Temperature-based recommendations
        if avg_temp < 10:
            recommendations.append("Pack warm clothing and layers")
        elif avg_temp > 25:
            recommendations.append("Pack light, breathable clothing and sun protection")
        
        # Conditions-based recommendations
        if conditions in ['Rain', 'Drizzle']:
            recommendations.append("Bring a waterproof jacket and umbrella")
        elif conditions == 'Snow':
            recommendations.append("Pack winter boots and snow-appropriate gear")
        elif conditions == 'Clear':
            recommendations.append("Don't forget sunscreen and sunglasses")
        
        # Precipitation probability recommendations
        if precip_prob > 50:
            recommendations.append("Plan for indoor activities or have backup plans")
        
        return recommendations