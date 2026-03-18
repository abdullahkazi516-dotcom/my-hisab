import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও ডিজাইন
st.set_page_config(page_title="স্মার্ট হিসাব খাতা", layout="wide")

st.markdown("""
    <style>
    .balance-card { background: linear-gradient(135deg, #1e1e1e, #2b2b2b); padding: 25px; border-radius: 15px; border: 2px solid #00c853; text-align: center; margin-bottom: 20px; }
    .header-box { background-color: #0d47a1; color: white; padding: 12px; border-radius: 8px; margin-top: 30px; text-align: center; font-weight: bold; font-size: 20px; border: 1px solid #1e88e5; }
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 5px; border: 1px solid #444; }
    .custom-table td, .custom-table th { padding: 12px; border: 1px solid #444; text-align: left; }
    .t-date { color: #ffd600; font-weight: bold; } /* তারিখ হলুদ */
    .t-amt { color: #00c853; font-weight: bold; }  /* টাকা সবুজ */
    .footer-total { padding: 12px; background-color: #263238; color: #00c853; text-align: right; font-weight: bold; border: 1px solid #444; border-top: none; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন সিস্টেম (পাসওয়ার্ড: 427054)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown('<div style="text-align:center; margin-top: 50px;"><h1>🔐 লগইন করুন</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("পাসওয়ার্ড দিন", type="password")
        if st.button("প্রবেশ করুন"):
            if password == "427054":
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("ভুল পাসওয়ার্ড! আবার চেষ্টা করুন।")
    st.stop() # লগইন না হওয়া পর্যন্ত নিচের কোড চলবে না

# ৩. ডাটা লোড ফাংশন
def load_data(sheet):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet}", timeout=15)
        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            return df.dropna(how='all').astype(str)
    except: pass
    return pd.DataFrame()

df_main = load_data("Sheet1")

# ৪. ব্যালেন্স কার্ড
st.markdown('<div class="balance-card">', unsafe_allow_html=True)
total_bal = 0
if not df_main.empty and 'Category' in df_main.columns:
    df_main['Amount'] = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    inc = df_main[df_main['Category'] == "আয়"]['Amount'].sum()
    exp = df_main[df_main['Category'] == "ব্যয়"]['Amount'].sum()
    total_bal = inc - exp

if "show_val" not in st.session_state: st.session_state["show_val"] = False
val_display = f"{total_bal} ৳" if st.session_state["show_val"] else "••••••"
st.markdown(f"## 💰 বর্তমান ব্যালেন্স: {val_display}")
if st.button("👁️ ব্যালেন্স দেখুন/লুকান"):
    st.session_state["show_val"] = not st.session_state["show_val"]; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ৫. মেইন কন্টেন্ট (আয়, ব্যয়, বকেয়া, দেনা, পাওনা)
tab1, tab2 = st.tabs(["📊 হিসাবের ঘর", "🗓️ অন্যান্য (প্ল্যান/অভিজ্ঞতা)"])

with tab1:
    # ডাটা ইনপুট ফর্ম
    cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    with st.form("main_entry", clear_on_submit=True):
        st.subheader("📝 নতুন হিসাব যোগ করুন")
        c1, c2 = st.columns(2)
        in_date = c1.date_input("তারিখ", datetime.now())
        in_cat = c2.selectbox("ধরণ", cats)
        in_desc = st.text_input("বিবরণ (Description)")
        in_amt = st.number_input("টাকা (Amount)", min_value=0)
        
        if st.form_submit_button("সেভ করুন"):
            if in_desc and in_amt > 0:
                # আপনার শিটের ক্রম: Date, Description, Category, Amount
                new_row = {"Date": str(in_date), "Description": in_desc, "Category": in_cat, "Amount": str(in_amt)}
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [new_row]})
                st.success("সফলভাবে সেভ হয়েছে!")
                st.rerun()

    st.divider()
    st.subheader("📂 ক্যাটাগরি অনুযায়ী বিস্তারিত ঘর")

    # নিচে ৫টি আলাদা আলাদা টেবিল/ঘর
    if not df_main.empty and 'Category' in df_main.columns:
        for cat in cats:
            st.markdown(f'<div class="header-box">{cat} এর ঘর</div>', unsafe_allow_html=True)
            filtered = df_main[df_main['Category'] == cat]
            
            if not filtered.empty:
                # কাস্টম টেবিল
                html = '<table class="custom-table"><tr><th>তারিখ</th><th>বিবরণ</th><th>টাকা</th></tr>'
                for _, r in filtered.iloc[::-1].iterrows():
                    html += f'<tr><td class="t-date">{r["Date"]}</td><td>{r["Description"]}</td><td class="t-amt">{r["Amount"]} ৳</td></tr>'
                st.markdown(html + '</table>', unsafe_allow_html=True)
                
                # ক্যাটাগরি অনুযায়ী মোট হিসাব
                sum_amt = pd.to_numeric(filtered['Amount']).sum()
                st.markdown(f'<div class="footer-total">মোট {cat}: {sum_amt} ৳</div>', unsafe_allow_html=True)
            else:
                st.info(f"এখনো কোনো {cat} এন্ট্রি করা হয়নি।")
    else:
        st.warning("শিটে কোনো ডাটা পাওয়া যায়নি।")

# ৬. অন্যান্য ট্যাব (প্ল্যান/অভিজ্ঞতা/ফোনবুক)
with tab2:
    p_tab, e_tab, ph_tab = st.tabs(["🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])
    
    with p_tab:
        df_p = load_data("Plans")
        if not df_p.empty: st.table(df_p)
        
    with e_tab:
        df_e = load_data("Experiences")
        if not df_e.empty: st.table(df_e)

    with ph_tab:
        df_ph = load_data("Phonebook")
        if not df_ph.empty: st.table(df_ph)
