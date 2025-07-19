import streamlit as st
import pandas as pd
from pathlib import Path
# import gspread
# from google.oauth2.service_account import Credentials

ADMIN_USER = 'ananya'
ADMIN_PASS = 'ananyayakkundirss'
DATA_FILE = Path('submissions.csv')
SHEET_NAME = 'https://docs.google.com/spreadsheets/d/1Lw9VckNhgVYAmJRsA0OgdAxYpESdIehxDNgjs8RBgJc/edit?usp=sharing'
AREAS = [
    "Akshay Park Nagar", "Vidya Nagar", "Nekar Nagar", "Akkihonda Nagar", "3000 Matha Nagar",
    "Ashok Nagar", "Keshwapur Nagar", "Unakal Nagar", "Hale Hubballi Nagar"
]

def get_gsheet():
    # Load secrets from streamlit cloud
    import json
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    gc = gspread.authorize(creds)
    sh = gc.open(SHEET_NAME)
    worksheet = sh.get_worksheet(0)
    return worksheet

def save_user_and_submissions(user_name, user_phone, user_area, entries):
    user_bold = f"**{user_name.upper()}**"
    rows = [
        [user_bold, user_phone, user_area],  # All-caps, bold
        [""]         # Empty line
        # ["EntryName", "PhoneNumber", "Area"]
    ]
    rows += [[e['EntryName'], e['PhoneNumber'], e['Area']] for e in entries]

    # Append to CSV file preserving formatting
    with open(DATA_FILE, 'a', encoding='utf-8', newline='') as f:
        for row in rows:
            f.write(",".join(str(cell) for cell in row) + "\n")


def show_admin():
    st.title("Admin Dashboard")
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE, header=None, names=['UserName', 'EntryName', 'PhoneNumber', 'Area'])
        st.dataframe(df)
        st.download_button(
            "Download all submissions",
            df.to_csv(index=False).encode('utf-8'),
            "submissions.csv",
            "text/csv"
        )
    else:
        st.info("No submissions yet.")

def main():
    st.set_page_config(page_title='Area Entry Form', layout='centered')
    mode = st.sidebar.selectbox("Choose mode", ["User Form", "Admin Login"])

    if mode == "User Form":
        st.header("Shatabdi Samparka Entry Form")

        # 1. Ask for user's name
        user_name = st.text_input("Your Name")
        user_phone = st.text_input("Your Phone Number")
        user_area = st.selectbox("Your Area", ["Akshay Park Nagar", "Vidya Nagar", "Nekar Nagar", "Akkihonda Nagar", "3000 Matha Nagar",
                                               "Ashok Nagar", "Keshwapur Nagar", "Unakal Nagar", "Hale Hubballi Nagar"])

        if user_name:
            # 2. Infinite loop of entry
            st.write("Enter name, phone and area as many times as you want. Click 'Add Entry' after each, and 'Submit All' when finished.")

            if 'entries' not in st.session_state:
                st.session_state.entries = []

            with st.form("entry_form", clear_on_submit=True):
                entry_name = st.text_input("Entry Name")
                phone = st.text_input("Phone Number")
                area = st.selectbox("Area", AREAS)
                add_entry = st.form_submit_button("Add Entry")

                if add_entry:
                    if not (entry_name and phone and area):
                        st.error("Please fill all fields before adding.")
                    elif not (phone.isdigit() and len(phone) == 10):
                        st.error("Phone number must be exactly 10 digits.")
                    else:
                        st.session_state.entries.append({
                            'EntryName': entry_name,
                            'PhoneNumber': phone,
                            'Area': area,
                        })
                        st.success(f"Added: {entry_name}, {phone}, {area}")


            if st.session_state.entries:
                st.write("Entries so far:")
                st.table(pd.DataFrame(st.session_state.entries))
                if st.button("Submit All"):
                    save_user_and_submissions(user_name, user_phone, user_area, st.session_state.entries)
                    st.success("All entries saved!")
                    st.session_state.entries = []
        else:
            st.info("Please enter your name to begin.")

    elif mode == "Admin Login":
        st.header("Admin Login")
        user = st.text_input("Username")
        passwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == ADMIN_USER and passwd == ADMIN_PASS:
                show_admin()
            else:
                st.error("Invalid credentials.")

if __name__ == "__main__":
    main()
