import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ১. পেজ সেটিংস ও রঙিন ডিজাইনের CSS
st.set_page_config(page_title="ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    /* ইনপুট ফিল্ডের রঙিন বর্ডার */
    div[data-baseweb="input"] { border: 2px solid #4A90E2 !important; border-radius: 10px !important; }
    div[data-baseweb="select"] { border: 2px solid #F5A623 !important; border-radius: 10px !important; }
    
    /* লেবেল কালার */
    label { color: #2C3E50 !important; font-weight: bold !important; font-size: 16px !important; }

    /* টেবিল স্টাইল */
    .stTable { border-radius: 10px; overflow: hidden; }
    
    /* টোটাল রো হাইলাইট */
    .total-box {
        background-color: #f1f3f4;
        padding: 10px;
        border-radius: 5px;
        text-align: right;
        font-weight: bold;
        font-size: 18px;
        color: #333;
        border-top: 2px solid #ddd;
        margin-top: -15px;
    }
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
            st.error("ভুল পাসওয়ার্ড!")
else:
    st.title("💰 আমার ডিজিটাল ক্যাশ বুক")
    df = get_data()

    # ৪. ব্যালেন্স হাইড/শো অপশন
    if not df.empty:
        ti = df[df['Category'] == 'আয়']['Amount'].sum()
        te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
        balance = ti - te
        
        with st.expander("👁️ বর্তমান জমা টাকা দেখতে টাচ করুন"):
            st.markdown(f"<h2 style='text-align:center; color:#28a745;'>💵 মোট জমা: {balance} টাকা</h2>", unsafe_allow_html=True)

    # ৫. রঙিন ডাটা এন্ট্রি ফর্ম
    st.subheader("➕ নতুন লেনদেন যোগ করুন")
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<p style='color:#4A90E2; margin-bottom:0;'>📅 তারিখ</p>", unsafe_allow_html=True)
            date = st.date_input("", datetime.now())
            st.markdown("<p style='color:#F5A623; margin-bottom:0;'>📂 ধরণ</p>", unsafe_allow_html=True)
            cat = st.selectbox("", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
        with c2:
            st.markdown("<p style='color:#4A90E2; margin-bottom:0;'>📝 বিবরণ</p>", unsafe_allow_html=True)
            desc = st.text_input("", placeholder="যেমন: দোকানের বাকি")
            st.markdown("<p style='color:#28a745; margin-bottom:0;'>💰 টাকা</p>", unsafe_allow_html=True)
            amt = st.number_input("", min_value=0)
        
        if st.form_submit_button("Submit"):
            if desc:
                new_entry = {"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}
                requests.post(API_URL, json={"data": [new_entry]})
                st.cache_data.clear()
                st.success("সেভ হয়েছে!")
                st.rerun()

    # ৬. বিভাগ অনুযায়ী টেবিল এবং টোটাল যোগফল
    st.subheader("📊 হিসাবের তালিকা (বিভাগ অনুযায়ী)")
    tabs = st.tabs(["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
    categories = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]

    for i, tab in enumerate(tabs):
        with tab:
            filtered = df[df['Category'] == categories[i]]
            if not filtered.empty:
                # টেবিল আকারে প্রদর্শন
                display_df = filtered[['Date', 'Description', 'Amount']].iloc[::-1].copy()
                st.table(display_df)
                
                # টোটাল যোগফল দেখানো
                total_amt = filtered['Amount'].sum()
                st.markdown(f'<div class="total-box">মোট {categories[i]}: {total_amt} টাকা</div>', unsafe_allow_html=True)
            else:
                st.info(f"এই মুহূর্তে কোনো {categories[i]} রেকর্ড নেই।")

    if st.sidebar.button("লগআউট"):
        st.session_state["logged_in"] = False
        st.rerun()
