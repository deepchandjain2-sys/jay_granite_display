import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Page Configuration
st.set_page_config(page_title="Jay Granite Tiles Display Management", layout="wide")

# Supabase Connection Setup
SUPABASE_URL = "https://gedzazirwxaxabnppchc.supabase.co"
SUPABASE_KEY = "sb_publishable_oi8gTy66MVBCtq-DasQHAA_M1Wvgg-g"

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
    st.title("🔐 Jay Granite Tiles - Login")
    
    with st.form("login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Login")
        
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

# ----------------- LOGOUT & SIDEBAR -----------------
st.sidebar.write(f"Logged in as: **{st.session_state.username}** ({st.session_state.role.upper()})")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# Navigation based on role
if st.session_state.role == "admin":
    menu = st.sidebar.radio("Navigation", ["Display & Item Entry", "Out of Stock / Remove Section", "Create Salesman Account"])
else:
    menu = st.sidebar.radio("Navigation", ["Display & Item Entry", "Out of Stock / Remove Section"])

# ----------------- ADMIN: CREATE SALESMAN -----------------
if st.session_state.role == "admin" and menu == "Create Salesman Account":
    st.title("👤 Create Salesman User ID & Password")
    
    with st.form("create_user_form"):
        new_user = st.text_input("New Salesman Username")
        new_pass = st.text_input("New Salesman Password", type="password")
        create_btn = st.form_submit_button("Create User")
        
        if create_btn:
            if new_user and new_pass:
                try:
                    supabase.table("users").insert([
                        {"username": new_user, "password": new_pass, "role": "salesman"}
                    ]).execute()
                    st.success(f"Salesman '{new_user}' created successfully!")
                except Exception as e:
                    st.error(f"Error creating user: {e}")
            else:
                st.warning("Please enter both username and password.")

# ----------------- DISPLAY & ITEM ENTRY (Points 2, 3, 4) -----------------
elif menu == "Display & Item Entry":
    st.title("🏢 Showroom Display & Item Management")
    
    st.subheader("➕ New Item Entry to Stand & Board")
    with st.form("item_entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Location (e.g., Hiriyur)")
            # Point 2: Stand select 1 to 50
            stand = st.selectbox("Select Stand Number", [str(i) for i in range(1, 51)])
        with col2:
            # Point 3: Board select 1 to 35
            board = st.selectbox("Select Board Number", [str(i) for i in range(1, 36)])
            # Point 4: Design selection from Item Master / Text input
            design = st.text_input("Design Name / Code (Item Master)")
            status = st.selectbox("Status", ["Available", "Out of Stock"])
            
        submit_item = st.form_submit_button("Save Item Entry")
        
        if submit_item:
            if location and design:
                try:
                    supabase.table("showroom_displays").insert([{
                        "location": location,
                        "stand": stand,
                        "board": board,
                        "design": design,
                        "status": status
                    }]).execute()
                    st.success("Item successfully assigned to stand!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding item: {e}")
            else:
                st.warning("Please fill in all required fields.")

    # View Current Display List & Option to Send to Remove (Point 5)
    st.markdown("---")
    st.subheader("📋 Current Active Displays")
    try:
        response = supabase.table("showroom_displays").select("*").eq("status", "Available").execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            # Point 5: Out of stock hone par send to remove section
            st.write("### Mark Item as Out of Stock / Send to Remove")
            item_ids = [item['id'] for item in data]
            selected_id = st.selectbox("Select Item ID to mark Out of Stock", item_ids)
            if st.button("Move to Out of Stock"):
                supabase.table("showroom_displays").update({"status": "Out of Stock"}).eq("id", selected_id).execute()
                st.success("Item moved to Out of Stock / Remove section!")
                st.rerun()
        else:
            st.info("No active displays found.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

# ----------------- OUT OF STOCK & PERMANENT REMOVE SECTION (Points 5, 6) -----------------
elif menu == "Out of Stock / Remove Section":
    st.title("🗑️ Out of Stock & Permanent Item Removal")
    
    try:
        response = supabase.table("showroom_displays").select("*").eq("status", "Out of Stock").execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            st.write("### Permanently Remove Item from Stand (Point 6)")
            remove_ids = [item['id'] for item in data]
            selected_remove_id = st.selectbox("Select Item ID to Permanently Remove", remove_ids)
            
            if st.button("Permanently Delete Item"):
                supabase.table("showroom_displays").delete().eq("id", selected_remove_id).execute()
                st.success("Item permanently removed from stand and database!")
                st.rerun()
        else:
            st.info("No items currently in Out of Stock / Remove section.")
    except Exception as e:
        st.error(f"Error loading removal section: {e}")
