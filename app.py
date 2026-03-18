import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটআপ ও ডিজাইন
st.set_page_config(page_title="আমার স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .balance-card { background: linear-gradient(135deg, #1e1e1e, #2b2b2b); padding: 20px; border-radius: 15px; border: 2px solid #00c853; text-align: center; margin-bottom: 20px; }
    .total-box { padding: 15px; border-radius: 10px; font-weight: bold; background-color: #0d47a1; color: white; text-align: center; border: 2px solid #1e88e5; }
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #444; }
    .custom-table td { padding: 10px; border: 1px solid #444; }
    .t-date { color: #ffd600; font-weight: bold; }
    .t-desc { color: #ffffff; }
    .t-amt { color: #00c853; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন চেক
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if not st.session_state["logged_in"]:
    st.subheader("🔐 লগইন")
    p = st.text_input("পাসওয়ার্ড", type="password", key="p_key")
    if st.button("প্রবেশ"):
        if p == "427054":
            st.session_state["logged_in"] = True
            st.rerun()
    st.stop()

# ৩. ডাটা লোড ফাংশন (নিরাপদ মোড)
def get_data(sheet):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet}", timeout=15)
        if res.status_code == 200:
            data = res.json()
            if data and isinstance(data, list):
                return pd.DataFrame(data).astype(str)
    except Exception as e:
        st.error(f"{sheet} ট্যাব থেকে ডাটা লোড করতে সমস্যা হচ্ছে।")
    return pd.DataFrame()

# ৪. ডাটা ও ব্যালেন্স লোড
df_main = get_data("Sheet1")
if "hide_bal" not in st.session_state: st.session_state["hide_bal"] = True

st.markdown('<div class="balance-card">', unsafe_allow_html=True)
total = 0
if not df_main.empty and 'Category' in df_main.columns:
    df_main['Amount'] = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    inc = df_main[df_main['Category'] == "আয়"]['Amount'].sum()
    exp = df_main[df_main['Category'] == "ব্যয়"]['Amount'].sum()
    total = inc - exp

val = "••••••" if st.session_state["hide_bal"] else f"{total} ৳"
st.markdown(f"## 💰 বর্তমান ব্যালেন্স: {val}")
if st.button("👁️ হাইড/শো"):
    st.session_state["hide_bal"] = not st.session_state["hide_bal"]
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ৫. ট্যাব সিস্টেম
t1, t2, t3, t4 = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

with t1:
    cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    if "edit_row" not in st.session_state: st.session_state.edit_row = None

    # এডিট ডাটা থাকলে বক্সে বসানো
    d_v, c_i, ds_v, am_v = datetime.now(), 0, "", 0
    if st.session_state.edit_row is not None:
        try:
            r = st.session_state.edit_row
            d_v = pd.to_datetime(r['Date']).to_pydatetime()
            ds_v, am_v = r['Description'], int(float(r['Amount']))
            if r['Category'] in cats: c_i = cats.index(r['Category'])
        except: pass

    with st.form("main_form", clear_on_submit=True):
        st.subheader("📝 এন্ট্রি / এডিট")
        c1, c2 = st.columns(2)
        in_date = c1.date_input("তারিখ", d_v)
        in_cat = c2.selectbox("ধরণ", cats, index=c_i)
        in_desc = st.text_input("বিবরণ", value=ds_v)
        in_amt = st.number_input("টাকা", min_value=0, value=am_v)
        
        if st.form_submit_button("সেভ করুন"):
            if in_desc:
                # এডিট হলে পুরনোটা ডিলিট
                if st.session_state.edit_row is not None:
                    requests.delete(f"{API_URL}/Description/{st.session_state.edit_row['Description']}?sheet=Sheet1")
                # নতুন সেভ
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(in_date), "Description": in_desc, "Category": in_cat, "Amount": str(in_amt)}]})
                st.session_state.edit_row = None
                st.rerun()

    # টেবিল দেখানো
    st.divider()
    sub_tabs = st.tabs(cats)
    for i, tab in enumerate(sub_tabs):
        with tab:
            if not df_main.empty and 'Category' in df_main.columns:
                sub = df_main[df_main['Category'] == cats[i]]
                if not sub.empty:
                    # কালারফুল টেবিল
                    html = '<table class="custom-table"><tr><th>তারিখ</th><th>বিবরণ</th><th>টাকা</th></tr>'
                    for _, r in sub.iloc[::-1].iterrows():
                        html += f'<tr><td class="t-date">{r["Date"]}</td><td class="t-desc">{r["Description"]}</td><td class="t-amt">{r["Amount"]} ৳</td></tr>'
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
                    st.markdown(f'<div class="total-box">📊 মোট {cats[i]}: {sub["Amount"].sum()} ৳</div>', unsafe_allow_html=True)
                    
                    for idx, row in sub.iterrows():
                        if st.button(f"📝 এডিট: {row['Description']}", key=f"ed_{idx}_{i}"):
                            st.session_state.edit_row = row
                            st.rerun()

# পরিকল্পনা, অভিজ্ঞতা ও ফোনবুক
with t2:
    st.subheader("🗓️ পরিকল্পনা")
    df_p = get_data("Plans")
    if not df_p.empty: st.table(df_p.iloc[::-1])

with t3:
    st.subheader("🌟 অভিজ্ঞতা")
    df_e = get_data("Experiences")
    if not df_e.empty: st.table(df_e.iloc[::-1])

with t4:
    st.subheader("📱 ফোনবুক")
    df_ph = get_data("Phonebook")
    if not df_ph.empty:
        for _, r in df_ph.iterrows():
            st.write(f"👤 {r.get('Name','')} - {r.get('Mobile','')}")
