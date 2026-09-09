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
if "item_queue" not in st.session_state:
    st.session_state.item_queue = []

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
    menu = st.sidebar.radio("Navigation Menu", [
        "Item Entry", 
        "Hiriyur Active Displays", 
        "Davangere Active Displays", 
        "All Showrooms View", 
        "Dashboard & Reports", 
        "Out of Stock / Remove Section", 
        "Create Salesman Account"
    ])
else:
    menu = st.sidebar.radio("Navigation Menu", [
        "Item Entry", 
        "Hiriyur Active Displays", 
        "Davangere Active Displays", 
        "Dashboard & Reports", 
        "Out of Stock / Remove Section"
    ])

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

# ----------------- 1. ITEM ENTRY SECTION -----------------
elif menu == "Item Entry":
    st.title("🏢 Showroom Display & Item Master Management")
    
    def fetch_item_master_from_sheet():
        try:
            sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4mWSP3s6r7UIwn-kcX8Ogev4yXWTMpMLvL87PGTR_UwxKjkcbU9NNxy__mbkyYplhDHxvsD2nKFvW/pub?gid=1816720040&single=true&output=csv"
            df_sheet = pd.read_csv(sheet_url)
            items = df_sheet.iloc[:, 0].dropna().astype(str).tolist()
            return items
        except Exception as e:
            return [
                "1000 L 12X18 KK",
                "10015 16X16 CIBELA",
                "1002 CIGAR GLOSSY 1X1 ICON",
                "ANTALYA WHITE DG MATT 80X240",
                "ROYAL IMPERIAL BROWN GRANITE"
            ]

    item_master_designs = fetch_item_master_from_sheet()

    st.subheader("🔍 Search & Add Items to Queue")
    search_query = st.text_input("Search Item (Filter by Size, Company, or Design Name)").lower()
    filtered_items = [item for item in item_master_designs if search_query in item.lower()] if search_query else item_master_designs

    with st.form("item_queue_form"):
        location = st.selectbox("1. Select Location", ["HIRIYUR (Head Office)", "Davangere (Branch)"])
        
        col1, col2 = st.columns(2)
        with col1:
            stand_list = [f"ST-{i:02d}" for i in range(1, 51)]
            stand = st.selectbox("2. Select Stand Number", stand_list)
        with col2:
            board_list = [f"B-{i}" for i in range(1, 36)]
            board = st.selectbox("3. Select Board Number", board_list)
            
        selected_design = st.selectbox("4. Select Design from Filtered List", filtered_items)
        
        add_to_queue_btn = st.form_submit_button("➕ Add Item to Queue")
        
        if add_to_queue_btn:
            if selected_design:
                queue_item = {
                    "location": location,
                    "stand": stand,
                    "board": board,
                    "design": selected_design,
                    "status": "Available",
                    "added_by": st.session_state.username
                }
                st.session_state.item_queue.append(queue_item)
                st.success(f"Added '{selected_design}' to queue!")
            else:
                st.warning("Please select a design.")

    if st.session_state.item_queue:
        st.markdown("### 🛒 Items in Queue (Ready to Save)")
        df_queue = pd.DataFrame(st.session_state.item_queue)
        st.dataframe(df_queue, use_container_width=True)
        
        col_save, col_clear = st.columns(2)
        with col_save:
            if st.button("💾 Save All Items to Active Display"):
                try:
                    supabase.table("showroom_displays").insert(st.session_state.item_queue).execute()
                    st.success("All items successfully saved to Active Display!")
                    st.session_state.item_queue = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving to database: {e}")
        with col_clear:
            if st.button("🗑️ Clear Queue"):
                st.session_state.item_queue = []
                st.rerun()
    else:
        st.info("Queue is empty. Add items above to save them together.")

# ----------------- 2. HIRIYUR ACTIVE DISPLAYS -----------------
# ----------------- 2. HIRIYUR ACTIVE DISPLAYS -----------------
elif menu == "Hiriyur Active Displays":
    st.title("🏢 Hiriyur Showroom - Active Displays")
    active_search = st.text_input("Search Hiriyur Displays (by Design, Stand)").lower()
    
    try:
        response = supabase.table("showroom_displays").select("*").eq("status", "Available").execute()
        data = response.data
        if data:
            # Hiriyur filter (jo Davangere nahi hain ya jisme Hiriyur likha hai)
            data = [item for item in data if "davangere" not in str(item.get("location", "")).lower()]
            
            if active_search:
                data = [item for item in data if any(active_search in str(val).lower() for val in item.values())]
            
            if data:
                for item in data:
                    cols = st.columns([3, 2, 2, 2])
                    with cols[0]:
                        st.write(f"**Design:** {item.get('design', '')}")
                    with cols[1]:
                        st.write(f"**Stand:** {item.get('stand', '')}")
                    with cols[2]:
                        st.write(f"**Board:** {item.get('board', '')}")
                    with cols[3]:
                        if st.button("❌ Not Available", key=f"btn_h_{item['id']}"):
                            supabase.table("showroom_displays").update({"status": "Not Available"}).eq("id", item['id']).execute()
                            st.success("Moved to Remove section!")
                            st.rerun()
                    st.markdown("---")
            else:
                st.info("No active displays found in Hiriyur.")
        else:
            st.info("No active displays found in database.")
    except Exception as e:
        st.error(f"Error fetching Hiriyur displays: {e}")

