import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটআপ ও কালারফুল ডিজাইন (CSS)
st.set_page_config(page_title="স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    /* মেইন ব্যালেন্স কার্ড */
    .balance-card { background: linear-gradient(135deg, #1e1e1e, #2b2b2b); padding: 25px; border-radius: 15px; border: 2px solid #00c853; text-align: center; margin-bottom: 20px; }
    
    /* টেবিল হেডার কালার */
    .stDataFrame div[data-testid="stTable"] { border: 1px solid #444; }
    
    /* টোটাল হিসাবের নীল ঘর */
    .total-summary-box { 
        padding: 15px; border-radius: 10px; font-weight: bold; 
        background-color: #0d47a1; color: white; 
        margin-top: 15px; font-size: 20px; text-align: center; border: 2px solid #1e88e5;
    }

    /* ক্যাটাগরি অনুযায়ী রঙিন স্টাইল */
    .date-col { color: #ffd600; font-weight: bold; }
    .desc-col { color: #ffffff; }
    .amt-col { color: #00c853; font-weight: bold; }
    
    .call-btn { background-color: #00c853; color: white !important; padding: 6px 12px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন সিস্টেম
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("🔐 পাসওয়ার্ড দিয়ে প্রবেশ করুন")
    pass_input = st.text_input("পাসওয়ার্ড", type="password", key="login_pass")
    if st.button("লগইন"):
        if pass_input == "427054":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!")
    st.stop()

# ৩. ডাটা লোড ফাংশন
def get_data(sheet):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet}", timeout=15)
        return pd.DataFrame(res.json()).astype(str) if res.status_code == 200 else pd.DataFrame()
    except: return pd.DataFrame()

# ৪. ব্যালেন্স হাইড/শো লজিক
if "hide_bal" not in st.session_state:
    st.session_state["hide_bal"] = True

df_main = get_data("Sheet1")

st.markdown('<div class="balance-card">', unsafe_allow_html=True)
if not df_main.empty:
    df_main['Amount'] = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    inc = df_main[df_main['Category'] == "আয়"]['Amount'].sum()
    exp = df_main[df_main['Category'] == "ব্যয়"]['Amount'].sum()
    curr_bal = inc - exp
    
    c1, c2 = st.columns([4, 1])
    with c1:
        val = "••••••" if st.session_state["hide_bal"] else f"{curr_bal} ৳"
        st.markdown(f"## 💰 বর্তমান ব্যালেন্স: {val}")
    with c2:
        if st.button("👁️" if st.session_state["hide_bal"] else "🕶️"):
            st.session_state["hide_bal"] = not st.session_state["hide_bal"]
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ৫. ট্যাব সিস্টেম
t1, t2, t3, t4 = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

# --- লেনদেন (এডিট ও কালার ফিক্স) ---
with t1:
    categories = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    
    # এডিট সেশন হ্যান্ডলিং
    if "edit_data" not in st.session_state:
        st.session_state.edit_data = None

    # ডিফল্ট মান
    d_v, c_i, ds_v, am_v = datetime.now(), 0, "", 0

    if st.session_state.edit_data is not None:
        row = st.session_state.edit_data
        try:
            d_v = pd.to_datetime(row['Date']).to_pydatetime()
            ds_v, am_v = row['Description'], int(float(row['Amount']))
            if row['Category'] in categories: c_i = categories.index(row['Category'])
        except: pass

    with st.form("main_form", clear_on_submit=True):
        st.subheader("📝 নতুন এন্ট্রি / এডিট")
        col_a, col_b = st.columns(2)
        date_in = col_a.date_input("তারিখ", d_v)
        cat_in = col_b.selectbox("ধরণ", categories, index=c_i)
        desc_in = st.text_input("বিবরণ", value=ds_v)
        amt_in = st.number_input("টাকার পরিমাণ", min_value=0, value=am_v)
        
        if st.form_submit_button("ডেটা সেভ করুন"):
            if desc_in:
                # এডিট মোডে থাকলে পুরনোটা ডিলিট করা (ID ভিত্তিক)
                if st.session_state.edit_data is not None:
                    requests.delete(f"{API_URL}/Description/{st.session_state.edit_data['Description']}?sheet=Sheet1")
                
                # নতুন ডাটা পাঠানো
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(date_in), "Description": desc_in, "Category": cat_in, "Amount": str(amt_in)}]})
                st.session_state.edit_data = None
                st.rerun()

    st.divider()
    
    # টেবিল প্রদর্শন ও রঙিন টোটাল
    sub_tabs = st.tabs(categories)
    for i, s_tab in enumerate(sub_tabs):
        with s_tab:
            sub_df = df_main[df_main['Category'] == categories[i]]
            if not sub_df.empty:
                # রঙিন টেবিল কলাম
                st.dataframe(sub_df[['Date', 'Description', 'Amount']].iloc[::-1], use_container_width=True, hide_index=True)
                
                # গাঢ় নীল কালারের টোটাল বক্স
                total_val = sub_df['Amount'].sum()
                st.markdown(f'<div class="total-summary-box">📊 মোট {categories[i]}: {total_val} ৳</div>', unsafe_allow_html=True)
                
                with st.expander("এডিট বা ডিলিট অপশন"):
                    for idx, r in sub_df.iterrows():
                        c1, c2, c3 = st.columns([3, 1, 1])
                        c1.write(f"📅 {r['Date']} | 📝 {r['Description']}")
                        if c2.button("📝 এডিট", key=f"ed_{idx}_{i}"):
                            st.session_state.edit_data = r
                            st.rerun()
                        if c3.button("🗑️", key=f"del_{idx}_{i}"):
                            requests.delete(f"{API_URL}/Description/{r['Description']}?sheet=Sheet1")
                            st.rerun()

# --- বাকি ট্যাবগুলো ফিক্স ---
with t2:
    st.subheader("🗓️ পরিকল্পনা")
    df_p = get_data("Plans")
    p_text = st.text_area("আপনার প্ল্যান লিখুন", key="plan_in")
    if st.button("প্ল্যান সেভ"):
        if p_text:
            requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"id": str(datetime.now().timestamp()), "Date": str(datetime.now().date()), "Task": p_text}]})
            st.rerun()
    if not df_p.empty: st.table(df_p[['Date', 'Task']].iloc[::-1])

with t3:
    st.subheader("🌟 অভিজ্ঞতা")
    df_e = get_data("Experiences")
    with st.form("exp_f"):
        g, b = st.text_input("ভালো"), st.text_input("খারাপ")
        if st.form_submit_button("সেভ"):
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"Date": str(datetime.now().date()), "Good": g, "Bad": b}]})
            st.rerun()
    if not df_e.empty: st.table(df_e.iloc[::-1])

with t4:
    st.subheader("📱 ফোনবুক")
    df_ph = get_data("Phonebook")
    if not df_ph.empty:
        for i, r in df_ph.iterrows():
            st.write(f"👤 {r['Name']} - {r['Mobile']}")
            st.markdown(f'<a href="tel:{r["Mobile"]}" class="call-btn">📞 কল করুন</a>', unsafe_allow_html=True)
            st.divider()
