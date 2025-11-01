import pandas as pd
import numpy as np 

df_crop = pd.read_csv("crop_production.csv")
df_rain = pd.read_csv("rainfall in india 1901-2015.csv")

print("--- Data Loading Complete ---")

df_crop.rename(columns={'Crop_Year': 'YEAR'}, inplace=True) 

df_rain.rename(columns={'SUBDIVISION': 'STATE', 'ANNUAL': 'RAINFALL_MM'}, inplace=True)

df_crop['STATE'] = df_crop['State_Name'].str.upper().str.strip()
df_rain['STATE'] = df_rain['STATE'].str.upper().str.strip()

df_rain.dropna(subset=['RAINFALL_MM'], inplace=True)

state_mapping = {
    'ANDAMAN & NICOBAR ISLANDS': 'ANDAMAN AND NICOBAR ISLANDS',
    'ORISSA': 'ODISHA',
    'NAGA MANI MIZO TRIPURA': 'NAGALAND', 
    'ASSAM & MEGHALAYA': 'ASSAM',
    'GUJARAT REGION': 'GUJARAT',
    'SAURASHTRA & KUTCH': 'GUJARAT',
    'LAKSHADWEEP': 'LAKSHADWEEP',
    'KONKAN & GOA': 'MAHARASHTRA', 
    'MADHYA MAHARASHTRA': 'MAHARASHTRA', 
    'MATATHWADA': 'MAHARASHTRA', 
    'VIDARBHA': 'MAHARASHTRA', 
    'HARYANA DELHI & CHANDIGARH': 'PUNJAB', 
    'WEST RAJASTHAN': 'RAJASTHAN',
    'EAST RAJASTHAN': 'RAJASTHAN',
}

df_rain['STATE'] = df_rain['STATE'].replace(state_mapping)

df_merged = pd.merge(df_crop, 
                     df_rain[['STATE', 'YEAR', 'RAINFALL_MM']], 
                     on=['STATE', 'YEAR'], 
                     how='inner') 

print("PHASE 1 COMPLETE: DATA INTEGRATION SUCCESSFUL ---")
print("Integrated Dataset Total Rows:", df_merged.shape[0])
print(df_merged.head(2))

# --- PHASE 2: INTELLIGENT Q&A LOGIC ---

def analyze_crop_and_rain(state_x, state_y, num_years, crop_type, top_m_crops):
    
    latest_year = df_merged['YEAR'].max()
    start_year = latest_year - num_years + 1
    
    df_filtered = df_merged[(df_merged['YEAR'] >= start_year) & 
                            (df_merged['STATE'].isin([state_x, state_y]))].copy()

    if df_filtered.empty:
        return f"\n*** Q&A Error ***\nData not available for selected states and period ({start_year}-{latest_year}). Check state names or years."
        
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

    
    answer = f"\n*** Q&A System Answer (Synthesized Insight) ***\n"
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



print(analyze_crop_and_rain(
    state_x='MAHARASHTRA', 
    state_y='PUNJAB', 
    num_years=5, 
    crop_type='RICE', 
    top_m_crops=3
))