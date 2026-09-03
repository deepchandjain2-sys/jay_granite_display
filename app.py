import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="Jay Granite Tiles Display", layout="wide")

USERS_FILE = "users_data.json"
DISPLAYS_FILE = "displays_data.json"

def load_local_data(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return default_val
    return default_val

def save_local_data(filename, data):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

default_users = {
    "admin": {"password": "123", "mobile": "9999999999", "role": "admin"},
    "DEEPCHAND JAIN": {"password": "deep1965", "mobile": "9888888888", "role": "admin"}
}

if "users" not in st.session_state:
    st.session_state.users = load_local_data(USERS_FILE, default_users)

if "displays" not in st.session_state:
    st.session_state.displays = load_local_data(DISPLAYS_FILE, [])

if "temp_design_queue" not in st.session_state:
    st.session_state.temp_design_queue = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

def load_designs_from_sheet():
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4mWSP3s6r7UIwn-kcX8Ogev4yXWTMpMLvL87PGTR_UwxKjkcbU9NNxy__mbkyYplhDHxvsD2nKFvW/pub?gid=1816720040&single=true&output=csv"
    try:
        df = pd.read_csv(sheet_url)
        column_name = 'ITEM NAME' if 'ITEM NAME' in df.columns else df.columns[0]
        designs = df[column_name].dropna().astype(str).tolist()
        if designs:
            return designs
    except:
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
                user_role = ""
                for uname, udata in st.session_state.users.items():
                    if uname.strip().lower() == user_id.strip().lower() or str(udata.get("mobile")) == str(user_id).strip():
                        if str(udata.get("password")) == str(password):
                            matched_user = uname
                            user_role = udata.get("role", "salesman")
                
                if matched_user:
                    st.session_state.logged_in = True
                    st.session_state.username = matched_user
                    st.session_state.role = user_role
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid User ID/Mobile or Password")
                    
    elif auth_mode == "Register New User":
        with st.form("reg_form"):
            new_user = st.text_input("Choose User ID (Text/Number)")
            new_mobile = st.text_input("Mobile Number")
            new_pass = st.text_input("Password", type="password")
            role_choice = st.selectbox("Role", ["salesman", "admin"])
            reg_submit = st.form_submit_button("Register")
            
            if reg_submit:
                if new_user in st.session_state.users:
                    st.error("User ID already exists!")
                elif not new_user or not new_mobile or not new_pass:
                    st.warning("Please fill all fields.")
                else:
                    st.session_state.users[new_user] = {"password": new_pass, "mobile": new_mobile, "role": role_choice}
                    save_local_data(USERS_FILE, st.session_state.users)
                    st.success("Registration Successful! Please switch to Login tab.")

    elif auth_mode == "Forgot Password":
        with st.form("forgot_form"):
            f_mobile = st.text_input("Enter Registered Mobile Number")
            f_new_pass = st.text_input("Enter New Password", type="password")
            f_submit = st.form_submit_button("Update Password")
            
            if f_submit:
                found = False
                for uname, udata in st.session_state.users.items():
                    if str(udata.get("mobile")) == str(f_mobile).strip():
                        udata["password"] = f_new_pass
                        found = True
                if found:
                    save_local_data(USERS_FILE, st.session_state.users)
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
    
    if st.session_state.role == "admin":
        tab1, tab2, tab3, tab4 = st.tabs(["📌 Assign Multiple Tiles", "📋 Selected Displays", "⚠️ Unavailable & Clear", "⚙️ Manage Users (Admin)"])
    else:
        tab1, tab2, tab3 = st.tabs(["📌 Assign Multiple Tiles", "📋 Selected Displays", "⚠️ Unavailable & Clear"])
    
    with tab1:
        st.header(f"Assign Multiple Tiles on Same Board - {location}")
        col_s, col_b = st.columns(2)
        with col_s:
            stand_no = st.selectbox("Select Stand No (1 - 50)", list(range(1, 51)), key="fixed_stand")
        with col_b:
            board_no = st.selectbox("Select Board No (1 - 35)", list(range(1, 36)), key="fixed_board")
        
        company_filter = st.text_input("🔎 Filter by Company / Name").strip().lower()
        filtered_designs = design_list
        if company_filter:
            filtered_designs = [d for d in design_list if company_filter in d.lower()]
        
        chosen_design = st.selectbox("Select Tile Design to Add", filtered_designs, key="single_design_selector")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("➕ Add to Queue"):
                if chosen_design and chosen_design not in st.session_state.temp_design_queue:
                    st.session_state.temp_design_queue.append(chosen_design)
                    st.success(f"Added '{chosen_design}' to queue!")
                    st.rerun()
        with col_btn2:
            if st.button("🗑️ Clear Queue"):
                st.session_state.temp_design_queue = []
                st.info("Queue cleared.")
                st.rerun()
        
        if st.session_state.temp_design_queue:
            st.markdown("### 📋 Queued Tiles:")
            for idx, item in enumerate(st.session_state.temp_design_queue):
                st.write(f"{idx + 1}. {item}")
            
            if st.button("💾 Save All Queued Tiles"):
                added_count = 0
                for design in st.session_state.temp_design_queue:
                    exists = any(
                        str(d.get('location', '')).strip().lower() == location.strip().lower() and 
                        int(d.get('stand', 0)) == stand_no and 
                        int(d.get('board', 0)) == board_no and 
                        str(d.get('design', '')).strip() == str(design).strip()
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
                save_local_data(DISPLAYS_FILE, st.session_state.displays)
                st.session_state.temp_design_queue = []
                st.success(f"{added_count} tile(s) saved successfully!")
                st.rerun()

    with tab2:
        st.header(f"Active Displays - {location}")
        loc_displays = [d for d in st.session_state.displays if str(d.get('location', '')).strip().lower() == location.strip().lower() and str(d.get('status', 'Available')).strip().capitalize() == 'Available']
        
        if not loc_displays:
            st.info("No active displays found.")
        else:
            for i, item in enumerate(loc_displays):
                col1, col2, col3, col4 = st.columns([2, 2, 4, 2])
                col1.write(f"**Stand:** {item.get('stand')}")
                col2.write(f"**Board:** {item.get('board')}")
                col3.write(f"**Design:** {item.get('design')}")
                if col4.button("Mark Unavailable", key=f"unavail_{i}_{item.get('stand')}_{item.get('board')}"):
                    for d in st.session_state.displays:
                        if d.get('location') == location and d.get('stand') == item.get('stand') and d.get('board') == item.get('board') and d.get('design') == item.get('design'):
                            d['status'] = 'Unavailable'
                    save_local_data(DISPLAYS_FILE, st.session_state.displays)
                    st.rerun()

    with tab3:
        st.header(f"Unavailable Section - {location}")
        unavail_displays = [d for d in st.session_state.displays if str(d.get('location', '')).strip().lower() == location.strip().lower() and str(d.get('status', '')).strip().capitalize() == 'Unavailable']
        if not unavail_displays:
            st.info("No unavailable items.")
        else:
            for i, item in enumerate(unavail_displays):
                col1, col2, col3, col4 = st.columns([2, 2, 3, 2])
                col1.write(f"**Stand:** {item.get('stand')}")
                col2.write(f"**Board:** {item.get('board')}")
                col3.write(f"**Design:** {item.get('design')}")
                if col4.button("Clear Tile", key=f"clear_{i}_{item.get('stand')}_{item.get('board')}"):
                    st.session_state.displays = [d for d in st.session_state.displays if not (d.get('location') == location and d.get('stand') == item.get('stand') and d.get('board') == item.get('board') and d.get('design') == item.get('design'))]
                    save_local_data(DISPLAYS_FILE, st.session_state.displays)
                    st.rerun()

    if st.session_state.role == "admin":
        with tab4:
            st.header("⚙️ Manage Users")
            with st.form("add_user_form"):
                new_id = st.text_input("New User ID")
                new_mob = st.text_input("Mobile Number")
                new_pwd = st.text_input("Password", type="password")
                r_choice = st.selectbox("Role", ["salesman", "admin"])
                if st.form_submit_button("Create User"):
                    if new_id and new_mob and new_pwd:
                        st.session_state.users[new_id] = {"password": new_pwd, "mobile": new_mob, "role": r_choice}
                        save_local_data(USERS_FILE, st.session_state.users)
                        st.success("User created!")
                        st.rerun()
