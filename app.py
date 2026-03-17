import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও ডিজাইন
st.set_page_config(page_title="আমার স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .total-summary { background-color: #f1f3f4; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 18px; color: #1967d2; margin: 10px 0; }
    .call-btn {
        background-color: #28a745;
        color: white;
        padding: 5px 15px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
        margin-top: 5px;
    }
    .call-btn:hover { background-color: #218838; color: white; }
    </style>
    """, unsafe_allow_html=True)

# API লিঙ্ক
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন সিস্টেম (পাসওয়ার্ড: 427054)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("🔐 নিরাপদ প্রবেশ")
    password = st.text_input("পাসওয়ার্ড দিন", type="password")
    if st.button("লগইন"):
        if password == "427054": 
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!")
    st.stop()

# ৩. ডাটা লোড করার ফাংশন
@st.cache_data(ttl=5)
def get_data(sheet_name="Sheet1"):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet_name}")
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

# ৪. ব্যালেন্স ক্যালকুলেশন
df_main = get_data("Sheet1")
if not df_main.empty:
    df_main['Amount'] = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    income = df_main[df_main['Category'] == 'আয়']['Amount'].sum()
    expense = df_main[df_main['Category'] == 'ব্যয়']['Amount'].sum()
    current_balance = income - expense
else:
    current_balance = 0

# ব্যালেন্স বাটন
st.subheader("🏦 ক্যাশ স্ট্যাটাস")
if "show_balance" not in st.session_state:
    st.session_state.show_balance = False

balance_label = f"ব্যালেন্স: {current_balance} ৳" if st.session_state.show_balance else "ব্যালেন্স দেখতে ক্লিক করুন"
if st.button(balance_label, use_container_width=True, type="primary"):
    st.session_state.show_balance = not st.session_state.show_balance
    st.rerun()

# ৫. ট্যাব সিস্টেম
tab_hishab, tab_plan, tab_exp, tab_phone = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

# --- ট্যাব ১: লেনদেন হিসাব ---
with tab_hishab:
    st.subheader("📝 লেনদেন এন্ট্রি")
    edit_mode = st.session_state.get('edit_data')
    with st.form("hishab_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        date = c1.date_input("তারিখ", datetime.now() if not edit_mode else pd.to_datetime(edit_mode['Date']))
        cat = c2.selectbox("বিভাগ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"], index=0 if not edit_mode else ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"].index(edit_mode['Category']))
        desc = st.text_input("বিবরণ", value="" if not edit_mode else edit_mode['Description'])
        amt = st.number_input("পরিমাণ", min_value=0, value=0 if not edit_mode else int(edit_mode['Amount']))
        if st.form_submit_button("সেভ"):
            if desc:
                if edit_mode: requests.delete(f"{API_URL}/Description/{edit_mode['Description']}?sheet=Sheet1")
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}]})
                st.session_state.edit_data = None
                st.cache_data.clear(); st.success("সেভ হয়েছে!"); st.rerun()

    cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    h_tabs = st.tabs(cats)
    for i, h_tab in enumerate(h_tabs):
        with h_tab:
            filtered = df_main[df_main['Category'] == cats[i]] if not df_main.empty else pd.DataFrame()
            if not filtered.empty:
                st.dataframe(filtered[['Date', 'Description', 'Amount']].iloc[::-1], use_container_width=True, hide_index=True)
                st.markdown(f'<div class="total-summary">মোট {cats[i]}: {pd.to_numeric(filtered["Amount"]).sum()} ৳</div>', unsafe_allow_html=True)

# --- ট্যাব ৪: 📱 ফোনবুক (কল বাটন সহ) ---
with tab_phone:
    st.subheader("📱 ফোনবুক ও সরাসরি কল")
    
    with st.form("phone_form", clear_on_submit=True):
        col_n, col_m = st.columns(2)
        name = col_n.text_input("নাম")
        mobile = col_m.text_input("মোবাইল নম্বর")
        note = st.text_input("নোট")
        if st.form_submit_button("সেভ করুন"):
            if name and mobile:
                ph_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Phonebook", json={"data": [{"id": ph_id, "Name": name, "Mobile": mobile, "Note": note}]})
                st.cache_data.clear(); st.success("সেভ হয়েছে!"); st.rerun()

    st.divider()
    ph_df = get_data("Phonebook")
    if not ph_df.empty:
        search_query = st.text_input("সার্চ করুন (নাম/নম্বর)")
        if search_query:
            ph_df = ph_df[ph_df['Name'].str.contains(search_query, case=False, na=False) | 
                          ph_df['Mobile'].str.contains(search_query, na=False)]
        
        # কার্ড ভিউ যেখানে কল বাটন থাকবে
        for i, row in ph_df.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([3, 1.5, 1])
                c1.write(f"👤 **{row['Name']}**\n\n{row['Note']}")
                c2.write(f"📞 {row['Mobile']}")
                # কল দেওয়ার বাটন (HTML লিঙ্ক ব্যবহার করে)
                c3.markdown(f'<a href="tel:{row["Mobile"]}" class="call-btn">📞 কল দিন</a>', unsafe_allow_html=True)
                
                # ডিলিট বাটন
                if st.button("🗑️", key=f"del_ph_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Phonebook")
                    st.cache_data.clear(); st.rerun()
                st.divider()
    else:
        st.info("কোনো নম্বর সেভ করা নেই।")

# বাকি ট্যাবগুলোর (Plan, Experience) সাধারণ ভিউ রাখা হয়েছে
with tab_plan:
    st.subheader("🗓️ পরিকল্পনা")
    p_df = get_data("Plans")
    if not p_df.empty: st.dataframe(p_df[['Date', 'Task']].iloc[::-1], use_container_width=True, hide_index=True)

with tab_exp:
    st.subheader("🌟 অভিজ্ঞতা")
    e_df = get_data("Experiences")
    if not e_df.empty: st.dataframe(e_df[['Date', 'Good', 'Bad']].iloc[::-1], use_container_width=True, hide_index=True)

# লগআউট
st.sidebar.button("লগআউট", on_click=lambda: st.session_state.update({"logged_in": False}))
