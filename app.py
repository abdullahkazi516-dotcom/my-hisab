import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও ডিজাইন
st.set_page_config(page_title="ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    /* ইনপুট ঘরগুলোর রঙিন বর্ডার */
    div[data-baseweb="input"] { border: 2px solid #4A90E2 !important; border-radius: 10px !important; }
    div[data-baseweb="select"] { border: 2px solid #F5A623 !important; border-radius: 10px !important; }
    
    /* টোটাল বক্স ডিজাইন */
    .total-summary {
        background-color: #e8f0fe; padding: 15px; border-radius: 10px;
        text-align: right; font-weight: bold; font-size: 20px;
        color: #1967d2; border: 1px solid #4A90E2; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"
DEFAULT_PW = "427054"

# ২. ডাটা ফেচিং ফাংশন
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

# ৩. লগইন সিস্টেম
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
    st.title("💰 আমার ডিজিটাল ক্যাশ বুক")
    df = get_data()

    # ৪. ব্যালেন্স হাইড/শো অপশন
    if not df.empty:
        ti = df[df['Category'] == 'আয়']['Amount'].sum()
        te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
        with st.expander("👁️ বর্তমান জমা টাকা দেখতে টাচ করুন"):
            st.info(f"### মোট নগদ জমা: {ti - te} টাকা")

    # ৫. ডাটা এন্ট্রি ফর্ম (রঙিন ইনপুট)
    st.subheader("➕ নতুন লেনদেন যোগ করুন")
    with st.form("entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        date = c1.date_input("📅 তারিখ", datetime.now())
        cat = c1.selectbox("📂 ধরণ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
        desc = c2.text_input("📝 বিবরণ")
        amt = c2.number_input("💰 টাকা", min_value=0)
        if st.form_submit_button("সংরক্ষণ করুন"):
            if desc:
                new_data = {"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}
                requests.post(API_URL, json={"data": [new_data]})
                st.cache_data.clear()
                st.rerun()

    # ৬. বিভাগ অনুযায়ী গোছানো টেবিল ও টোটাল
    st.subheader("📊 বিভাগ অনুযায়ী লেনদেনের তালিকা")
    tabs = st.tabs(["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
    cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]

    for i, tab in enumerate(tabs):
        with tab:
            filtered = df[df['Category'] == cats[i]]
            if not filtered.empty:
                # আসল টেবিল ফরম্যাট (Dataframe)
                display_df = filtered[['Date', 'Description', 'Amount']].iloc[::-1].copy()
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # টেবিলের নিচে টোটাল
                total_val = filtered['Amount'].sum()
                st.markdown(f'<div class="total-summary">মোট {cats[i]}: {total_val} টাকা</div>', unsafe_allow_html=True)
                
                # ডিলিট করার জন্য আলাদা সেকশন (টেবিলের নিচেই ডিলিট বাটন)
                with st.expander("🗑️ লেনদেন ডিলিট করতে ক্লিক করুন"):
                    for idx, row in filtered.iterrows():
                        col1, col2 = st.columns([4, 1])
                        col1.write(f"{row['Date']} - {row['Description']} ({row['Amount']}৳)")
                        if col2.button("🗑️", key=f"del_{cats[i]}_{idx}"):
                            requests.delete(f"{API_URL}/Description/{row['Description']}")
                            st.cache_data.clear()
                            st.rerun()
            else:
                st.info(f"এই মুহূর্তে কোনো {cats[i]} রেকর্ড নেই।")

    if st.sidebar.button("লগআউট"):
        st.session_state["logged_in"] = False
        st.rerun()
