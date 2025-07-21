
import streamlit as st
import requests
from skyfield.api import load, EarthSatellite, wgs84
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="Real-Time ISS Tracker", layout="wide")

# Cached function to get ISS position
@st.cache_data(ttl=10) # Cache data for 10 seconds to avoid hitting API too often
def get_iss_position():
    """Fetches TLE and calculates current ISS position."""
    try:
        url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        lines = response.text.strip().split('\n')

        ts = load.timescale()
        satellite = EarthSatellite(lines[1], lines[2], lines[0], ts)

        geocentric = satellite.at(ts.now())
        subpoint = wgs84.subpoint(geocentric)

        return {
            'lat': subpoint.latitude.degrees,
            'lon': subpoint.longitude.degrees,
            'elevation_km': subpoint.elevation.km
        }
    except Exception as e:
        st.error(f"Could not fetch live ISS data: {e}")
        return None

st.title("🛰️ Real-Time ISS Tracker Dashboard")

# Get position
position = get_iss_position()

if position:
    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Latitude", f"{position['lat']:.4f}°")
    col2.metric("Longitude", f"{position['lon']:.4f}°")
    col3.metric("Altitude", f"{position['elevation_km']:.2f} km")

    # Display map
    df = pd.DataFrame([position])
    st.map(df, zoom=2, size=20)

    st.write(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.warning("Could not display ISS position.")

# Auto-refresh logic
time.sleep(10) # Wait 10 seconds
st.rerun()
