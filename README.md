# Military Data Analysis Platform

## Overview
This Streamlit app visualizes global military data, including:
- Interactive World Map of military power
- Country-to-country military strength comparisons
- Defense budget trends over time
- Top defense companies analysis
- Military exports/imports data
- Historical major conflicts dashboard
- Future military power projections (2047)

## Structure
```
home.py           # Main landing page
pages/            # Each file corresponds to a section of the app
  World_Map.py
  Military_Strength.py
  Defense_Budget.py
  Defense_Companies.py
  Trade_Data.py
  Major_Conflicts.py
  Predictions_2047.py
assets/           # Place project images or documents here
requirements.txt   # Python dependencies
README.md          # Project documentation
```

## Running the App
1. Clone or unzip the project.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the home page:
   ```
   streamlit run home.py
   ```
4. Use the sidebar to navigate between pages.

## Assets
Add any images or related documents to the `assets` folder and reference them in your pages.

