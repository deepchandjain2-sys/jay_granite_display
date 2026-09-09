import streamlit as st
import pandas as pd
from supabase import create_client, Client
import urllib.request
import json

# Page Configuration for Professional Look
st.set_page_config(page_title="Jay Granite Tiles - Management System", layout="wide")

# Supabase Connection Setup
SUPABASE_URL = "https://gedzazirwxaxabnppchc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdlZHphemlyd3hheGFibnBwY2hjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg2ODAyOTgsImV4cCI6MjEwNDI1NjI5OH0.CSCbuwInWJtGpL7w_nMFU6ElGWnXxr67bKeMWuTpMMM"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ----------------- LOGIN PAGE -----------------
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🏢 Jay Granite Tiles - Secure Login</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit_login:
                if username_input == "admin" and password_input == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.username = "admin"
                    st.session_state.role = "admin"
                    st.success("Admin Login Successful!")
                    st.rerun()
                else:
                    try:
                        res = supabase.table("users").select("*").eq("username", username_input).eq("password", password_input).execute()
                        if res.data:
                            st.session_state.logged_in = True
                            st.session_state.username = username_input
                            st.session_state.role = "salesman"
                            st.success("Salesman Login Successful!")
                            st.rerun()
                        else:
                            st.error("Invalid Username or Password")
                    except Exception as e:
                        st.error(f"Login error: {e}")
        st.stop()

# ----------------- SIDEBAR NAVIGATION -----------------
st.sidebar.markdown(f"### 👤 User: {st.session_state.username.upper()}")
st.sidebar.markdown(f"**Role:** `{st.session_state.role.upper()}`")
st.sidebar.markdown("---")

if st.session_state.role == "admin":
    menu = st.sidebar.radio("Navigation Menu", ["Display & Item Entry", "Out of Stock / Remove Section", "Create Salesman Account"])
else:
    menu = st.sidebar.radio("Navigation Menu", ["Display & Item Entry", "Out of Stock / Remove Section"])

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# ----------------- ADMIN: CREATE SALESMAN ACCOUNT -----------------
if st.session_state.role == "admin" and menu == "Create Salesman Account":
    st.title("👤 Salesman Account Management")
    
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_user = st.text_input("New Salesman Username")
        with col2:
            new_pass = st.text_input("New Salesman Password", type="password")
            
        create_btn = st.form_submit_button("Create Salesman Account")
        
        if create_btn:
            if new_user and new_pass:
                try:
                    supabase.table("users").insert([
                        {"username": new_user, "password": new_pass, "role": "salesman"}
                    ]).execute()
                    st.success(f"Salesman account '{new_user}' created successfully!")
                except Exception as e:
                    st.error(f"Error creating user: {e}")
            else:
                st.warning("Please fill in both username and password fields.")

# ----------------- DISPLAY & ITEM ENTRY SECTION -----------------
elif menu == "Display & Item Entry":
    st.title("🏢 Showroom Display & Item Master Management")
    
    # Fetch live item master from Google Sheet CSV export link
    def fetch_item_master_from_sheet():
        try:
            sheet_url = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdlZHphemlyd3hheGFibnBwY2hjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg2ODAyOTgsImV4cCI6MjEwNDI1NjI5OH0.CSCbuwInWJtGpL7w_nMFU6ElGWnXxr67bKeMWuTpMMM"
            df_sheet = pd.read_csv(sheet_url)
            items = df_sheet.iloc[:, 0].dropna().astype(str).tolist()
            return items
        except Exception as e:
            return [
                "1000 L 12X18 KK",
                "10015 16X16 CIBELA",
                "1002 CIGAR GLOSSY 1X1 ICON"
            ]

    item_master_designs = fetch_item_master_from_sheet()

    with st.form("item_entry_form"):
        st.subheader("➕ Assign Multiple Designs to Stand & Board (Status: Available)")
        
        location = st.selectbox("1. Select Location", ["HIRIYUR (Head Office)", "Davangere (Branch)"])
        
        col1, col2 = st.columns(2)
        with col1:
            stand_list = [f"ST-{i:02d}" for i in range(1, 51)]
            stand = st.selectbox("2. Select Stand Number", stand_list)
        with col2:
            board_list = [f"B-{i}" for i in range(1, 36)]
            board = st.selectbox("3. Select Board Number", board_list)
            
        selected_designs = st.multiselect(
            "4. Select Design(s) from Item Master (Multiple allowed for this Board)", 
            item_master_designs
        )
        
        # Default status jab select hoke submit hoga toh "Available" rahega
        status = "Available"
        submit_item = st.form_submit_button("Save Entries to Display")
        
        if submit_item:
            if selected_designs:
                try:
                    insert_data = []
                    for design in selected_designs:
                        insert_data.append({
                            "location": location,
                            "stand": stand,
                            "board": board,
                            "design": design,
                            "status": status
                        })
                    
                    supabase.table("showroom_displays").insert(insert_data).execute()
                    st.success(f"Successfully added {len(selected_designs)} design(s) as Available!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving entries: {e}")
            else:
                st.warning("Please select at least one design from the Item Master.")

    # Current Active Displays Table with "Not Available" Action
    st.markdown("---")
    st.subheader("📋 Current Active Showroom Displays (Available)")
    try:
        response = supabase.table("showroom_displays").select("*").eq("status", "Available").execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("### 🔄 Mark Item as Not Available (Send to Remove Section)")
            item_ids = [item['id'] for item in data]
            selected_id = st.selectbox("Select Item ID to mark Not Available", item_ids)
            if st.button("Move to Not Available / Remove Section"):
                supabase.table("showroom_displays").update({"status": "Not Available"}).eq("id", selected_id).execute()
                st.success("Item marked as Not Available and moved to Remove section!")
                st.rerun()
        else:
            st.info("No active available displays found in the database.")
    except Exception as e:
        st.error(f"Error fetching active displays: {e}")

# ----------------- OUT OF STOCK / REMOVE SECTION -----------------
elif menu == "Out of Stock / Remove Section":
    st.title("🗑️ Not Available & Permanent Stand Removal Section")
    
    try:
        response = supabase.table("showroom_displays").select("*").eq("status", "Not Available").execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("### ❌ Permanent Removal from Stand & Database")
            remove_ids = [item['id'] for item in data]
            selected_remove_id = st.selectbox("Select Item ID for Permanent Deletion", remove_ids)
            
            if st.button("Permanently Delete from System"):
                supabase.table("showroom_displays").delete().eq("id", selected_remove_id).execute()
                st.success("Item permanently removed from stand and database!")
                st.rerun()
        else:
            st.info("No items currently marked as Not Available.")
    except Exception as e:
        st.error(f"Error loading removal section: {e}")
