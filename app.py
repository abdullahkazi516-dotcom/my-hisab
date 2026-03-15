import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও ডিজাইন
st.set_page_config(page_title="ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    div[data-baseweb="input"] { border: 2px solid #4A90E2 !important; border-radius: 10px !important; }
    div[data-baseweb="select"] { border: 2px solid #F5A623 !important; border-radius: 10px !important; }
    .total-summary {
        background-color: #e8f0fe; padding: 15px; border-radius: 10px;
        text-align: right; font-weight: bold; font-size: 20px;
        color: #1967d2; border: 1px solid #4A90E2; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"
DEFAULT_PW = "427054"

# ২. ডাটা ফেচিং ফাংশন (উন্নত হ্যান্ডলিং)
@st.cache_data(ttl=5)
def get_data():
    try:
        res = requests.get(API_URL, timeout=5)
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            return df
        else:
            return pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])
    except:
        return pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])

# ৩. সেশন স্টেট ইনিশিয়ালাইজেশন (এরর এড়ানোর প্রধান সমাধান)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "edit_data" not in st.session_state:
    st.session_state.edit_data = None

# ৪. লগইন সিস্টেম
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

    # ব্যালেন্স সামারি (যদি ডাটা থাকে)
    if not df.empty:
        ti = df[df['Category'] == 'আয়']['Amount'].sum()
        te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
        with st.expander("👁️ বর্তমান জমা টাকা দেখতে টাচ করুন"):
            st.info(f"### মোট নগদ জমা: {ti - te} টাকা")

    # ৫. লেনদেন যোগ/এডিট সেকশন
    st.subheader("➕ লেনদেন যোগ/এডিট করুন")
    
    default_date = datetime.now()
    default_cat = "আয়"
    default_desc = ""
    default_amt = 0

    # এডিট মোড চেক
    if st.session_state.edit_data is not None:
        try:
            ed = st.session_state.edit_data
            default_date = datetime.strptime(str(ed['Date']), '%Y-%m-%d')
            default_cat = ed['Category']
            default_desc = ed['Description']
            default_amt = int(float(ed['Amount']))
            st.warning(f"আপনি এখন '{default_desc}' লেনদেনটি এডিট করছেন।")
        except:
            st.session_state.edit_data = None

    with st.form("entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        date = c1.date_input("📅 তারিখ", default_date)
        cats_list = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
        cat = c1.selectbox("📂 ধরণ", cats_list, index=cats_list.index(default_cat))
        desc = c2.text_input("📝 বিবরণ", value=default_desc)
        amt = c2.number_input("💰 টাকা", min_value=0, value=default_amt)
        
        btn_label = "হালনাগাদ করুন" if st.session_state.edit_data is not None else "সংরক্ষণ করুন"
        
        if st.form_submit_button(btn_label):
            if desc:
                # এডিট মোডে থাকলে আগের ডাটা মুছে ফেলা
                if st.session_state.edit_data is not None:
                    requests.delete(f"{API_URL}/Description/{st.session_state.edit_data['Description']}")
                
                new_entry = {"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}
                requests.post(API_URL, json={"data": [new_entry]})
                st.session_state.edit_data = None
                st.cache_data.clear()
                st.success("সফলভাবে সম্পন্ন হয়েছে!")
                st.rerun()
            else:
                st.error("বিবরণ দিন!")

    # ৬. বিভাগ অনুযায়ী ট্যাব ও টেবিল
    st.subheader("📊 বিভাগ অনুযায়ী লেনদেনের তালিকা")
    cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    tabs = st.tabs(cats)

    for i, tab in enumerate(tabs):
        with tab:
            filtered = df[df['Category'] == cats[i]] if not df.empty else pd.DataFrame()
            if not filtered.empty:
                st.dataframe(filtered[['Date', 'Description', 'Amount']].iloc[::-1], use_container_width=True, hide_index=True)
                
                total_val = filtered['Amount'].sum()
                st.markdown(f'<div class="total-summary">মোট {cats[i]}: {total_val} টাকা</div>', unsafe_allow_html=True)
                
                with st.expander("📝 এডিট বা 🗑️ ডিলিট করতে ক্লিক করুন"):
                    for idx, row in filtered.iterrows():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        col1.write(f"{row['Date']} - {row['Description']} ({row['Amount']}৳)")
                        
                        if col2.button("📝", key=f"edit_{cats[i]}_{idx}"):
                            st.session_state.edit_data = row
                            st.rerun()
                            
                        if col3.button("🗑️", key=f"del_{cats[i]}_{idx}"):
                            requests.delete(f"{API_URL}/Description/{row['Description']}")
                            st.cache_data.clear()
                            st.rerun()
            else:
                st.info(f"এই মুহূর্তে কোনো {cats[i]} রেকর্ড নেই।")

    if st.sidebar.button("লগআউট"):
        st.session_state["logged_in"] = False
        st.rerun()
