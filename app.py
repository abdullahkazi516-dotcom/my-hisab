import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও কালারফুল ডিজাইন (CSS)
st.set_page_config(page_title="স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .balance-card { background: linear-gradient(135deg, #1e1e1e, #2b2b2b); padding: 25px; border-radius: 15px; border: 2px solid #00c853; text-align: center; margin-bottom: 20px; }
    .total-summary-box { 
        padding: 15px; border-radius: 10px; font-weight: bold; 
        background-color: #0d47a1; color: white; 
        margin-top: 15px; font-size: 20px; text-align: center; border: 2px solid #1e88e5;
    }
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #444; }
    .custom-table th { background-color: #333; color: white; padding: 10px; text-align: left; border: 1px solid #444; }
    .custom-table td { padding: 10px; border: 1px solid #444; }
    .t-date { color: #ffd600; font-weight: bold; } /* তারিখ হলুদ */
    .t-desc { color: #ffffff; }               /* বিবরণ সাদা */
    .t-amt { color: #00c853; font-weight: bold; }  /* টাকা সবুজ */
    .call-btn { background-color: #00c853; color: white !important; padding: 6px 12px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন সিস্টেম
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown('<div style="text-align:center;"><h2>🔐 লগইন করুন</h2></div>', unsafe_allow_html=True)
    pass_input = st.text_input("পাসওয়ার্ড", type="password", key="login_key")
    if st.button("প্রবেশ করুন"):
        if pass_input == "427054":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!")
    st.stop()

# ৩. নিরাপদ ডাটা লোড ফাংশন
def get_safe_data(sheet_name):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet_name}", timeout=15)
        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            return df.astype(str) if not df.empty else pd.DataFrame()
    except: pass
    return pd.DataFrame()

# ৪. মেইন ডাটা ও ব্যালেন্স লোড
df_main = get_safe_data("Sheet1")
if "hide_bal" not in st.session_state: st.session_state["hide_bal"] = True

st.markdown('<div class="balance-card">', unsafe_allow_html=True)
current_total = 0
if not df_main.empty and 'Category' in df_main.columns:
    df_main['Amount'] = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    inc = df_main[df_main['Category'] == "আয়"]['Amount'].sum()
    exp = df_main[df_main['Category'] == "ব্যয়"]['Amount'].sum()
    current_total = inc - exp

display_val = "••••••" if st.session_state["hide_bal"] else f"{current_total} ৳"
st.markdown(f"## 💰 বর্তমান ব্যালেন্স: {display_val}")
if st.button("👁️ হাইড/শো"):
    st.session_state["hide_bal"] = not st.session_state["hide_bal"]
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ৫. ট্যাব সিস্টেম
t1, t2, t3, t4 = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

# --- লেনদেন ট্যাব (এডিট ফিক্সসহ) ---
with t1:
    cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    if "edit_row" not in st.session_state: st.session_state.edit_row = None

    # এডিট ডাটা হ্যান্ডলিং
    d_v, c_i, ds_v, am_v = datetime.now(), 0, "", 0
    if st.session_state.edit_row is not None:
        try:
            row = st.session_state.edit_row
            d_v = pd.to_datetime(row['Date']).to_pydatetime()
            ds_v, am_v = row['Description'], int(float(row['Amount']))
            if row['Category'] in cats: c_i = cats.index(row['Category'])
        except: pass

    with st.form("entry_form", clear_on_submit=True):
        st.subheader("📝 এন্ট্রি / এডিট করুন")
        col_a, col_b = st.columns(2)
        date_in = col_a.date_input("তারিখ", d_v)
        cat_in = col_b.selectbox("ধরণ", cats, index=c_i)
        desc_in = st.text_input("বিবরণ", value=ds_v)
        amt_in = st.number_input("টাকা", min_value=0, value=am_v)
        
        if st.form_submit_button("সেভ করুন"):
            if desc_in:
                if st.session_state.edit_row is not None:
                    requests.delete(f"{API_URL}/Description/{st.session_state.edit_row['Description']}?sheet=Sheet1")
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(date_in), "Description": desc_in, "Category": cat_in, "Amount": str(amt_in)}]})
                st.session_state.edit_row = None
                st.rerun()

    st.divider()
    sub_tabs = st.tabs(cats)
    for i, s_tab in enumerate(sub_tabs):
        with s_tab:
            if not df_main.empty and 'Category' in df_main.columns:
                sub_df = df_main[df_main['Category'] == cats[i]]
                if not sub_df.empty:
                    # কালারফুল টেবিল
                    html_table = f'<table class="custom-table"><tr><th>তারিখ</th><th>বিবরণ</th><th>টাকা</th></tr>'
                    for _, r in sub_df.iloc[::-1].iterrows():
                        html_table += f'<tr><td class="t-date">{r["Date"]}</td><td class="t-desc">{r["Description"]}</td><td class="t-amt">{r["Amount"]} ৳</td></tr>'
                    html_table += '</table>'
                    st.markdown(html_table, unsafe_allow_html=True)
                    
                    # নীল টোটাল বক্স
                    st.markdown(f'<div class="total-summary-box">📊 মোট {cats[i]}: {sub_df["Amount"].sum()} ৳</div>', unsafe_allow_html=True)
                    
                    # এডিট বাটন
                    with st.expander("এডিট/ডিলিট"):
                        for idx, r in sub_df.iterrows():
                            c1, c2, c3 = st.columns([3, 1, 1])
                            c1.write(f"{r['Date']} - {r['Description']}")
                            if c2.button("📝", key=f"edit_{idx}_{i}"):
                                st.session_state.edit_row = r
                                st.rerun()
                            if c3.button("🗑️", key=f"del_{idx}_{i}"):
                                requests.delete(f"{API_URL}/Description/{r['Description']}?sheet=Sheet1")
                                st.rerun()

# --- পরিকল্পনা ট্যাব ---
with t2:
    st.subheader("🗓️ আজকের পরিকল্পনা")
    df_p = get_safe_data("Plans")
    p_input = st.text_area("নতুন প্ল্যান লিখুন", key="p_in")
    if st.button("প্ল্যান সেভ করুন"):
        if p_input:
            requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"Date": str(datetime.now().date()), "Task": p_input}]})
            st.rerun()
    if not df_p.empty:
        st.table(df_p.iloc[::-1])

