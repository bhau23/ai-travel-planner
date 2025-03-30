"""Gemini API wrapper with integrated mock support."""
import google.generativeai as genai
from typing import Dict, Any, Optional, List
import json
import streamlit as st
import time
import re
from datetime import datetime

class GeminiAPI:
    def __init__(self, api_key: str, use_mock: bool = False):
        """Initialize Gemini API with retries and fallbacks."""
        self.use_mock = use_mock
        self.model = None
        self.chat = None
        self.context = {
            "current_stage": None,
            "user_data": {},
            "generated_suggestions": None,
            "final_itinerary": None
        }

        if self.use_mock:
            st.warning("Using mock Gemini API for demonstration purposes.")
            st.success("Mock API initialized successfully")
            return

        try:
            genai.configure(api_key=api_key)
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            model_names = [
                "models/gemini-1.5-pro-002",
                "models/gemini-1.5-pro",
                "models/gemini-1.5-pro-latest",
                "models/gemini-1.5-pro-001",
            ]
            
            for model_name in model_names:
                try:
                    if (model_name != model_names[0]):
                        st.info("Waiting before retry...")
                        time.sleep(2)
                    
                    with st.spinner(f"Attempting to initialize {model_name}..."):
                        self.model = genai.GenerativeModel(
                            model_name=model_name,
                            generation_config=generation_config
                        )
                        test_response = self.model.generate_content("List one travel item.")
                        if not test_response or not test_response.text:
                            raise Exception("Model test failed - no response")
                        st.success(f"Successfully connected using model: {model_name}")
                        return
                        
                except Exception as e:
                    st.warning(f"Failed to initialize {model_name}, trying next model...")
                    continue
            
            st.warning("⚠️ All API initialization attempts failed. Using mock API.")
            self.use_mock = True
            st.success("Mock API initialized successfully")
            
        except Exception as e:
            st.error(f"Failed to initialize Gemini API: {str(e)}")
            if "quota" in str(e).lower():
                st.info("API quota exceeded. Using mock API.")
                self.use_mock = True
            else:
                raise

    def _get_mock_suggestions(self) -> Dict[str, Any]:
        """Get mock activity suggestions."""
        return {
            "attractions": [
                {"name": "ParisianMuseum", "description": "Historicalartifacts", "cost": "20EUR", "time_needed": "3hours"},
                {"name": "EiffelTower", "description": "IconicParisianlandmark", "cost": "25EUR", "time_needed": "2hours"},
                {"name": "NotreDame", "description": "Historicalcathedral", "cost": "0EUR", "time_needed": "1hour"}
            ],
            "restaurants": [
                {"name": "LeBistro", "description": "Traditionalfrenchcuisine", "cost": "30EUR", "cuisine": "French"},
                {"name": "CafeParis", "description": "Casualfrenchdining", "cost": "25EUR", "cuisine": "French"},
                {"name": "BrasserieRoyal", "description": "Elegantdining", "cost": "45EUR", "cuisine": "French"}
            ],
            "activities": [
                {"name": "RiverCruise", "description": "SeineRivertour", "cost": "15EUR", "time_needed": "1hour"},
                {"name": "WineTours", "description": "Winetasting", "cost": "40EUR", "time_needed": "3hours"},
                {"name": "BikeRental", "description": "Citybiketour", "cost": "10EUR", "time_needed": "2hours"}
            ]
        }

    def _get_mock_itinerary(self) -> Dict[str, Any]:
        """Get mock travel itinerary."""
        return {
            "daily_plans": [
                {
                    "day": 1,
                    "date": "2024-03-30",
                    "activities": [
                        {
                            "time": "09:00",
                            "duration": "3hours",
                            "description": "ExploreMuseum",
                            "location": "ParisianMuseum",
                            "cost": "20EUR",
                            "type": "activity"
                        },
                        {
                            "time": "12:30",
                            "duration": "1hour",
                            "description": "Lunch",
                            "location": "LeBistro",
                            "cost": "30EUR",
                            "type": "meal"
                        },
                        {
                            "time": "14:00",
                            "duration": "2hours",
                            "description": "CityTour",
                            "location": "BikeRental",
                            "cost": "10EUR",
                            "type": "activity"
                        }
                    ],
                    "daily_budget": "60EUR",
                    "notes": "Startwithamuseumvisitandrelaxingbiketouraround"
                }
            ],
            "total_budget": "60EUR",
            "general_tips": [
                "Bookmuseumticketsinadvance",
                "Uselocaltransport",
                "Carrywater"
            ],
            "emergency_contacts": {
                "police": "17",
                "ambulance": "15",
                "tourist_police": "17"
            }
        }

    async def generate_suggestions(self, travel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized activity suggestions."""
        if self.use_mock:
            return self._get_mock_suggestions()
        
        try:
            prompt = self._create_suggestion_prompt(travel_data)
            response_text = await self._generate_response(prompt)
            expected_keys = ['attractions', 'restaurants', 'activities']
            suggestions = self._parse_json_response(response_text, expected_keys)
            self.context["generated_suggestions"] = suggestions
            return suggestions
        except Exception as e:
            st.error(f"Error in generating suggestions: {str(e)}")
            if not self.use_mock:
                st.info("Falling back to mock suggestions...")
                self.use_mock = True
                return self._get_mock_suggestions()
            raise

    async def _generate_response(self, prompt: str) -> str:
        """Generate response from the model."""
        try:
            response = self.model.generate_content(prompt)
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            return response.text
        except Exception as e:
            if "quota" in str(e).lower():
                self.use_mock = True
            raise

    def _create_suggestion_prompt(self, travel_data: Dict[str, Any]) -> str:
        """Create a prompt for generating activity suggestions."""
        return f"""Generate a simple JSON response with exactly 3 attractions, 3 restaurants, and 3 activities.
Important: DO NOT use special characters or spaces in keys or values.
Example: {{"attractions":[{{"name":"TheLouvre","description":"Famousmuseum","cost":"20EUR","time_needed":"3hours"}}]}}

Location: {travel_data.get('destination')}
Budget: {travel_data.get('budget')}
Interests: {travel_data.get('interests', [])}

Required structure (on a single line):
{{"attractions":[{{"name":"Place1","description":"Simpledescription","cost":"XEUR","time_needed":"Xhours"}},...],"restaurants":[{{"name":"Place1","description":"Simpledescription","cost":"XEUR","cuisine":"Type"}},...],"activities":[{{"name":"Activity1","description":"Simpledescription","cost":"XEUR","time_needed":"Xhours"}},...]}}\n"""

    async def generate_itinerary(self, travel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a detailed travel itinerary."""
        if self.use_mock:
            return self._get_mock_itinerary()
        
        try:
            if not self.context.get("generated_suggestions"):
                self.context["generated_suggestions"] = await self.generate_suggestions(travel_data)
            
            prompt = self._create_itinerary_prompt(travel_data, self.context["generated_suggestions"])
            response_text = await self._generate_response(prompt)
            
            expected_keys = ['daily_plans', 'total_budget', 'general_tips', 'emergency_contacts']
            itinerary = self._parse_json_response(response_text, expected_keys)
            self._validate_itinerary(itinerary)
            self.context["final_itinerary"] = itinerary
            return itinerary
        except Exception as e:
            st.error(f"Error in generating itinerary: {str(e)}")
            if not self.use_mock:
                st.info("Falling back to mock itinerary...")
                self.use_mock = True
                return self._get_mock_itinerary()
            raise

    def _create_itinerary_prompt(self, travel_data: Dict[str, Any], suggestions: Dict[str, Any]) -> str:
        """Create a prompt for final itinerary generation."""
        attractions = [{"name": a['name'], "cost": a['cost']} for a in suggestions.get('attractions', [])]
        restaurants = [{"name": r['name'], "cost": r['cost']} for r in suggestions.get('restaurants', [])]
        activities = [{"name": a['name'], "cost": a['cost']} for a in suggestions.get('activities', [])]

        return f"""Generate a simple {travel_data.get('duration')}-day itinerary JSON.
Important: Use ONLY ASCII characters. NO spaces in keys or values.

Available places (use these names exactly):
Attractions: {attractions}
Restaurants: {restaurants}
Activities: {activities}

Rules:
1. Each day needs 2-3 activities
2. Include lunch between 12:00-14:00
3. Use 24-hour time format (e.g., "09:00") with quotes
4. Keep descriptions under 50 chars
5. Use simple costs (e.g., "20EUR")
6. Start dates from 2024-03-30
7. Only use these activity types: "activity", "meal", or "transport"
   - Use "activity" for attractions and activities
   - Use "meal" for restaurants
   - Use "transport" for travel between locations

Required JSON structure (one line):
{{"daily_plans":[{{"day":1,"date":"2024-03-30","activities":[{{"time":"09:00","duration":"2hours","description":"Visitmuseum","location":"TheLouvre","cost":"20EUR","type":"activity"}},{{"time":"12:00","duration":"1hour","description":"Lunchbreak","location":"RestaurantName","cost":"15EUR","type":"meal"}}],"daily_budget":"35EUR","notes":"Morningactivities"}}],"total_budget":"35EUR","general_tips":["Usemetro"],"emergency_contacts":{{"police":"17","ambulance":"15","tourist_police":"117"}}}}\n"""

    def _validate_itinerary(self, itinerary: Dict[str, Any]) -> None:
        """Validate the itinerary structure and content."""
        try:
            required_keys = ['daily_plans', 'total_budget', 'general_tips', 'emergency_contacts']
            self._validate_json_structure(itinerary, required_keys)

            if not isinstance(itinerary['daily_plans'], list) or len(itinerary['daily_plans']) == 0:
                raise ValueError("daily_plans must be a non-empty list")
            
            for day_idx, day in enumerate(itinerary['daily_plans'], 1):
                required_day_keys = ['day', 'date', 'activities', 'daily_budget']
                self._validate_json_structure(day, required_day_keys)
                
                if day['day'] != day_idx:
                    raise ValueError(f"Day numbers must be sequential. Got {day['day']}, expected {day_idx}")
                
                if not isinstance(day['activities'], list) or len(day['activities']) == 0:
                    raise ValueError(f"Day {day['day']} must have at least one activity")
                
                for activity in day['activities']:
                    required_activity_keys = ['time', 'duration', 'description', 'location', 'cost', 'type']
                    self._validate_json_structure(activity, required_activity_keys)
                    
                    activity['time'] = self._validate_time_format(activity['time'])
                    
                    valid_types = ['activity', 'meal', 'transport']
                    activity_type = activity['type'].lower()
                    
                    if activity_type not in valid_types:
                        raise ValueError(f"Invalid activity type: {activity['type']}")
            
        except Exception as e:
            st.error(f"Itinerary validation error: {str(e)}")
            raise

    def _validate_json_structure(self, data: Dict[str, Any], expected_keys: List[str]) -> None:
        """Validate JSON structure against expected keys."""
        missing_keys = [key for key in expected_keys if key not in data]
        if missing_keys:
            raise ValueError(f"Missing required keys: {', '.join(missing_keys)}")

    def _validate_time_format(self, time_str: str) -> str:
        """Validate and normalize time string format."""
        try:
            time_str = time_str.strip().strip('"\'')
            
            if re.match(r'^\d{1,2}$', time_str):
                time_str = f"{time_str}:00"
            
            if ':' not in time_str:
                if len(time_str) == 3:
                    time_str = f"{time_str[0]}:{time_str[1:]}"
                elif len(time_str) == 4:
                    time_str = f"{time_str[:2]}:{time_str[2:]}"
            
            datetime.strptime(time_str, '%H:%M')
            hours, minutes = map(int, time_str.split(':'))
            return f"{hours:02d}:{minutes:02d}"
        except Exception as e:
            st.warning(f"Invalid time format: {time_str}. Error: {str(e)}")
            return time_str

    def _clean_json_text(self, text: str) -> str:
        """Clean and extract JSON from text response."""
        try:
            text = text.strip()
            text = re.sub(r'```(?:json)?\n?', '', text)
            text = text.replace('```', '')
            
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                text = text[start:end + 1]
            else:
                raise ValueError("No valid JSON found")

            text = self._fix_over_escaped_quotes(text)
            text = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', text)
            text = re.sub(r'"([^"]+)"', lambda m: '"' + m.group(1).replace(' ', '') + '"', text)
            text = re.sub(r'"(\d{1,2})h"', r'"\1:00"', text)
            text = re.sub(r'"(\d{1,2})(\d{2})"', r'"\1:\2"', text)
            text = text.replace("'", '"')
            text = text.replace('...', '')

            if not text.strip().endswith('}'):
                text = self._repair_truncated_json(text)

            text = text.encode('ascii', 'ignore').decode()
            
            return text.strip()
        except Exception as e:
            st.error(f"Error cleaning JSON: {str(e)}")
            return text

    def _fix_over_escaped_quotes(self, text: str) -> str:
        """Fix over-escaped quotes in JSON text."""
        text = re.sub(r'"{2,}([^"]+)"{2,}', r'"\1"', text)
        text = re.sub(r'\\+"', '"', text)
        text = re.sub(r'"([^"]+)"', lambda m: '"' + m.group(1).replace(' ', '') + '"', text)
        return text

    def _repair_truncated_json(self, text: str) -> str:
        """Attempt to repair truncated JSON response."""
        open_braces = text.count('{')
        close_braces = text.count('}')
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        
        if open_braces > close_braces:
            text += '}' * (open_braces - close_braces)
        if open_brackets > close_brackets:
            text += ']' * (open_brackets - close_brackets)
        return text.strip()

    def _parse_json_response(self, response_text: str, expected_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Parse and validate JSON response from the API."""
        try:
            json_str = self._clean_json_text(response_text)
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                st.warning("Initial JSON parse failed, attempting repairs...")
                json_str = self._repair_truncated_json(json_str)
                try:
                    data = json.loads(json_str)
                    st.success("Successfully repaired JSON")
                except json.JSONDecodeError as e:
                    error_msg = self._format_json_error(json_str, e)
                    st.error(error_msg)
                    raise ValueError(f"JSON parse failed: {str(e)}")

            if expected_keys:
                self._validate_json_structure(data, expected_keys)

            for key in ['attractions', 'restaurants', 'activities']:
                if key in data and isinstance(data[key], list):
                    for item in data[key]:
                        if isinstance(item, dict):
                            for k in list(item.keys()):
                                if ' ' in k:
                                    item[k.replace(' ', '')] = item.pop(k)
                                if isinstance(item[k], str):
                                    item[k] = item[k].replace(' ', '')

            return data
        except Exception as e:
            st.error(f"Error processing response: {str(e)}")
            raise

    def _format_json_error(self, text: str, error: Exception) -> str:
        """Format JSON error message with context."""
        try:
            match = re.search(r'line (\d+) column (\d+)', str(error))
            if match:
                error_pos = int(match.group(2))
                context_start = max(0, error_pos - 50)
                context_end = min(len(text), error_pos + 50)
                context = text[context_start:context_end]
                
                return f"""JSON Parse Error: {str(error)}
                
                Context around error:
                {context}
                {' ' * (min(50, error_pos))}^
                
                Full text preview:
                {text[:200]}..."""
            return f"JSON Error: {str(error)}\nText preview: {text[:200]}..."
        except Exception as e:
            return f"Error formatting message: {str(e)}\nOriginal error: {str(error)}"