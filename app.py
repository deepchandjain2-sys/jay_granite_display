import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Page Configuration
st.set_page_config(page_title="Jay Granite Tiles Display", layout="wide")

# Supabase Connection Setup
SUPABASE_URL = "https://gedzazirwxaxabnppchc.supabase.co"
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

# Main App UI & Logic
st.title("Jay Granite Tiles Display Management")

displays_data = fetch_showroom_displays()
if displays_data:
    df_displays = pd.DataFrame(displays_data)
    st.dataframe(df_displays, use_container_width=True)
else:
    st.info("No displays found in Supabase database yet.")
