import streamlit as st
import pandas as pd
import os
import json
import re

st.set_page_config(page_title="Jay Granite Tiles Display", layout="wide")

USERS_FILE = "users_data.json"
DISPLAYS_FILE = "displays_data.json"

def load_local_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_local_data(filename, data):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "123", "mobile": "9999999999", "role": "admin"},
        "DEEPCHAND JAIN": {"password": "deep1965", "mobile": "9888888888", "role": "admin"}
    }

if "displays" not in st.session_state:
    st.session_state.displays = load_local_data(DISPLAYS_FILE)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

def load_designs_from_sheet():
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4mWSP3s6r7Ulwn-kcX8Ogev4yXWTMpMLvL87PGTR_UwxKjkcbU9NNxy_mbkyYlphDHxvsD2nKFVw/pub?output=csv"
    try:
        df = pd.read_csv(sheet_url)
        column_name = 'ITEM NAME' if 'ITEM NAME' in df.columns else df.columns[0]
        designs = df[column_name].dropna().astype(str).tolist()
        if designs:
            return designs
    except Exception as e:
        pass
    
    return [
        "1000 L 12X18 KK",
        "0015 16X16 CIBELA",
        "1002 EI 2x1 Torino",
        "1005 CIGAR GLOSSY 1X1 ICON"
    ]

design_list = load_designs_from_sheet()

if not st.session_state.logged_in:
    st.title("🪟 Jay Granite Tiles - Portal")
    st.subheader("Hiriyur & Davangere Display Management")
    
    auth_mode = st.selectbox("Choose Action", ["Login", "Register New User", "Forgot Password"])
    
    if auth_mode == "Login":
        with st.form("login_form"):
            user_id = st.text_input("User ID or Mobile Number")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                matched_user = None
                for uname, udata in st.session_state.users.items():
                    if uname == user_id or udata["mobile"] == user_id:
                        if udata["password"] == password:
                            matched_user = uname
                            st.session_state.role = udata["role"]
                
                if matched_user:
                    st.session_state.logged_in = True
                    st.session_state.username = matched_user
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid User ID/Mobile or Password")
                    
    elif auth_mode == "Register New User":
        with st.form("reg_form"):
            new_user = st.text_input("Choose User ID (Text/Number)")
            new_mobile = st.text_input("Mobile Number (For Login & Reset)")
            new_pass = st.text_input("Password", type="password")
            role_choice = st.selectbox("Role", ["salesman", "admin"])
            reg_submit = st.form_submit_button("Register")
            
            if reg_submit:
                if new_user in st.session_state.users:
                    st.error("User ID already exists!")
                elif not new_user or not new_mobile or not new_pass:
                    st.warning("Please fill all fields.")
                else:
                    st.session_state.users[new_user] = {
                        "password": new_pass,
                        "mobile": new_mobile,
                        "role": role_choice
                    }
                    st.success("Registration Successful! Please switch to Login tab.")

    elif auth_mode == "Forgot Password":
        with st.form("forgot_form"):
            f_mobile = st.text_input("Enter Registered Mobile Number")
            f_new_pass = st.text_input("Enter New Password", type="password")
            f_submit = st.form_submit_button("Update Password")
            
            if f_submit:
                found = False
                for uname, udata in st.session_state.users.items():
                    if udata["mobile"] == f_mobile:
                        udata["password"] = f_new_pass
                        found = True
                if found:
                    st.success("Password updated successfully!")
                else:
                    st.error("Mobile number not found.")

