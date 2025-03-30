# AI Travel Planner

An AI-powered travel planner that creates personalized travel itineraries using Gemini AI. Built with Streamlit and Python.

## Features

- Personalized travel suggestions
- Day-by-day itinerary planning
- Weather integration
- Interactive timeline visualization
- Dark/Light theme support

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-travel-planner
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```
GEMINI_API_KEY=your_gemini_api_key
WEATHER_API_KEY=your_weather_api_key
```

4. Run the application:
```bash
streamlit run app/main.py
```

## Streamlit Cloud Deployment

1. Fork this repository to your GitHub account

2. Visit [Streamlit Cloud](https://streamlit.io/cloud)

3. Create a new app and select your forked repository

4. Set the following:
   - Main file path: `app/main.py`
   - Python version: 3.10+

5. Add your secrets in the Streamlit Cloud dashboard:
   - Navigate to ⚙️ -> Settings -> Secrets
   - Add the following secrets:
     ```toml
     GEMINI_API_KEY = "your_gemini_api_key"
     WEATHER_API_KEY = "your_weather_api_key"
     ```

6. Deploy the app

## Project Structure

```
ai_travelling_agent/
├── app/
│   ├── components/      # UI components
│   ├── utils/          # Helper functions
│   └── main.py         # Main application
├── static/             # Static assets
│   ├── css/           # Stylesheets
│   └── js/            # JavaScript files
└── .streamlit/        # Streamlit configuration
```

## Usage

1. Enter your travel preferences:
   - Destination
   - Dates
   - Budget
   - Interests

2. Get personalized suggestions

3. Generate and view your itinerary

## License

[MIT License](LICENSE)

## Credits

Built using:
- [Streamlit](https://streamlit.io)
- [Gemini AI](https://deepmind.google/technologies/gemini/)
- [Plotly](https://plotly.com/python/)