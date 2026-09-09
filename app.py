import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Page Configuration
st.set_page_config(page_title="Jay Granite Tiles Display", layout="wide")

# Supabase Connection Setup
SUPABASE_URL = "sb_publishable_oi8gTy66MV8CTq-DasQHAA_M1Wvgg-g"
SUPABASE_KEY = "sb_publishable_oi8gTy66MV8CTq-DasQHAA_M1Wvgg-g"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch Showroom Displays from Supabase
def fetch_showroom_displays():
    try:
        response = supabase.table("showroom_displays").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Database error: {e}")
        return []

# Fetch Users from Supabase
def fetch_users():
    try:
        response = supabase.table("users").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Users fetch error: {e}")
        return []

# Initialize Session State using Supabase Data
if "users" not in st.session_state:
    st.session_state.users = fetch_users()

if "displays" not in st.session_state:
    st.session_state.displays = fetch_showroom_displays()

# Main App UI & Logic
st.title("Jay Granite Tiles Display Management")

# Quick check to display fetched data
if st.button("Refresh Data"):
    st.session_state.users = fetch_users()
    st.session_state.displays = fetch_showroom_displays()
    st.success("Data refreshed successfully from Supabase!")

st.write("### Showroom Displays")
displays_data = fetch_showroom_displays()
if displays_data:
    df_displays = pd.DataFrame(displays_data)
    st.dataframe(df_displays, use_container_width=True)
else:
    st.info("No displays found in Supabase database yet.")