else:
    st.sidebar.title(f"👤 {st.session_state.username} ({st.session_state.role.capitalize()})")
    
    if st.session_state.role == "admin":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔄 Restore Displays Data")
        uploaded_json_backup = st.sidebar.file_uploader("Upload Displays JSON (.json)", type=["json"])
        if uploaded_json_backup is not None:
            try:
                raw_data = json.load(uploaded_json_backup)
                if isinstance(raw_data, list):
                    st.session_state.displays = raw_data
                    save_local_data(DISPLAYS_FILE, raw_data)
                    st.sidebar.success("Displays restored successfully!")
                    st.rerun()
                else:
                    st.sidebar.error("Invalid format.")
            except Exception as e:
                st.sidebar.error("Error reading JSON file.")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.title("🏢 Showroom Display Management")
    location = st.selectbox("Select Showroom Location", ["Hiriyur", "Davangere"])
    
    if st.session_state.role == "admin":
        tab1, tab2, tab3, tab4 = st.tabs(["📌 Assign Multiple Tiles", "📋 Selected Displays", "⚠️ Unavailable & Clear", "⚙️ Manage Users (Admin)"])
    else:
        tab1, tab2, tab3 = st.tabs(["📌 Assign Multiple Tiles", "📋 Selected Displays", "⚠️ Unavailable & Clear"])
    
    with tab1:
        st.header(f"Assign Multiple Tiles on Same Board - {location}")
        
        # Stand and Board numbers fixed outside form so they don't reset automatically
        col_s, col_b = st.columns(2)
        with col_s:
            stand_no = st.selectbox("Select Stand No (1 - 50)", list(range(1, 51)), key="fixed_stand")
        with col_b:
            board_no = st.selectbox("Select Board No (1 - 35)", list(range(1, 36)), key="fixed_board")
        
        company_filter = st.text_input("🔎 Filter by Company / Name (e.g. ITALICA, KAG, Johnson)").strip().lower()
        filtered_designs = design_list
        if company_filter:
            filtered_designs = [d for d in design_list if company_filter in d.lower()]
        
        selected_designs = st.multiselect("Select Multiple Tile Designs for Stand " + str(stand_no) + ", Board " + str(board_no), filtered_designs)
        
        if st.button("Add All Selected Tiles to Board"):
            if not selected_designs:
                st.warning("Please select at least one tile design.")
            else:
                current_displays = load_local_data(DISPLAYS_FILE)
                if not current_displays:
                    current_displays = st.session_state.displays or []
                    
                added_count = 0
                for design in selected_designs:
                    exists = any(
                        str(d.get('location', '')).strip().lower() == location.strip().lower() and 
                        int(d.get('stand', 0)) == stand_no and 
                        int(d.get('board', 0)) == board_no and 
                        str(d.get('design', '')).strip() == str(design).strip()
                        for d in current_displays
                    )
                    if not exists:
                        current_displays.append({
                            'location': location,
                            'stand': stand_no,
                            'board': board_no,
                            'design': design,
                            'status': 'Available'
                        })
                        added_count += 1
                
                st.session_state.displays = current_displays
                save_local_data(DISPLAYS_FILE, current_displays)
                st.success(f"{added_count} tile(s) successfully added to Stand {stand_no}, Board {board_no}!")
                st.rerun()

    with tab2:
        st.header(f"Active Displays - {location}")
        
        current_displays = load_local_data(DISPLAYS_FILE)
        if not current_displays:
            current_displays = st.session_state.displays or []
            
        search_query = st.text_input("🔍 Search (e.g. S1, B1, S1B1 or Design Name)").strip().lower()
        
        loc_displays = []
        if current_displays and isinstance(current_displays, list):
            loc_displays = [
                d for d in current_displays 
                if str(d.get('location', '')).strip().lower() == location.strip().lower() 
                and str(d.get('status', 'Available')).strip().capitalize() == 'Available'
            ]
        
        if search_query:
            has_s = 's' in search_query
            has_b = 'b' in search_query
            nums = re.findall(r'\d+', search_query)
            
            filtered = []
            for d in loc_displays:
                st_str = str(d.get('stand', ''))
                bo_str = str(d.get('board', ''))
                de_str = str(d.get('design', '')).lower()
                
                match = False
                if has_s and has_b and len(nums) >= 2:
                    if nums[0] == st_str and nums[1] == bo_str:
                        match = True
                elif has_s and not has_b and len(nums) >= 1:
                    if nums[0] == st_str:
                        match = True
                elif has_b and not has_s and len(nums) >= 1:
                    if nums[0] == bo_str:
                        match = True
                else:
                    if search_query in st_str or search_query in bo_str or search_query in de_str:
                        match = True
                if match:
                    filtered.append(d)
            loc_displays = filtered
        
        if not loc_displays:
            st.info("No matching active displays found.")
        else:
            loc_displays = sorted(loc_displays, key=lambda x: (int(x.get('stand', 0)), int(x.get('board', 0))))
            
            for i, item in enumerate(loc_displays):
                col1, col2, col3, col4 = st.columns([2, 2, 4, 2])
                col1.write(f"**Stand No:** {item.get('stand')}")
                col2.write(f"**Board No:** {item.get('board')}")
                col3.write(f"**Design:** {item.get('design')}")
                if col4.button("Mark Unavailable", key=f"unavail_{location}_{item.get('stand')}_{item.get('board')}_{i}_{item.get('design')}"):
                    fresh_data = load_local_data(DISPLAYS_FILE) or st.session_state.displays or []
                    for d in fresh_data:
                        if (str(d.get('location', '')).strip().lower() == location.strip().lower() and 
                            int(d.get('stand', 0)) == int(item.get('stand', 0)) and 
                            int(d.get('board', 0)) == int(item.get('board', 0)) and 
                            str(d.get('design', '')).strip() == str(item.get('design', '')).strip()):
                            d['status'] = 'Unavailable'
                    st.session_state.displays = fresh_data
                    save_local_data(DISPLAYS_FILE, fresh_data)
                    st.success("Marked as Unavailable!")
                    st.rerun()

    with tab3:
        st.header(f"Unavailable Section & Clear Boards - {location}")
        fresh_data = load_local_data(DISPLAYS_FILE) or st.session_state.displays or []
        unavail_displays = []
        if fresh_data and isinstance(fresh_data, list):
            unavail_displays = [d for d in fresh_data if str(d.get('location', '')).strip().lower() == location.strip().lower() and str(d.get('status', '')).strip().capitalize() == 'Unavailable']
        
        if not unavail_displays:
            st.info("No unavailable items.")
        else:
            text_data = f"--- UNAVAILABLE TILES LIST ({location}) ---\n\n"
            for item in unavail_displays:
                text_data += f"Stand: {item.get('stand')} | Board: {item.get('board')} | Design: {item.get('design')}\n"
            
            st.download_button(
                label="📥 Download / Print Unavailable List",
                data=text_data,
                file_name=f"unavailable_tiles_{location.lower()}.txt",
                mime="application/text"
            )
            st.markdown("---")
            
            for i, item in enumerate(unavail_displays):
                col1, col2, col3, col4 = st.columns([2, 2, 3, 2])
                col1.write(f"**Stand No:** {item.get('stand')}")
                col2.write(f"**Board No:** {item.get('board')}")
                col3.write(f"**Design:** {item.get('design')}")
                if col4.button("Remove / Clear Tile", key=f"clear_{location}_{item.get('stand')}_{item.get('board')}_{i}_{item.get('design')}"):
                    latest_data = load_local_data(DISPLAYS_FILE) or st.session_state.displays or []
                    latest_data = [
                        d for d in latest_data 
                        if not (str(d.get('location', '')).strip().lower() == location.strip().lower() and 
                                int(d.get('stand', 0)) == int(item.get('stand', 0)) and 
                                int(d.get('board', 0)) == int(item.get('board', 0)) and 
                                str(d.get('design', '')).strip() == str(item.get('design', '')).strip())
                    ]
                    st.session_state.displays = latest_data
                    save_local_data(DISPLAYS_FILE, latest_data)
                    st.success("Item cleared successfully!")
                    st.rerun()

    if st.session_state.role == "admin":
        with tab4:
            st.header("⚙️ Manage Registered Users / Salesmen")
            with st.form("add_user_form"):
                st.subheader("➕ Add New Staff Account")
                new_staff_id = st.text_input("New User ID (Name)")
                new_staff_mobile = st.text_input("Staff Mobile Number")
                new_staff_pass = st.text_input("Staff Password", type="password")
                staff_role = st.selectbox("Role", ["salesman", "admin"])
                add_btn = st.form_submit_button("Create User Account")
                
                if add_btn:
                    if not new_staff_id or not new_staff_mobile or not new_staff_pass:
                        st.warning("Please fill all fields.")
                    elif new_staff_id in st.session_state.users:
                        st.error("User ID already exists!")
                    else:
                        st.session_state.users[new_staff_id] = {
                            "password": new_staff_pass,
                            "mobile": new_staff_mobile,
                            "role": staff_role
                        }
                        st.success(f"Staff account '{new_staff_id}' successfully created!")
                        st.rerun()
            
            st.markdown("---")
            st.subheader("📋 Existing Users List")
            for uname, udata in list(st.session_state.users.items()):
                col1, col2, col3 = st.columns([3, 3, 2])
                col1.write(f"**User ID:** {uname}")
                col2.write(f"**Role:** {udata.get('role', 'salesman').capitalize()} (Mobile: {udata.get('mobile', '')})")
                
                if uname != "admin":
                    if col3.button("🗑️ Delete User", key=f"del_user_{uname}"):
                        if uname in st.session_state.users:
                            del st.session_state.users[uname]
                            st.success(f"User '{uname}' successfully deleted!")
                            st.rerun()
                else:
                    col3.write("🔒 Protected")
