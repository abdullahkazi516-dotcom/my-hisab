import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. ডিজাইন ও স্টাইল
st.set_page_config(page_title="স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .balance-card { background: linear-gradient(135deg, #1e1e1e, #2b2b2b); padding: 25px; border-radius: 15px; border: 2px solid #00c853; text-align: center; margin-bottom: 20px; }
    .total-summary-box { padding: 15px; border-radius: 10px; font-weight: bold; background-color: #0d47a1; color: white; margin-top: 15px; font-size: 20px; text-align: center; border: 2px solid #1e88e5; }
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #444; }
    .custom-table td { padding: 10px; border: 1px solid #444; }
    .t-date { color: #ffd600; font-weight: bold; }
    .t-desc { color: #ffffff; }
    .t-amt { color: #00c853; font-weight: bold; }
    .call-btn { background-color: #00c853; color: white !important; padding: 6px 12px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন সিস্টেম
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if not st.session_state["logged_in"]:
    st.subheader("🔐 প্রবেশ করুন")
    p = st.text_input("পাসওয়ার্ড", type="password", key="login_p")
    if st.button("লগইন"):
        if p == "427054":
            st.session_state["logged_in"] = True
            st.rerun()
    st.stop()

# ৩. নিরাপদ ডাটা লোড ফাংশন (Error Handling সহ)
def load_data(sheet):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet}", timeout=15)
        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            return df.astype(str) if not df.empty else pd.DataFrame()
    except: pass
    return pd.DataFrame()

# ৪. ডাটা ও ব্যালেন্স লোড
df_main = load_data("Sheet1")
if "hide_bal" not in st.session_state: st.session_state["hide_bal"] = True

st.markdown('<div class="balance-card">', unsafe_allow_html=True)
total_bal = 0
if not df_main.empty and 'Category' in df_main.columns:
    df_main['Amount'] = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    inc = df_main[df_main['Category'] == "আয়"]['Amount'].sum()
    exp = df_main[df_main['Category'] == "ব্যয়"]['Amount'].sum()
    total_bal = inc - exp
val = "••••••" if st.session_state["hide_bal"] else f"{total_bal} ৳"
st.markdown(f"## 💰 বর্তমান ব্যালেন্স: {val}")
if st.button("👁️ হাইড/শো"):
    st.session_state["hide_bal"] = not st.session_state["hide_bal"]; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ৫. ট্যাব সিস্টেম (লেনদেন, পরিকল্পনা, অভিজ্ঞতা, ফোনবুক)
t1, t2, t3, t4 = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

# --- লেনদেন ট্যাব ---
with t1:
    cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    if "edit_row" not in st.session_state: st.session_state.edit_row = None
    
    d_v, c_i, ds_v, am_v = datetime.now(), 0, "", 0
    if st.session_state.edit_row is not None:
        try:
            r = st.session_state.edit_row
            d_v = pd.to_datetime(r['Date']).to_pydatetime()
            ds_v, am_v = r['Description'], int(float(r['Amount']))
            if r['Category'] in cats: c_i = cats.index(r['Category'])
        except: pass

    with st.form("h_form", clear_on_submit=True):
        st.subheader("📝 এন্ট্রি / এডিট")
        c1, c2 = st.columns(2)
        in_date, in_cat = c1.date_input("তারিখ", d_v), c2.selectbox("ধরণ", cats, index=c_i)
        in_desc, in_amt = st.text_input("বিবরণ", value=ds_v), st.number_input("টাকা", min_value=0, value=am_v)
        if st.form_submit_button("সেভ করুন"):
            if in_desc:
                if st.session_state.edit_row is not None:
                    requests.delete(f"{API_URL}/Description/{st.session_state.edit_row['Description']}?sheet=Sheet1")
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(in_date), "Description": in_desc, "Category": in_cat, "Amount": str(in_amt)}]})
                st.session_state.edit_row = None; st.rerun()

    if not df_main.empty and 'Category' in df_main.columns:
        s_tabs = st.tabs(cats)
        for i, s_tab in enumerate(s_tabs):
            with s_tab:
                sub = df_main[df_main['Category'] == cats[i]]
                if not sub.empty:
                    html = '<table class="custom-table"><tr><th>তারিখ</th><th>বিবরণ</th><th>টাকা</th></tr>'
                    for _, row in sub.iloc[::-1].iterrows():
                        html += f'<tr><td class="t-date">{row["Date"]}</td><td class="t-desc">{row["Description"]}</td><td class="t-amt">{row["Amount"]} ৳</td></tr>'
                    st.markdown(html + '</table>', unsafe_allow_html=True)
                    st.markdown(f'<div class="total-summary-box">📊 মোট {cats[i]}: {sub["Amount"].sum()} ৳</div>', unsafe_allow_html=True)
                    for idx, r in sub.iterrows():
                        if st.button(f"📝 এডিট: {r['Description']}", key=f"ed_{idx}_{i}"):
                            st.session_state.edit_row = r; st.rerun()
    else:
        st.warning("Sheet1-এ 'Category' কলামটি খুঁজে পাওয়া যায়নি। দয়া করে গুগল শিট চেক করুন।")

# --- পরিকল্পনা ট্যাব ---
with t2:
    st.subheader("🗓️ পরিকল্পনা")
    df_p = load_data("Plans")
    p_text = st.text_area("নতুন প্ল্যান")
    if st.button("প্ল্যান সেভ"):
        if p_text: requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"Date": str(datetime.now().date()), "Task": p_text}]}); st.rerun()
    if not df_p.empty: st.table(df_p.iloc[::-1])

# --- অভিজ্ঞতা ট্যাব ---
with t3:
    st.subheader("🌟 অভিজ্ঞতা")
    df_e = load_data("Experiences")
    with st.form("e_form"):
        g, b = st.text_input("ভালো"), st.text_input("খারাপ")
        if st.form_submit_button("সেভ"):
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"Date": str(datetime.now().date()), "Good": g, "Bad": b}]}); st.rerun()
    if not df_e.empty: st.table(df_e.iloc[::-1])

# --- ফোনবুক ট্যাব ---
with t4:
    st.subheader("📱 ফোনবুক")
    df_ph = load_data("Phonebook")
    with st.form("ph_form"):
        n, m = st.text_input("নাম"), st.text_input("মোবাইল")
        if st.form_submit_button("নম্বর সেভ"):
            requests.post(f"{API_URL}?sheet=Phonebook", json={"data": [{"Name": n, "Mobile": f"'{m}"}]}); st.rerun()
    if not df_ph.empty:
        for _, r in df_ph.iterrows():
            col1, col2 = st.columns([3, 1])
            col1.write(f"👤 **{r['Name']}** ({r['Mobile']})")
            col2.markdown(f'<a href="tel:{r["Mobile"]}" class="call-btn">📞 কল</a>', unsafe_allow_html=True); st.divider()
