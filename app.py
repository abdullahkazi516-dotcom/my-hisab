import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import streamlit.components.v1 as components
import json

# ১. পেজ সেটিংস ও কাস্টম ডিজাইন
st.set_page_config(page_title="ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    /* তালিকার বর্ডার ও ডিজাইন */
    .list-item {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .income-border { border-left: 8px solid #28a745; background-color: #f8fff9; }
    .expense-border { border-left: 8px solid #dc3545; background-color: #fff8f8; }
    .due-border { border-left: 8px solid #ffc107; background-color: #fffdf5; }
    .dena-border { border-left: 8px solid #fd7e14; background-color: #fff9f5; }
    .powna-border { border-left: 8px solid #17a2b8; background-color: #f5fcff; }
    
    .item-text { font-size: 16px; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"
FIXED_USER = "Kazi_Mamun"
DEFAULT_PW = "427054"

# ২. ডাটা ফেচিং
@st.cache_data(ttl=10)
def get_data():
    try:
        res = requests.get(API_URL, timeout=5)
        df = pd.DataFrame(res.json())
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])

# ৩. লগইন হ্যান্ডলিং (ফিক্সড)
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
    # ড্যাশবোর্ড ও এন্ট্রি
    st.title("💰 আমার ডিজিটাল ক্যাশ বুক")
    df = get_data()

    # ক্যাশ জমা ড্যাশবোর্ড
    if not df.empty:
        ti = df[df['Category'] == 'আয়']['Amount'].sum()
        te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
        st.success(f"💵 বর্তমান নগদ জমা: {ti - te} টাকা")

    # এন্ট্রি ফর্ম (আপনার দেওয়া ডিজাইনের মতো)
    with st.expander("➕ নতুন লেনদেন যোগ করুন"):
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("তারিখ", datetime.now())
            cat = st.selectbox("ধরণ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
            desc = st.text_input("বিবরণ")
            amt = st.number_input("টাকা", min_value=0)
            if st.form_submit_button("Submit"):
                if desc:
                    new_data = {"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}
                    requests.post(API_URL, json={"data": [new_data]})
                    st.cache_data.clear()
                    st.rerun()

    # ৪. বিভাগ অনুযায়ী রঙিন বর্ডার যুক্ত তালিকা
    st.subheader("📊 হিসাবের তালিকা (বিভাগ অনুযায়ী)")
    tabs = st.tabs(["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
    
    cat_map = {
        "আয়": ("income-border", tabs[0]),
        "ব্যয়": ("expense-border", tabs[1]),
        "বকেয়া": ("due-border", tabs[2]),
        "দেনা": ("dena-border", tabs[3]),
        "পাওনা": ("powna-border", tabs[4])
    }

    for category, (css_class, tab_obj) in cat_map.items():
        with tab_obj:
            filtered_df = df[df['Category'] == category]
            if not filtered_df.empty:
                for idx, row in filtered_df.iloc[::-1].iterrows():
                    # বর্ডার ও কালার কোডেড বক্স
                    st.markdown(f"""
                        <div class="list-item {css_class}">
                            <div class="item-text">
                                📅 {row['Date']} | {row['Description']} | 💰 {row['Amount']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"এই মুহূর্তে কোনো {category} রেকর্ড নেই।")

    if st.sidebar.button("লগআউট"):
        st.session_state["logged_in"] = False
        st.rerun()
