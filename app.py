import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ ডিজাইন ও স্টাইল
st.set_page_config(page_title="আমার ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .balance-card { background: linear-gradient(135deg, #1e1e1e, #2b2b2b); padding: 25px; border-radius: 15px; border: 2px solid #00c853; text-align: center; margin-bottom: 20px; }
    .header-box { background-color: #0d47a1; color: white; padding: 12px; border-radius: 8px; margin-top: 30px; text-align: center; font-weight: bold; font-size: 18px; border: 1px solid #1e88e5; }
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 5px; border: 1px solid #444; background-color: #1a1a1a; }
    .custom-table td, .custom-table th { padding: 12px; border: 1px solid #444; text-align: left; }
    .t-date { color: #ffd600; font-weight: bold; } /* তারিখ হলুদ */
    .t-amt { color: #00c853; font-weight: bold; }  /* টাকা সবুজ */
    .footer-total { padding: 12px; background-color: #263238; color: #00c853; text-align: right; font-weight: bold; border: 1px solid #444; border-top: none; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন সিস্টেম (পাসওয়ার্ড: 427054)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown('<div style="text-align:center; margin-top: 50px;"><h1>🔐 লগইন করুন</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        password = st.text_input("পাসওয়ার্ড লিখুন", type="password")
        if st.button("প্রবেশ করুন"):
            if password == "427054":
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("ভুল পাসওয়ার্ড!")
    st.stop()

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

# ৪. ব্যালেন্স সেকশন
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
if st.button("👁️ হাইড/শো"):
    st.session_state["show_val"] = not st.session_state["show_val"]; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ৫. মেইন ট্যাব সিস্টেম
t_main, t_others = st.tabs(["📊 হিসাবের ঘরসমূহ", "🗓️ পরিকল্পনা ও অভিজ্ঞতা"])

with t_main:
    # ডাটা ইনপুট ফর্ম
    cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    with st.form("input_form", clear_on_submit=True):
        st.subheader("📝 নতুন ডাটা এন্ট্রি")
        c1, c2 = st.columns(2)
        in_date = c1.date_input("তারিখ", datetime.now())
        in_cat = c2.selectbox("ক্যাটাগরি", cats)
        in_desc = st.text_input("বিবরণ (Description)")
        in_amt = st.number_input("টাকা (Amount)", min_value=0)
        
        if st.form_submit_button("সেভ করুন"):
            if in_desc and in_amt > 0:
                # আপনার শিটের ক্রম অনুযায়ী সেভ: Date, Description, Category, Amount
                new_row = {"Date": str(in_date), "Description": in_desc, "Category": in_cat, "Amount": str(in_amt)}
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [new_row]})
                st.success("সফলভাবে সেভ হয়েছে!")
                st.rerun()

    st.divider()
    st.subheader("📂 বিস্তারিত খতিয়ান (নিচে ৫টি ঘর)")

    # নিচে ৫টি আলাদা আলাদা ঘর (আয়, ব্যয়, বকেয়া, দেনা, পাওনা)
    if not df_main.empty and 'Category' in df_main.columns:
        for cat in cats:
            # প্রতিটি খাতের জন্য আলাদা হেডার
            st.markdown(f'<div class="header-box">{cat} এর ঘর</div>', unsafe_allow_html=True)
            
            sub_df = df_main[df_main['Category'] == cat]
            if not sub_df.empty:
                # কাস্টম ডিজাইন টেবিল
                html = '<table class="custom-table"><tr><th>তারিখ</th><th>বিবরণ</th><th>টাকা</th></tr>'
                for _, row in sub_df.iloc[::-1].iterrows(): # নতুন তথ্য উপরে
                    html += f'<tr><td class="t-date">{row["Date"]}</td><td>{row["Description"]}</td><td class="t-amt">{row["Amount"]} ৳</td></tr>'
                st.markdown(html + '</table>', unsafe_allow_html=True)
                
                # যোগফল বক্স
                cat_sum = pd.to_numeric(sub_df['Amount']).sum()
                st.markdown(f'<div class="footer-total">মোট {cat}: {cat_sum} ৳</div>', unsafe_allow_html=True)
            else:
                st.info(f"এখনো কোনো {cat} এন্ট্রি করা হয়নি।")
    else:
        st.warning("শিটে কোনো ডাটা নেই। ইনপুট ফর্ম থেকে প্রথম এন্ট্রি দিন।")

# ৬. পরিকল্পনা, অভিজ্ঞতা ও ফোনবুক
with t_others:
    p_tab, e_tab, ph_tab = st.tabs(["🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])
    
    with p_tab:
        df_p = load_data("Plans")
        if not df_p.empty: st.table(df_p.iloc[::-1])
        
    with e_tab:
        df_e = load_data("Experiences")
        if not df_e.empty: st.table(df_e.iloc[::-1])

    with ph_tab:
        df_ph = load_data("Phonebook")
        if not df_ph.empty:
            for _, r in df_ph.iterrows():
                st.write(f"👤 **{r.get('Name','')}** - {r.get('Mobile','')}")
