import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ১. পেজ সেটিংস ও ডিজাইন (Custom CSS)
st.set_page_config(page_title="ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    /* ফর্মের ব্যাকগ্রাউন্ড ডিজাইন */
    .stForm {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #ddd;
    }
    /* রঙিন বর্ডার কার্ড ডিজাইন */
    .record-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: white;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .income-b { border-left: 8px solid #28a745; }
    .expense-b { border-left: 8px solid #dc3545; }
    .due-b { border-left: 8px solid #ffc107; }
    .dena-b { border-left: 8px solid #fd7e14; }
    .powna-b { border-left: 8px solid #17a2b8; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"
DEFAULT_PW = "427054"

# ২. ডাটা ফেচিং
@st.cache_data(ttl=5)
def get_data():
    try:
        res = requests.get(API_URL, timeout=5)
        df = pd.DataFrame(res.json())
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])

# ৩. লগইন চেক
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 লগইন করুন")
    pw = st.text_input("পাসওয়ার্ড দিন", type="password")
    if st.button("প্রবেশ করুন"):
        if pw == DEFAULT_PW:
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!") #
else:
    st.title("💰 আমার ডিজিটাল ক্যাশ বুক")
    df = get_data()

    # ড্যাশবোর্ড সামারি
    if not df.empty:
        ti = df[df['Category'] == 'আয়']['Amount'].sum()
        te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
        st.info(f"💵 বর্তমান নগদ জমা: {ti - te} টাকা")

    # ৪. ডাটা এন্ট্রি ফর্ম (সবসময় খোলা থাকবে)
    st.subheader("➕ নতুন লেনদেন যোগ করুন")
    with st.form("main_form", clear_on_submit=True):
        date = st.date_input("তারিখ", datetime.now())
        cat = st.selectbox("ধরণ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
        desc = st.text_input("বিবরণ")
        amt = st.number_input("টাকা", min_value=0)
        
        if st.form_submit_button("Submit"):
            if desc:
                new_entry = {"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}
                requests.post(API_URL, json={"data": [new_entry]})
                st.cache_data.clear()
                st.success("লেনদেনটি সফলভাবে সেভ হয়েছে!")
                st.rerun()

    # ৫. বিভাগ অনুযায়ী রঙিন বর্ডার তালিকা (Tabs)
    st.subheader("📊 হিসাবের তালিকা (বিভাগ অনুযায়ী)")
    tabs = st.tabs(["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
    
    config = {
        "আয়": ("income-b", tabs[0]),
        "ব্যয়": ("expense-b", tabs[1]),
        "বকেয়া": ("due-b", tabs[2]),
        "দেনা": ("dena-b", tabs[3]),
        "পাওনা": ("powna-b", tabs[4])
    }

    for category, (border_class, tab_obj) in config.items():
        with tab_obj:
            filtered = df[df['Category'] == category]
            if not filtered.empty:
                for _, row in filtered.iloc[::-1].iterrows():
                    st.markdown(f"""
                        <div class="record-card {border_class}">
                            <b>📅 {row['Date']}</b> | {row['Description']} | <b>💰 {row['Amount']} টাকা</b>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.write(f"এই মুহূর্তে কোনো {category} রেকর্ড নেই।")

    if st.sidebar.button("লগআউট"):
        st.session_state["logged_in"] = False
        st.rerun()
