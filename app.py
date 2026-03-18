import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও কাস্টম কালার ডিজাইন (CSS)
st.set_page_config(page_title="স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .balance-card { background: linear-gradient(135deg, #1e1e1e, #2b2b2b); padding: 20px; border-radius: 15px; border: 2px solid #00c853; text-align: center; margin-bottom: 20px; }
    
    /* টোটাল হিসাবের নীল ঘর */
    .total-summary-box { 
        padding: 15px; border-radius: 10px; font-weight: bold; 
        background-color: #0d47a1; color: white; 
        margin-top: 10px; font-size: 20px; text-align: center; border: 2px solid #1e88e5;
    }

    /* কাস্টম কালারফুল টেবিল স্টাইল */
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #444; }
    .custom-table th { background-color: #333; color: white; padding: 10px; text-align: left; border: 1px solid #444; }
    .custom-table td { padding: 10px; border: 1px solid #444; }
    .t-date { color: #ffd600; font-weight: bold; } /* তারিখ হলুদ */
    .t-desc { color: #ffffff; }               /* বিবরণ সাদা */
    .t-amt { color: #00c853; font-weight: bold; }  /* টাকা সবুজ */

    .call-btn { background-color: #00c853; color: white !important; padding: 5px 10px; text-decoration: none; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন সিস্টেম
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("🔐 পাসওয়ার্ড দিয়ে লগইন করুন")
    p_in = st.text_input("পাসওয়ার্ড", type="password")
    if st.button("লগইন"):
        if p_in == "427054":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!")
    st.stop()

# ৩. ডাটা লোড
def get_safe_data(sheet):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet}", timeout=15)
        return pd.DataFrame(res.json()).astype(str) if res.status_code == 200 else pd.DataFrame()
    except: return pd.DataFrame()

# ৪. ব্যালেন্স কার্ড (হাইড/শো)
if "hide_bal" not in st.session_state: st.session_state["hide_bal"] = True
df_main = get_safe_data("Sheet1")

st.markdown('<div class="balance-card">', unsafe_allow_html=True)
if not df_main.empty:
    df_main['Amount'] = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    bal = df_main[df_main['Category'] == "আয়"]['Amount'].sum() - df_main[df_main['Category'] == "ব্যয়"]['Amount'].sum()
    val = "••••••" if st.session_state["hide_bal"] else f"{bal} ৳"
    st.markdown(f"## 💰 বর্তমান ব্যালেন্স: {val}")
    if st.button("👁️ হাইড / শো"):
        st.session_state["hide_bal"] = not st.session_state["hide_bal"]; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ৫. লেনদেন এন্ট্রি ও এডিট ফিক্স
t1, t2, t3, t4 = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

with t1:
    categories = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    if "edit_row" not in st.session_state: st.session_state.edit_row = None

    # ডিফল্ট মান (এডিট মোড চেক)
    d_v, c_i, ds_v, am_v = datetime.now(), 0, "", 0
    if st.session_state.edit_row is not None:
        row = st.session_state.edit_row
        try:
            d_v = pd.to_datetime(row['Date']).to_pydatetime()
            ds_v, am_v = row['Description'], int(float(row['Amount']))
            if row['Category'] in categories: c_i = categories.index(row['Category'])
        except: pass

    with st.form("hishab_form"):
        st.subheader("📝 নতুন এন্ট্রি / এডিট")
        c_a, c_b = st.columns(2)
        date_in = c_a.date_input("তারিখ", d_v)
        cat_in = c_b.selectbox("ধরণ", categories, index=c_i)
        desc_in = st.text_input("বিবরণ", value=ds_v)
        amt_in = st.number_input("টাকা", min_value=0, value=am_v)
        
        if st.form_submit_button("সেভ করুন"):
            if desc_in:
                if st.session_state.edit_row is not None:
                    requests.delete(f"{API_URL}/Description/{st.session_state.edit_row['Description']}?sheet=Sheet1")
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(date_in), "Description": desc_in, "Category": cat_in, "Amount": str(amt_in)}]})
                st.session_state.edit_row = None; st.rerun()

    st.divider()
    sub_tabs = st.tabs(categories)
    for i, s_tab in enumerate(sub_tabs):
        with s_tab:
            sub_df = df_main[df_main['Category'] == categories[i]]
            if not sub_df.empty:
                # কালারফুল কাস্টম টেবিল (HTML)
                html_table = f'<table class="custom-table"><tr><th>তারিখ</th><th>বিবরণ</th><th>টাকা</th></tr>'
                for _, r in sub_df.iloc[::-1].iterrows():
                    html_table += f'<tr><td class="t-date">{r["Date"]}</td><td class="t-desc">{r["Description"]}</td><td class="t-amt">{r["Amount"]} ৳</td></tr>'
                html_table += '</table>'
                st.markdown(html_table, unsafe_allow_html=True)
                
                # নীল টোটাল বক্স
                st.markdown(f'<div class="total-summary-box">📊 মোট {categories[i]}: {sub_df["Amount"].sum()} ৳</div>', unsafe_allow_html=True)
                
                with st.expander("এডিট বা ডিলিট"):
                    for idx, r in sub_df.iterrows():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        col1.write(f"{r['Date']} - {r['Description']}")
                        if col2.button("📝 এডিট", key=f"e_{idx}_{i}"):
                            st.session_state.edit_row = r; st.rerun()
                        if col3.button("🗑️", key=f"d_{idx}_{i}"):
                            requests.delete(f"{API_URL}/Description/{r['Description']}?sheet=Sheet1"); st.rerun()

# পরিকল্পনা ও অভিজ্ঞতা ট্যাব
with t2:
    st.subheader("🗓️ পরিকল্পনা")
    df_p = get_safe_data("Plans")
    p_text = st.text_area("নতুন প্ল্যান")
    if st.button("সেভ"):
        requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"Date": str(datetime.now().date()), "Task": p_text}]}); st.rerun()
    if not df_p.empty: st.table(df_p)

with t4:
    st.subheader("📱 ফোনবুক")
    df_ph = get_safe_data("Phonebook")
    if not df_ph.empty:
        for _, r in df_ph.iterrows():
            st.write(f"👤 {r['Name']} ({r['Mobile']})")
            st.markdown(f'<a href="tel:{r["Mobile"]}" class="call-btn">📞 কল</a>', unsafe_allow_html=True); st.divider()
