# Deployment Steps for AI Travel Planner

## 1. Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click "New" to create a new repository
3. Name it "ai-travel-planner"
4. Leave it public
5. Don't initialize with README (we already have one)
6. Click "Create repository"

## 2. Push to GitHub

After creating the repository, run these commands in your terminal (replace `<username>` with your GitHub username):

```bash
git remote add origin https://github.com/<username>/ai-travel-planner.git
git branch -M main
git push -u origin main
```

## 3. Deploy on Streamlit Cloud

1. Visit [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select the repository "ai-travel-planner"
5. Set the following:
   - Main file path: `app/main.py`
   - Branch: `main`

6. Add your secrets:
   - Click on ⚙️ (Settings)
   - Go to "Secrets" section
   - Add these secrets:
     ```
     GEMINI_API_KEY = "your_gemini_api_key"
     WEATHER_API_KEY = "your_weather_api_key"
     ```

7. Click "Deploy!"

Your app will be available at: `https://share.streamlit.io/<username>/ai-travel-planner/main`

## 4. Verify Deployment

1. Check if the app loads correctly
2. Test the functionality:
   - Enter travel preferences
   - Generate itinerary
   - Verify weather integration
   - Test dark/light theme

## 5. Troubleshooting

If you encounter issues:

1. Check the deployment logs in Streamlit Cloud
2. Verify your API keys are correctly set
3. Make sure all dependencies are in `requirements.txt`
4. Check if the app runs locally with:
   ```bash
   streamlit run app/main.py
   ```

## 6. Updates and Maintenance

To update the deployed app:
1. Make changes locally
2. Commit the changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
3. Streamlit Cloud will automatically redeploy