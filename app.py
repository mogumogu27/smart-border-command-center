import streamlit as st
import boto3
import pandas as pd
import random
import time
from datetime import datetime
import pydeck as pdk
from streamlit_autorefresh import st_autorefresh
import hashlib

# Configure AWS connections with explicit region
REGION = 'us-east-1'
s3 = boto3.client('s3', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table('BorderThreatAlerts')

# --- USER CONFIGURATION ---
BUCKET_NAME = 'border-sensor-data-mrigank-v2' 

st.set_page_config(page_title="Border Command Center", layout="wide")
st.title("Live Smart Border Command Center - India")

# 1. Real-Time Auto-Refresh Engine
st_autorefresh(interval=35000, limit=10000, key="data_refresh")

# 2. Auto-Generate Data Simulation Section
st.sidebar.header("Simulation Engine")
st.sidebar.write("Turn on to simulate live nationwide border sensor activity.")
auto_generate = st.sidebar.toggle("Auto-Generate Live Sensor Data")

if 'last_upload_time' not in st.session_state:
    st.session_state.last_upload_time = 0

if auto_generate:
    current_time = time.time()
    if current_time - st.session_state.last_upload_time >= 35:
        try:
            zones = ['A', 'B', 'C']
            zone = random.choice(zones)
            motion = random.randint(5, 60)
            temp = random.randint(15, 35)
            
            csv_content = f"Zone,Hour,Temperature,Motion_Count\n{zone},{datetime.now().hour},{temp},{motion}"
            file_name = f"simulated_sensor_{int(time.time())}.csv"
            
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=file_name,
                Body=csv_content.encode('utf-8')
            )
            st.session_state.last_upload_time = current_time
            st.sidebar.success(f"Dispatched: {file_name} (Network {zone})")
            st.cache_data.clear()
        except Exception as e:
            st.sidebar.error(f"S3 Upload Error: {e}")
    else:
        time_left = int(35 - (current_time - st.session_state.last_upload_time))
        st.sidebar.info(f"Next sensor dispatch in {time_left} seconds...")
else:
    st.sidebar.info("Simulation OFF. Displaying database & pre-dataset fallback records.")

ZONE_LOCATIONS = {
    'A': [
        {'name': 'Gujarat Border (Kutch)', 'lat': 23.8000, 'lon': 68.8000, 'unit': 'BSF Sector HQ, Bhuj'},
        {'name': 'Rajasthan Border (Barmer)', 'lat': 25.7000, 'lon': 70.3000, 'unit': 'Alpha-2 Outpost, Barmer'},
        {'name': 'Rajasthan Border (Jaisalmer)', 'lat': 26.9157, 'lon': 70.9083, 'unit': 'Bravo-3 Outpost, Jaisalmer'},
        {'name': 'Rajasthan Border (Bikaner)', 'lat': 28.0000, 'lon': 72.3000, 'unit': 'BSF Unit, Bikaner'},
        {'name': 'Punjab Border (Amritsar)', 'lat': 31.6000, 'lon': 74.3000, 'unit': 'Delta-4 Base, Amritsar'},
        {'name': 'J&K Border (Jammu)', 'lat': 32.7266, 'lon': 74.8570, 'unit': 'Alpha-1 Base, Jammu'}
    ],
    'B': [
        {'name': 'Ladakh Border (LAC)', 'lat': 34.1000, 'lon': 78.1000, 'unit': 'ITBP Post, Leh'},
        {'name': 'Himachal Border (Kinnaur)', 'lat': 31.8000, 'lon': 78.6000, 'unit': 'Echo-5 Station, Reckong Peo'},
        {'name': 'Uttarakhand Border (Pithoragarh)', 'lat': 30.5000, 'lon': 80.5000, 'unit': 'ITBP Sector HQ, Bareilly'},
        {'name': 'Sikkim Border (Nathu La)', 'lat': 27.7000, 'lon': 88.7000, 'unit': 'Foxtrot-6 Base, Gangtok'},
        {'name': 'Arunachal Border (Tawang)', 'lat': 27.5000, 'lon': 92.0000, 'unit': 'Charlie-9 Station, Tezpur'},
        {'name': 'Arunachal Border (Anjaw)', 'lat': 28.0000, 'lon': 96.0000, 'unit': 'Golf-7 Outpost, Walong'}
    ],
    'C': [
        {'name': 'West Bengal Border (South)', 'lat': 22.0000, 'lon': 88.9000, 'unit': 'BSF HQ, Kolkata'},
        {'name': 'West Bengal Border (North)', 'lat': 25.0000, 'lon': 88.0000, 'unit': 'Hotel-8 Base, Malda'},
        {'name': 'Meghalaya Border (Dawki)', 'lat': 25.2000, 'lon': 91.0000, 'unit': 'India-9 Station, Shillong'},
        {'name': 'Tripura Border (Agartala)', 'lat': 23.7000, 'lon': 91.3000, 'unit': 'BSF Sector HQ, Agartala'},
        {'name': 'Mizoram Border (Champhai)', 'lat': 23.3000, 'lon': 93.0000, 'unit': 'Assam Rifles Post, Aizawl'},
        {'name': 'Manipur Border (Moreh)', 'lat': 24.3000, 'lon': 94.1000, 'unit': 'Juliet-10 Outpost, Imphal'}
    ]
}