# --- অভিজ্ঞতা ট্যাব ---
with t3:
    st.subheader("🌟 অভিজ্ঞতা ডায়েরি")
    df_e = get_safe_data("Experiences")
    with st.form("exp_form"):
        good = st.text_input("ভালো কি হলো?")
        bad = st.text_input("খারাপ কি হলো?")
        if st.form_submit_button("অভিজ্ঞতা সেভ"):
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"Date": str(datetime.now().date()), "Good": good, "Bad": bad}]})
            st.rerun()
    if not df_e.empty:
        st.table(df_e.iloc[::-1])

# --- ফোনবুক ট্যাব ---
with t4:
    st.subheader("📱 ফোনবুক / কন্টাক্ট")
    df_ph = get_safe_data("Phonebook")
    with st.form("ph_form"):
        name = st.text_input("নাম")
        mobile = st.text_input("মোবাইল নম্বর")
        if st.form_submit_button("নম্বর সেভ করুন"):
            if name and mobile:
                requests.post(f"{API_URL}?sheet=Phonebook", json={"data": [{"Name": name, "Mobile": str(mobile)}]})
                st.rerun()
    st.divider()
    if not df_ph.empty:
        for idx, r in df_ph.iterrows():
            col1, col2 = st.columns([3, 1])
            col1.write(f"👤 **{r['Name']}** ({r['Mobile']})")
            col2.markdown(f'<a href="tel:{r["Mobile"]}" class="call-btn">📞 কল দিন</a>', unsafe_allow_html=True)
            st.write("---")
