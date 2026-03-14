import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ১. পেজ সেটিংস ও ডিজাইন
st.set_page_config(page_title="ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    div[data-baseweb="input"] { border: 2px solid #4A90E2 !important; border-radius: 10px !important; }
    div[data-baseweb="select"] { border: 2px solid #F5A623 !important; border-radius: 10px !important; }
    .total-box {
        background-color: #f1f3f4; padding: 10px; border-radius: 5px;
        text-align: right; font-weight: bold; font-size: 18px;
        color: #333; border-top: 2px solid #ddd; margin-top: 5px;
    }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"
DEFAULT_PW = "427054"

# ২. ডাটা ফাংশন
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

def delete_row(desc):
    requests.delete(f"{API_URL}/Description/{desc}")
    st.cache_data.clear()
    st.rerun()

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
        else: st.error("ভুল পাসওয়ার্ড!")
else:
    st.title("💰 ডিজিটাল ক্যাশ বুক")
    df = get_data()

    # ৪. ব্যালেন্স হাইড/শো
    if not df.empty:
        ti = df[df['Category'] == 'আয়']['Amount'].sum()
        te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
        with st.expander("👁️ বর্তমান জমা টাকা দেখতে টাচ করুন"):
            st.success(f"### মোট জমা: {ti - te} টাকা")

    # ৫. ডাটা এন্ট্রি ফর্ম
    st.subheader("➕ নতুন লেনদেন যোগ করুন")
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date = col1.date_input("তারিখ", datetime.now())
        cat = col1.selectbox("ধরণ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
        desc = col2.text_input("বিবরণ")
        amt = col2.number_input("টাকা", min_value=0)
        if st.form_submit_button("সংরক্ষণ করুন"):
            if desc:
                new_entry = {"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}
                requests.post(API_URL, json={"data": [new_entry]})
                st.cache_data.clear()
                st.rerun()

    # ৬. টেবিল ভিউ ও এডিট/ডিলিট অপশন
    st.subheader("📊 হিসাবের তালিকা ও টোটাল")
    tabs = st.tabs(["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
    categories = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]

    for i, tab in enumerate(tabs):
        with tab:
            filtered = df[df['Category'] == categories[i]]
            if not filtered.empty:
                # টেবিল হেডার
                header_cols = st.columns([2, 3, 2, 1, 1])
                header_cols[0].write("**তারিখ**")
                header_cols[1].write("**বিবরণ**")
                header_cols[2].write("**টাকা**")
                header_cols[3].write("**অ্যাকশন**")
                st.divider()

                for _, row in filtered.iloc[::-1].iterrows():
                    cols = st.columns([2, 3, 2, 1, 1])
                    cols[0].write(row['Date'])
                    cols[1].write(row['Description'])
                    cols[2].write(f"{row['Amount']} ৳")
                    
                    # ডিলিট বাটন (এডিট অপশন হিসেবে বর্তমান ডাটা ডিলিট করে নতুন এন্ট্রি দেওয়া সহজ)
                    if cols[3].button("🗑️", key=f"del_{row['Description']}"):
                        delete_row(row['Description'])
                
                # টোটাল যোগফল
                total = filtered['Amount'].sum()
                st.markdown(f'<div class="total-box">মোট {categories[i]}: {total} টাকা</div>', unsafe_allow_html=True)
            else:
                st.info(f"এই মুহূর্তে কোনো {categories[i]} রেকর্ড নেই।")

    if st.sidebar.button("লগআউট"):
        st.session_state["logged_in"] = False
        st.rerun()
