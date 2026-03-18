import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটআপ ও স্টাইল
st.set_page_config(page_title="হিসাব খাতা", layout="wide")

st.markdown("""
    <style>
    .balance-card { background: linear-gradient(135deg, #1e1e1e, #2b2b2b); padding: 20px; border-radius: 15px; border: 2px solid #00c853; text-align: center; margin-bottom: 20px; }
    .table-header { background-color: #0d47a1; color: white; padding: 10px; border-radius: 5px; margin-top: 20px; text-align: center; font-size: 18px; font-weight: bold; }
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 5px; border: 1px solid #444; background-color: #1a1a1a; }
    .custom-table td, .custom-table th { padding: 10px; border: 1px solid #444; text-align: left; }
    .t-date { color: #ffd600; font-weight: bold; }
    .t-amt { color: #00c853; font-weight: bold; }
    .total-box { padding: 10px; background-color: #263238; color: #00c853; font-weight: bold; border: 1px solid #444; border-top: none; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. ডাটা লোড ফাংশন
def load_data(sheet):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet}", timeout=15)
        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            return df.dropna(how='all').astype(str)
    except: pass
    return pd.DataFrame()

df_main = load_data("Sheet1")

# ৩. ব্যালেন্স হিসাব
st.markdown('<div class="balance-card">', unsafe_allow_html=True)
total_bal = 0
if not df_main.empty and 'Category' in df_main.columns:
    df_main['Amount'] = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    inc = df_main[df_main['Category'] == "আয়"]['Amount'].sum()
    exp = df_main[df_main['Category'] == "ব্যয়"]['Amount'].sum()
    total_bal = inc - exp

if "hide_bal" not in st.session_state: st.session_state["hide_bal"] = True
val = "••••••" if st.session_state["hide_bal"] else f"{total_bal} ৳"
st.markdown(f"## 💰 বর্তমান ব্যালেন্স: {val}")
if st.button("👁️ ব্যালেন্স দেখুন/লুকান"):
    st.session_state["hide_bal"] = not st.session_state["hide_bal"]
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ৪. ডাটা এন্ট্রি ফর্ম
cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
with st.form("entry_form", clear_on_submit=True):
    st.subheader("📝 নতুন হিসাব যোগ করুন")
    c1, c2 = st.columns(2)
    in_date = c1.date_input("তারিখ", datetime.now())
    in_cat = c2.selectbox("ধরণ", cats)
    in_desc = st.text_input("বিবরণ")
    in_amt = st.number_input("টাকা", min_value=0)
    if st.form_submit_button("সেভ করুন"):
        if in_desc and in_amt > 0:
            requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(in_date), "Description": in_desc, "Category": in_cat, "Amount": str(in_amt)}]})
            st.success("সেভ হয়েছে!")
            st.rerun()

# ৫. নিচে ৫টি আলাদা আলাদা টেবিল (আয়, ব্যয়, বকেয়া, দেনা, পাওনা)
st.divider()
st.subheader("📊 বিস্তারিত হিসাব তালিকা")

if not df_main.empty and 'Category' in df_main.columns:
    for cat in cats:
        sub_df = df_main[df_main['Category'] == cat]
        
        # প্রতিটি ক্যাটাগরির জন্য আলাদা হেডার
        st.markdown(f'<div class="table-header">{cat} তালিকা</div>', unsafe_allow_html=True)
        
        if not sub_df.empty:
            # কাস্টম ডিজাইন করা টেবিল
            html = '<table class="custom-table"><tr><th>তারিখ</th><th>বিবরণ</th><th>টাকা</th></tr>'
            for _, row in sub_df.iloc[::-1].iterrows(): # নতুনগুলো উপরে দেখাবে
                html += f'''
                <tr>
                    <td class="t-date">{row['Date']}</td>
                    <td>{row['Description']}</td>
                    <td class="t-amt">{row['Amount']} ৳</td>
                </tr>
                '''
            html += '</table>'
            st.markdown(html, unsafe_allow_html=True)
            
            # সাব-টোটাল বক্স
            cat_total = pd.to_numeric(sub_df['Amount']).sum()
            st.markdown(f'<div class="total-box">মোট {cat}: {cat_total} ৳</div>', unsafe_allow_html=True)
        else:
            st.info(f"এখনো কোনো {cat} এন্ট্রি করা হয়নি।")
else:
    st.error("গুগল শিটে 'Category' কলামটি খুঁজে পাওয়া যাচ্ছে না।")

# ৬. অন্যান্য ট্যাব (পরিকল্পনা, অভিজ্ঞতা, ফোনবুক)
st.divider()
t_plan, t_exp, t_phone = st.tabs(["🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

with t_plan:
    df_p = load_data("Plans")
    if not df_p.empty: st.table(df_p)

with t_exp:
    df_e = load_data("Experiences")
    if not df_e.empty: st.table(df_e)

with t_phone:
    df_ph = load_data("Phonebook")
    if not df_ph.empty:
        for _, r in df_ph.iterrows():
            st.write(f"👤 {r.get('Name','')} - {r.get('Mobile','')}")
