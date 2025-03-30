import streamlit as st
import os
import asyncio
from dotenv import load_dotenv
from utils.gemini import GeminiAPI
from utils.weather import WeatherAPI
from components.user_input import UserInputForm
from components.itinerary import ItineraryDisplay

# Load environment variables
load_dotenv()

# Configure page settings
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to run async code in Streamlit
def async_to_sync(coroutine):
    """Helper function to run async code in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

# Function to load CSS
def load_css():
    """Load custom CSS styles."""
    try:
        with open("static/css/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load CSS: {str(e)}")

# Function to load JavaScript
def load_js():
    """Load JavaScript files."""
    # Add Font Awesome for icons
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """, unsafe_allow_html=True)
    
    # Load theme initialization script
    try:
        with open("static/js/theme_init.js") as f:
            init_js = f.read()
            st.markdown(f"<script>{init_js}</script>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load theme initialization script: {str(e)}")
    
    # Load main theme script
    try:
        with open("static/js/theme.js") as f:
            js_content = f.read()
            st.markdown(f"""
            <script>
            {js_content}
            </script>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load theme.js: {str(e)}")
        
        # Add fallback script
        st.markdown("""
        <script>
        (function() {
            // Basic theme handler fallback
            function applyTheme() {
                const savedTheme = localStorage.getItem('theme') || 'light';
                document.body.setAttribute('data-theme', savedTheme);
                const stApp = document.querySelector('.stApp');
                if (stApp) stApp.setAttribute('data-theme', savedTheme);
            }
            
            // Apply theme immediately and when DOM is ready
            applyTheme();
            document.addEventListener('DOMContentLoaded', applyTheme);
            
            // Create theme toggle button
            function createToggleButton() {
                if (document.getElementById('theme-toggle')) return;
                
                const theme = localStorage.getItem('theme') || 'light';
                const button = document.createElement('button');
                button.id = 'theme-toggle';
                button.className = 'theme-toggle';
                button.innerHTML = theme === 'light' 
                    ? '<i class="fas fa-moon"></i><span>Dark Mode</span>' 
                    : '<i class="fas fa-sun"></i><span>Light Mode</span>';
                
                button.onclick = function() {
                    const newTheme = theme === 'light' ? 'dark' : 'light';
                    localStorage.setItem('theme', newTheme);
                    window.location.reload();
                };
                
                document.body.appendChild(button);
            }
            
            // Apply when DOM is loaded
            document.addEventListener('DOMContentLoaded', createToggleButton);
            // Try immediately in case DOM is already loaded
            if (document.readyState !== 'loading') createToggleButton();
        })();
        </script>
        """, unsafe_allow_html=True)

# Initialize theme in session state
if 'theme' not in st.session_state:
    # Check if there's a stored theme preference
    saved_theme = None
    try:
        # Try to read from localStorage via a hidden div and JavaScript
        get_theme_js = """
        <div id="theme-detector" style="display:none;"></div>
        <script>
            document.getElementById('theme-detector').textContent = localStorage.getItem('theme') || 'light';
        </script>
        """
        st.markdown(get_theme_js, unsafe_allow_html=True)
        # Default to light theme
        st.session_state.theme = 'light'
    except:
        st.session_state.theme = 'light'

# Theme toggle function in Python (for sidebar button)
def toggle_theme():
    """Toggle between light and dark theme."""
    current = st.session_state.get('theme', 'light')
    st.session_state.theme = 'dark' if current == 'light' else 'light'
    
    # Apply theme change via JavaScript
    st.markdown(f"""
    <script>
        localStorage.setItem('theme', '{st.session_state.theme}');
        document.body.setAttribute('data-theme', '{st.session_state.theme}');
        const stApp = document.querySelector('.stApp');
        if (stApp) stApp.setAttribute('data-theme', '{st.session_state.theme}');
        // Reload to apply changes consistently
        window.location.reload();
    </script>
    """, unsafe_allow_html=True)

# Load CSS and JS
load_css()
load_js()

# Initialize APIs with error handling
gemini_api = None
weather_api = None

try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    weather_api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not gemini_api_key:
        st.warning("Gemini API key not found. Using demo mode.")
        gemini_api = GeminiAPI(api_key="demo", use_mock=True)
    else:
        try:
            gemini_api = GeminiAPI(api_key=gemini_api_key)
        except Exception as e:
            st.warning("Failed to initialize Gemini API. Using demo mode.")
            gemini_api = GeminiAPI(api_key="demo", use_mock=True)
    
    if not weather_api_key:
        st.warning("OpenWeather API key not found. Weather data may be limited.")
        weather_api = WeatherAPI(api_key="demo")
    else:
        weather_api = WeatherAPI(api_key=weather_api_key)
        
except Exception as e:
    st.error(f"Failed to initialize application: {str(e)}")
    st.stop()

if not gemini_api or not weather_api:
    st.error("Failed to initialize required APIs")
    st.stop()

def main():
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🌍 AI Travel Planner")
    st.markdown("### Your Personal AI-Powered Travel Assistant")
    st.markdown('</div>', unsafe_allow_html=True)

    # Initialize session state with default values
    defaults = {
        'current_step': 0,
        'travel_data': {},
        'itinerary': None,
        'suggestions': None,
        'suggestions_status': 'pending',  # pending, loading, ready, error
        'itinerary_status': 'pending',    # pending, loading, ready, error
        'error_message': None
    }
    
    for var, default in defaults.items():
        if var not in st.session_state:
            st.session_state[var] = default
    
    # Show any persistent error message
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        if st.button("Clear Error"):
            st.session_state.error_message = None
            st.rerun()

    # Sidebar navigation
    with st.sidebar:
        # Add theme toggle button to sidebar
        current_theme = st.session_state.get('theme', 'light')
        icon = "☀️" if current_theme == 'dark' else "🌙"
        if st.button(f"{icon} Toggle Theme", key="sidebar_theme_toggle"):
            toggle_theme()
        
        st.header("Navigation")
        steps = ["User Details", "Preferences", "Generate Itinerary", "Final Plan"]
        current_step = st.radio("Steps", steps, index=st.session_state.current_step)
        st.session_state.current_step = steps.index(current_step)

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
            This AI-powered travel planner helps you create 
            personalized travel itineraries based on your 
            preferences and requirements.
        """)

    # Progress bar
    progress = (st.session_state.current_step + 1) / len(steps)
    st.progress(progress)

    # Main content area
    if st.session_state.current_step == 0:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.subheader("📝 Basic Travel Details")
        UserInputForm.show_basic_details()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.current_step == 1:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.subheader("🎯 Travel Preferences")
        UserInputForm.show_preferences()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.current_step == 2:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.subheader("🔄 Generating Your Itinerary")
        
        if not UserInputForm.validate_travel_data():
            st.error("Please complete all required information in the previous steps.")
            st.session_state.current_step = 0
            st.rerun()
            
        # Initialize suggestions in session state if not present
        if 'suggestions' not in st.session_state:
            st.session_state.suggestions = None

        if st.button("🔍 Get Suggestions", key="get_suggestions_btn"):
            st.session_state.suggestions_status = 'loading'
            try:
                with st.spinner("🔍 Finding personalized suggestions for your trip..."):
                    suggestions = async_to_sync(
                        gemini_api.generate_suggestions(st.session_state.travel_data)
                    )
                    st.session_state.suggestions = suggestions
                    st.session_state.suggestions_status = 'ready'
                    st.success("✨ Suggestions generated successfully!")
                    st.rerun()

            except Exception as e:
                st.session_state.suggestions_status = 'error'
                st.session_state.error_message = f"Failed to generate suggestions: {str(e)}"
                st.error(st.session_state.error_message)
                st.info("Please try again or modify your preferences.")
                return

        # Display suggestions if they're ready
        if st.session_state.suggestions_status == 'ready' and st.session_state.suggestions:
            st.subheader("📍 Suggested Activities")
            cols = st.columns(3)
            
            # Display attractions
            with cols[0]:
                st.write("### Attractions")
                for attraction in st.session_state.suggestions.get('attractions', []):
                    if isinstance(attraction, dict):
                        with st.container():
                            st.markdown(f"""
                            **{attraction.get('name', '')}**  
                            {attraction.get('description', '')}  
                            💰 {attraction.get('cost', '')} | ⏱️ {attraction.get('time_needed', '')}
                            """)
                    else:
                        st.write(f"- {attraction}")
            
            # Display restaurants
            with cols[1]:
                st.write("### Restaurants")
                for restaurant in st.session_state.suggestions.get('restaurants', []):
                    if isinstance(restaurant, dict):
                        with st.container():
                            st.markdown(f"""
                            **{restaurant.get('name', '')}**  
                            {restaurant.get('description', '')}  
                            💰 {restaurant.get('cost', '')} | 🍽️ {restaurant.get('cuisine', '')}
                            """)
                    else:
                        st.write(f"- {restaurant}")
            
            # Display activities
            with cols[2]:
                st.write("### Activities")
                for activity in st.session_state.suggestions.get('activities', []):
                    if isinstance(activity, dict):
                        with st.container():
                            st.markdown(f"""
                            **{activity.get('name', '')}**  
                            {activity.get('description', '')}  
                            💰 {activity.get('cost', '')} | ⏱️ {activity.get('time_needed', '')}
                            """)
                    else:
                        st.write(f"- {activity}")

            st.markdown("---")
            st.write("Please review the suggestions and click below to generate your itinerary.")
            
            generate_btn = st.button("✨ Generate Itinerary", key="generate_btn")
            if generate_btn or st.session_state.itinerary_status == 'loading':
                st.session_state.itinerary_status = 'loading'
                try:
                    with st.spinner("🌟 Creating your personalized travel plan..."):
                        col1, col2 = st.columns(2)
                        with col1:
                            with st.spinner("Generating itinerary..."):
                                itinerary = async_to_sync(
                                    gemini_api.generate_itinerary(st.session_state.travel_data)
                                )
                        with col2:
                            with st.spinner("Fetching weather data..."):
                                weather_data = async_to_sync(
                                    weather_api.get_forecast(
                                        st.session_state.travel_data.get("destination"),
                                        st.session_state.travel_data.get("start_date"),
                                        st.session_state.travel_data.get("end_date")
                                    )
                                )
                        
                        st.session_state.itinerary = {
                            "plan": itinerary,
                            "weather": weather_data
                        }
                        st.session_state.itinerary_status = 'ready'
                        st.success("🎉 Your personalized travel itinerary is ready!")
                        st.session_state.current_step += 1
                        st.rerun()
                except Exception as e:
                    st.session_state.itinerary_status = 'error'
                    error_msg = f"Failed to generate itinerary: {str(e)}"
                    st.session_state.error_message = error_msg
                    st.error(error_msg)
                    st.info("Please try again or modify your preferences.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.current_step == 3:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.subheader("🎉 Your Personalized Travel Itinerary")
        if st.session_state.itinerary:
            try:
                ItineraryDisplay.show_itinerary(
                    st.session_state.itinerary["plan"],
                    st.session_state.itinerary["weather"]
                )
            except Exception as e:
                st.error(f"Error displaying itinerary: {str(e)}")
                if st.button("Regenerate Itinerary"):
                    st.session_state.current_step = 2
                    st.rerun()
        else:
            st.warning("Please generate an itinerary first.")
            st.session_state.current_step = 2
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Add a reset button in the sidebar
    with st.sidebar:
        if st.button("Start Over"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        if st.button("Restart Application"):
            st.session_state.clear()
            st.rerun()