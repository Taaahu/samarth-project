import pandas as pd
import numpy as np 
import streamlit as st

st.set_page_config(layout="wide", page_title="Project Samarth: Agri-Climate Q&A")

@st.cache_data
def load_data():
    df_crop = pd.read_csv("crop_production.csv")
    df_rain = pd.read_csv("rainfall in india 1901-2015.csv")

    df_crop.rename(columns={'Crop_Year': 'YEAR'}, inplace=True) 
    df_rain.rename(columns={'SUBDIVISION': 'STATE', 'ANNUAL': 'RAINFALL_MM'}, inplace=True)

    df_crop['STATE'] = df_crop['State_Name'].str.upper().str.strip()
    df_rain['STATE'] = df_rain['STATE'].str.upper().str.strip()
    df_rain.dropna(subset=['RAINFALL_MM'], inplace=True)

    state_mapping = {
        'ANDAMAN & NICOBAR ISLANDS': 'ANDAMAN AND NICOBAR ISLANDS', 'ORISSA': 'ODISHA',
        'NAGA MANI MIZO TRIPURA': 'NAGALAND', 'ASSAM & MEGHALAYA': 'ASSAM',
        'GUJARAT REGION': 'GUJARAT', 'SAURASHTRA & KUTCH': 'GUJARAT',
        'KONKAN & GOA': 'MAHARASHTRA', 'MADHYA MAHARASHTRA': 'MAHARASHTRA', 
        'MATATHWADA': 'MAHARASHTRA', 'VIDARBHA': 'MAHARASHTRA', 
        'HARYANA DELHI & CHANDIGARH': 'PUNJAB', 'WEST RAJASTHAN': 'RAJASTHAN',
        'EAST RAJASTHAN': 'RAJASTHAN', 'LAKSHADWEEP': 'LAKSHADWEEP', 
    }
    df_rain['STATE'] = df_rain['STATE'].replace(state_mapping)

    df_merged = pd.merge(
        df_crop, 
        df_rain[['STATE', 'YEAR', 'RAINFALL_MM']], 
        on=['STATE', 'YEAR'], 
        how='inner'
    )
    return df_merged

df_merged = load_data()

def analyze_crop_and_rain(state_x, state_y, num_years, crop_type, top_m_crops):
    latest_year = df_merged['YEAR'].max()
    start_year = latest_year - num_years + 1
    
    df_filtered = df_merged[(df_merged['YEAR'] >= start_year) & 
                            (df_merged['STATE'].isin([state_x, state_y]))].copy()
    
    if df_filtered.empty:
        return f"\n***  Q&A Error ***\nData not available for selected states and period ({start_year}-{latest_year}). Check state names or years."
        
    rain_summary = df_filtered.groupby('STATE')['RAINFALL_MM'].mean().round(2)
    df_crops_filtered = df_filtered[df_filtered['Crop'].str.contains(crop_type, case=False, na=False)]
    top_crops_raw = df_crops_filtered.groupby(['STATE', 'Crop'])['Production'].sum()

    top_crops_x = []
    if state_x in top_crops_raw.index.get_level_values('STATE'):
        top_crops_x = top_crops_raw.loc[state_x].nlargest(top_m_crops).index.tolist()
        
    top_crops_y = []
    if state_y in top_crops_raw.index.get_level_values('STATE'):
        top_crops_y = top_crops_raw.loc[state_y].nlargest(top_m_crops).index.tolist()

    rain_x = rain_summary.get(state_x, "N/A (Data Missing)")
    rain_y = rain_summary.get(state_y, "N/A (Data Missing)")
    
    answer = f"\n***  Q&A System Answer (Synthesized Insight) ***\n"
    answer += f"Data analyzed for the period: {start_year} to {latest_year} ({num_years} years).\n"
    answer += f"\n[PART A: RAINFALL COMPARISON]\n"
    answer += f"Average Annual Rainfall in {state_x}: {rain_x} mm.\n"
    answer += f"Average Annual Rainfall in {state_y}: {rain_y} mm.\n"
    
    answer += f"\n[PART B: TOP CROP PRODUCTION]\n"
    answer += f"Top {top_m_crops} produced crops of type '{crop_type}' in {state_x}: {', '.join(top_crops_x) or 'No data found'}\n"
    answer += f"Top {top_m_crops} produced crops of type '{crop_type}' in {state_y}: {', '.join(top_crops_y) or 'No data found'}\n"
    
    answer += f"\n[DATA TRACEABILITY]\n"
    answer += f"Source 1: crop_production.csv\n"
    answer += f"Source 2: rainfall in india 1901-2015.csv\n"

    return answer

st.title("🇮🇳 Project Samarth: Agri-Climate Q&A System")
st.markdown("---")

st.subheader("Analyze Crop Production vs. Rainfall (Sample Question 1)")

st.markdown("**Enter the parameters for the question:** *Compare the average annual rainfall in State_X and State_Y for the last N available years...*")
state_x = st.text_input("State 1 (State_X)", "MAHARASHTRA").upper()
state_y = st.text_input("State 2 (State_Y)", "PUNJAB").upper()
num_years = st.slider("Last N Years (for analysis period)", min_value=1, max_value=20, value=5)
crop_type = st.text_input("Crop Type (Crop_Type_C)", "RICE").upper()
top_m_crops = st.slider("Top M Crops to List", min_value=1, max_value=5, value=3)

if st.button('Synthesize Data & Get Answer'):
    with st.spinner('Analyzing integrated data...'):
        try:
            result = analyze_crop_and_rain(state_x, state_y, num_years, crop_type, top_m_crops)
            st.code(result)
            st.success("Analysis Complete! Scroll up for the full report.")
        except Exception as e:
            st.error(f" Error during analysis. Please check State names or the merged data: {e}")

st.markdown("---")
st.caption(f"System Status: Data Integrated. Total rows processed: {df_merged.shape[0]}.")