# ----------------- 3. DAVANGERE ACTIVE DISPLAYS -----------------
elif menu == "Davangere Active Displays":
    st.title("🏛️ Davangere Branch - Active Displays")
    active_search = st.text_input("Search Davangere Displays (by Design, Stand)").lower()
    
    try:
        response = supabase.table("showroom_displays").select("*").eq("status", "Available").execute()
        data = response.data
        if data:
            # Davangere filter (sirf jisme davangere likha ho)
            data = [item for item in data if "davangere" in str(item.get("location", "")).lower()]
            
            if active_search:
                data = [item for item in data if any(active_search in str(val).lower() for val in item.values())]
            
            if data:
                for item in data:
                    cols = st.columns([3, 2, 2, 2])
                    with cols[0]:
                        st.write(f"**Design:** {item.get('design', '')}")
                    with cols[1]:
                        st.write(f"**Stand:** {item.get('stand', '')}")
                    with cols[2]:
                        st.write(f"**Board:** {item.get('board', '')}")
                    with cols[3]:
                        if st.button("❌ Not Available", key=f"btn_d_{item['id']}"):
                            supabase.table("showroom_displays").update({"status": "Not Available"}).eq("id", item['id']).execute()
                            st.success("Moved to Remove section!")
                            st.rerun()
                    st.markdown("---")
            else:
                st.info("No active displays found in Davangere. (Naye items entry karte waqt Location 'Davangere (Branch)' select karein).")
        else:
            st.info("No active displays found in database.")
    except Exception as e:
        st.error(f"Error fetching Davangere displays: {e}")# ----------------- 4. ALL SHOWROOMS VIEW (ADMIN) -----------------
elif menu == "All Showrooms View" and st.session_state.role == "admin":
    st.title("🌐 Combined View: All Showrooms")
    try:
        response = supabase.table("showroom_displays").select("*").eq("status", "Available").execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No active displays found.")
    except Exception as e:
        st.error(f"Error loading combined data: {e}")

# ----------------- 5. DASHBOARD & REPORTS -----------------
elif menu == "Dashboard & Reports":
    st.title("📊 Executive Dashboard & Performance Reports")
    try:
        res_all = supabase.table("showroom_displays").select("*").execute().data
        df_all = pd.DataFrame(res_all) if res_all else pd.DataFrame(columns=['id', 'location', 'stand', 'board', 'design', 'status', 'added_by'])
        
        if not df_all.empty:
            branch_tab1, branch_tab2 = st.tabs(["🏢 Hiriyur (Head Office)", "🏛️ Davangere (Branch)"])
            total_stands_count = 50
            
            with branch_tab1:
                st.subheader("Hiriyur Showroom Metrics")
                df_hiriyur = df_all[df_all['location'].str.contains("HIRIYUR", case=False, na=False)]
                active_hiriyur = df_hiriyur[df_hiriyur['status'] == "Available"]
                full_stands_h = active_hiriyur['stand'].nunique() if not active_hiriyur.empty else 0
                empty_stands_h = total_stands_count - full_stands_h
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Active Items", len(active_hiriyur))
                col2.metric("Full Stands", full_stands_h)
                col3.metric("Empty Stands", empty_stands_h)
                
                if not active_hiriyur.empty:
                    st.dataframe(active_hiriyur[['stand', 'board', 'design', 'added_by']], use_container_width=True)
                else:
                    st.info("No active displays in Hiriyur.")

            with branch_tab2:
                st.subheader("Davangere Showroom Metrics")
                df_davangere = df_all[df_all['location'].str.contains("Davangere", case=False, na=False)]
                active_davangere = df_davangere[df_davangere['status'] == "Available"]
                full_stands_d = active_davangere['stand'].nunique() if not active_davangere.empty else 0
                empty_stands_d = total_stands_count - full_stands_d
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Active Items", len(active_davangere))
                col2.metric("Full Stands", full_stands_d)
                col3.metric("Empty Stands", empty_stands_d)
                
                if not active_davangere.empty:
                    st.dataframe(active_davangere[['stand', 'board', 'design', 'added_by']], use_container_width=True)
                else:
                    st.info("No active displays in Davangere.")

            st.markdown("---")
            st.subheader("👨‍💼 Salesman Progress Report")
            if 'added_by' in df_all.columns:
                salesman_stats = df_all.groupby('added_by').agg(
                    Total_Selections=('design', 'count'),
                    Active_Displays=('status', lambda x: (x == 'Available').sum()),
                    Removed_Displays=('status', lambda x: (x == 'Not Available').sum())
                ).reset_index()
                st.dataframe(salesman_stats, use_container_width=True)
            else:
                st.info("Salesman tracking data is populating.")
        else:
            st.info("No data available in the database.")
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

# ----------------- 6. OUT OF STOCK / REMOVE SECTION -----------------
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
