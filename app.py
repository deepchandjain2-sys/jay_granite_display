import streamlit as st
import pandas as pd
import requests
import io
import json
import os
import re

st.set_page_config(page_title="Jay Granite Tiles Display", layout="wide")

# --- Persistent Data Storage Files ---
USERS_FILE = "users_data.json"
DISPLAYS_FILE = "displays_data.json"

def load_json_file(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return default_val
    return default_val

def save_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# Load users and displays from permanent files
if "users" not in st.session_state:
    st.session_state.users = load_json_file(USERS_FILE, {"admin": {"password": "123", "mobile": "9999999999", "role": "admin"}})

if "displays" not in st.session_state:
    st.session_state.displays = load_json_file(DISPLAYS_FILE, [])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- Google Sheet Live Integration ---
# --- Google Sheet Live Integration ---
def load_designs_from_sheet():
    try:
        # Apni Google Sheet ka Publish to Web wala CSV link yahan daalein
        sheet_url = "https://docs.google.com/spreadsheets/d/1qhBmCLkdAKQMXrbyKSRfCEHybfdxfv2XIABLxO6pA/pub?output=csv"
        response = requests.get(sheet_url, timeout=5)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            column_name = 'ITEM NAME' if 'ITEM NAME' in df.columns else df.columns[0]
            designs = df[column_name].dropna().astype(str).tolist()
            if designs:
                return designs
    except Exception as e:
        pass
    
    # Agar sheet load na ho toh yeh items dikhenge taaki aapka kaam na ruke
    return [
        "1000 L 12X18 KK",
        "0015 16X16 CIBELA",
        "1002 EI 2x1 Torino",
        "1005 CIGAR GLOSSY 1X1 ICON",
        "Mega HI 2x1 Varmora",
        "DOVER NERO 2X2 ITALICA"
    ]
# --- AUTHENTICATION SECTION ---
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
                    save_json_file(USERS_FILE, st.session_state.users)
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
                    save_json_file(USERS_FILE, st.session_state.users)
                    st.success("Password updated successfully!")
                else:
                    st.error("Mobile number not found.")

else:
    st.sidebar.title(f"👤 {st.session_state.username} ({st.session_state.role.capitalize()})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.title("🏢 Showroom Display Management")
    location = st.selectbox("Select Showroom Location", ["Hiriyur", "Davangere"])
    
    tab1, tab2, tab3 = st.tabs(["📌 Assign Multiple Tiles (Same Board)", "📋 Selected Displays", "⚠️ Unavailable & Clear"])
    
    with tab1:
        st.header(f"Assign Multiple Tiles on Same Board - {location}")
        
        # Search Bar for Tile Selection
        item_search = st.text_input("🔎 Search Tile Design from Google Sheet List").strip().lower()
        filtered_designs = design_list
        if item_search:
            filtered_designs = [d for d in design_list if item_search in d.lower()]
        
        with st.form("assign_form"):
            stand_no = st.selectbox("Select Stand No (1 - 50)", list(range(1, 51)), key="m_stand")
            board_no = st.selectbox("Select Board No (1 - 35)", list(range(1, 36)), key="m_board")
            
            selected_designs = st.multiselect("Select Filtered Tile Designs", filtered_designs)
            
            assign_btn = st.form_submit_button("Add Tiles to Board")
            if assign_btn:
                if not selected_designs:
                    st.warning("Please select at least one tile design.")
                else:
                    added_count = 0
                    for design in selected_designs:
                        exists = any(
                            d['location'] == location and 
                            d['stand'] == stand_no and 
                            d['board'] == board_no and 
                            d['design'] == design 
                            for d in st.session_state.displays
                        )
                        if not exists:
                            st.session_state.displays.append({
                                'location': location,
                                'stand': stand_no,
                                'board': board_no,
                                'design': design,
                                'status': 'Available'
                            })
                            added_count += 1
                    save_json_file(DISPLAYS_FILE, st.session_state.displays)
                    st.success(f"{added_count} tile(s) successfully added to Stand {stand_no}, Board {board_no} at {location}!")

    with tab2:
        st.header(f"Active Displays - {location}")
        
        search_query = st.text_input("🔍 Search (e.g. S1, B1, S1B1 or Design Name)").strip().lower()
        
        loc_displays = [d for d in st.session_state.displays if d['location'] == location and d['status'] == 'Available']
        
        if search_query:
            has_s = 's' in search_query
            has_b = 'b' in search_query
            nums = re.findall(r'\d+', search_query)
            
            filtered = []
            for d in loc_displays:
                st_str = str(d['stand'])
                bo_str = str(d['board'])
                de_str = d['design'].lower()
                
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
            loc_displays = sorted(loc_displays, key=lambda x: (x['stand'], x['board']))
            
            for i, item in enumerate(loc_displays):
                col1, col2, col3, col4 = st.columns([2, 2, 4, 2])
                col1.write(f"**Stand No:** {item['stand']}")
                col2.write(f"**Board No:** {item['board']}")
                col3.write(f"**Design:** {item['design']}")
                if col4.button("Mark Unavailable", key=f"unavail_{location}_{item['stand']}_{item['board']}_{i}"):
                    for d in st.session_state.displays:
                        if d['location'] == location and d['stand'] == item['stand'] and d['board'] == item['board'] and d['design'] == item['design']:
                            d['status'] = 'Unavailable'
                    save_json_file(DISPLAYS_FILE, st.session_state.displays)
                    st.rerun()

    with tab3:
        st.header(f"Unavailable Section & Clear Boards - {location}")
        unavail_displays = [d for d in st.session_state.displays if d['location'] == location and d['status'] == 'Unavailable']
        
        if not unavail_displays:
            st.info("No unavailable items.")
        else:
            for i, item in enumerate(unavail_displays):
                col1, col2, col3, col4 = st.columns([2, 2, 3, 2])
                col1.write(f"**Stand No:** {item['stand']}")
                col2.write(f"**Board No:** {item['board']}")
                col3.write(f"**Design:** {item['design']}")
                if col4.button("Remove / Clear Tile", key=f"clear_{location}_{item['stand']}_{item['board']}_{i}"):
                    st.session_state.displays = [
                        d for d in st.session_state.displays 
                        if not (d['location'] == location and d['stand'] == item['stand'] and d['board'] == item['board'] and d['design'] == item['design'])
                    ]
                    save_json_file(DISPLAYS_FILE, st.session_state.displays)
                    st.success("Item cleared successfully!")
                    st.rerun()