@st.cache_data(ttl=30, show_spinner=False)
def fetch_data():
    try:
        response = table.scan()
        items = response.get('Items', [])
        
        # FALLBACK LOGIC: If DynamoDB is completely empty, load the default pre-dataset
        if not items:
            # Create a default fallback DataFrame matching your pre-dataset structure
            fallback_data = [{
                'Zone': 'C',
                'Hour': 3,
                'Temperature': 20,
                'Motion_Count': 45,
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Threat_Level': 'High'
            }]
            df = pd.DataFrame(fallback_data)
        else:
            df = pd.DataFrame(items)
            
        if 'Motion_Count' in df.columns:
            df['Motion_Count'] = pd.to_numeric(df['Motion_Count'], errors='coerce')
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            df = df.sort_values(by='Timestamp', ascending=False)
            
        if 'Zone' not in df.columns:
            df['Zone'] = 'C'
        df['Zone'] = df['Zone'].fillna('C')
            
        def assign_location(row):
            zone = row.get('Zone', 'C')
            if zone not in ZONE_LOCATIONS:
                zone = 'C'
            ts_str = str(row.get('Timestamp', '0'))
            hash_idx = int(hashlib.md5(ts_str.encode()).hexdigest(), 16) % len(ZONE_LOCATIONS[zone])
            return pd.Series(ZONE_LOCATIONS[zone][hash_idx])
            
        loc_data = df.apply(assign_location, axis=1)
        df['Region'] = loc_data['name']
        df['Latitude'] = loc_data['lat']
        df['Longitude'] = loc_data['lon']
        df['Nearest_Unit'] = loc_data['unit']
            
        return df
    except Exception:
        return pd.DataFrame()

data = fetch_data()

if data.empty:
    st.info("No data found.")
else:
    total_alerts = len(data)
    high_threat_data = data[data['Threat_Level'] == 'High'] if 'Threat_Level' in data.columns else pd.DataFrame()
    
    col1, col2 = st.columns(2)
    col1.metric("Total Sensor Events", total_alerts)
    col2.metric("Critical Alerts (Emails Dispatched)", len(high_threat_data), delta_color="inverse")
    
    st.markdown("---")
    st.subheader("📍 Live Threat Map")
    
    if not high_threat_data.empty:
        latest_breach = high_threat_data.iloc[0]
        st.error(f"🚨 **CRITICAL BREACH LOCATED:** {latest_breach.get('Region', 'Unknown')} | **Coordinates:** {latest_breach.get('Latitude', 0.0)}° N, {latest_breach.get('Longitude', 0.0)}° E | **Dispatching:** {latest_breach.get('Nearest_Unit', 'Unknown')} immediately.")
    else:
        st.success("All borders secure. No active high-level threats.")

    map_df = data.head(150).copy() 
    
    if not map_df.empty:
        map_df['color'] = map_df['Threat_Level'].map(lambda x: [255, 0, 0, 200] if x == 'High' else [0, 255, 0, 100])
        map_df['radius'] = map_df['Threat_Level'].map(lambda x: 45000 if x == 'High' else 20000)
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            map_df,
            get_position=["Longitude", "Latitude"],
            get_color="color",
            get_radius="radius",
            pickable=True
        )
        
        view_state = pdk.ViewState(latitude=22.5, longitude=79.0, zoom=4.2, pitch=30)
        
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Region: {Region}\nCoordinates: {Latitude}° N, {Longitude}° E\nThreat Level: {Threat_Level}"}
        ), height=500)
    
    st.markdown("---")
    st.subheader("📧 Nationwide SNS Dispatch Log")
    if not high_threat_data.empty:
        cols_to_show = ['Timestamp', 'Region', 'Latitude', 'Longitude', 'Threat_Level', 'Nearest_Unit']
        cols_to_show = [c for c in cols_to_show if c in high_threat_data.columns]
        st.dataframe(high_threat_data[cols_to_show].head(50), use_container_width=True, height=400)
    else:
        st.write("No high-threat emails have been dispatched yet.")