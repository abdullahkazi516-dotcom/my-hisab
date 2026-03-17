import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও ডিজাইন (CSS)
st.set_page_config(page_title="স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .total-summary { background-color: #f1f3f4; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 18px; color: #1967d2; margin: 10px 0; }
    .call-btn {
        background-color: #00c853; color: white !important; padding: 5px 10px;
        text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px;
        display: inline-block; text-align: center; border: 1px solid #00a040;
    }
    .call-btn:hover { background-color: #00e676; color: white !important; }
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
        df = pd.DataFrame(res.json())
        if not df.empty:
            return df.astype(str) # সব ডাটাকে টেক্সট হিসেবে পড়া যাতে নম্বর ঠিক থাকে
        return df
    except:
        return pd.DataFrame()

# ৪. ক্যাশ ব্যালেন্স হিসাব
df_main = get_data("Sheet1")
current_balance = 0
if not df_main.empty:
    amounts = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    income = amounts[df_main['Category'] == 'আয়'].sum()
    expense = amounts[df_main['Category'] == 'ব্যয়'].sum()
    current_balance = income - expense

st.subheader("🏦 ক্যাশ স্ট্যাটাস")
if "show_balance" not in st.session_state: st.session_state.show_balance = False
balance_label = f"ব্যালেন্স: {current_balance} ৳" if st.session_state.show_balance else "ব্যালেন্স দেখতে ক্লিক করুন"
if st.button(balance_label, use_container_width=True, type="primary"):
    st.session_state.show_balance = not st.session_state.show_balance
    st.rerun()

# ৫. ট্যাব সিস্টেম
tab_hishab, tab_plan, tab_exp, tab_phone = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

# --- ট্যাব ১: লেনদেন --- (পূর্বের কোড অনুযায়ী)
with tab_hishab:
    st.subheader("📝 লেনদেন এন্ট্রি")
    edit_mode = st.session_state.get('edit_data')
    with st.form("hishab_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        date = c1.date_input("তারিখ", datetime.now() if not edit_mode else pd.to_datetime(edit_mode['Date']))
        cat = c2.selectbox("বিভাগ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"], index=0 if not edit_mode else ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"].index(edit_mode['Category']))
        desc = st.text_input("বিবরণ", value="" if not edit_mode else edit_mode['Description'])
        amt = st.number_input("পরিমাণ", min_value=0, value=0 if not edit_mode else int(float(edit_mode['Amount'])))
        if st.form_submit_button("সেভ"):
            if desc:
                if edit_mode: requests.delete(f"{API_URL}/Description/{edit_mode['Description']}?sheet=Sheet1")
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(date), "Description": desc, "Category": cat, "Amount": str(amt)}]})
                st.session_state.edit_data = None
                st.cache_data.clear(); st.rerun()

# --- ট্যাব ২: পরিকল্পনা ও ৩: অভিজ্ঞতা (সংক্ষিপ্ত আকারে রাখা হয়েছে) ---
with tab_plan:
    st.subheader("🗓️ পরিকল্পনা")
    p_df = get_data("Plans")
    if not p_df.empty: st.dataframe(p_df[['Date', 'Task']].iloc[::-1], use_container_width=True, hide_index=True)

with tab_exp:
    st.subheader("🌟 ডায়েরি/অভিজ্ঞতা")
    e_df = get_data("Experiences")
    if not e_df.empty: st.dataframe(e_df[['Date', 'Good', 'Bad']].iloc[::-1], use_container_width=True, hide_index=True)

# --- ট্যাব ৪: ফোনবুক (আপনার চাহিদা মতো টেবিল সামারি আকারে) ---
with tab_phone:
    st.subheader("📱 ফোনবুক সামারি")
    
    # এডিট করার জন্য ডাটা চেক
    edit_ph_mode = st.session_state.get('edit_phone_data')
    
    # নম্বর সেভ করার ফর্ম
    with st.form("phone_form", clear_on_submit=True):
        col_n, col_m, col_note = st.columns(3)
        p_name = col_n.text_input("নাম", value="" if not edit_ph_mode else str(edit_ph_mode['Name']))
        p_mobile = col_m.text_input("মোবাইল নম্বর", value="" if not edit_ph_mode else str(edit_ph_mode['Mobile']))
        p_note = col_note.text_input("পরিচয়/নোট", value="" if not edit_ph_mode else str(edit_ph_mode['Note']))
        
        if st.form_submit_button("নম্বরটি সেভ করুন"):
            if p_name and p_mobile:
                if edit_ph_mode: requests.delete(f"{API_URL}/id/{edit_ph_mode['id']}?sheet=Phonebook")
                ph_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Phonebook", json={"data": [{"id": ph_id, "Name": str(p_name), "Mobile": str(p_mobile).strip(), "Note": str(p_note)}]})
                st.session_state.edit_phone_data = None
                st.cache_data.clear(); st.success("সংরক্ষিত!"); st.rerun()

    st.divider()
    
    # টেবিল সামারি প্রদর্শন
    ph_df = get_data("Phonebook")
    if not ph_df.empty:
        # টেবিলের হেডার (শিরোনাম)
        h1, h2, h3, h4 = st.columns([2, 2, 2, 3])
        h1.write("**নাম**")
        h2.write("**মোবাইল**")
        h3.write("**নোট**")
        h4.write("**অ্যাকশন**")
        st.write("---")
        
        # ডাটাগুলো লুপ করে টেবিলে দেখানো
        for i, row in ph_df.iloc[::-1].iterrows():
            r1, r2, r3, r4 = st.columns([2, 2, 2, 3])
            r1.write(row['Name'])
            r2.write(row['Mobile'])
            r3.write(row['Note'])
            
            # অ্যাকশন কলামে কল, এডিট, ডিলিট বাটন
            with r4:
                btn_col1, btn_col2, btn_col3 = st.columns([1.2, 0.8, 0.8])
                # কল বাটন
                btn_col1.markdown(f'<a href="tel:{row["Mobile"]}" class="call-btn">📞 কল দিন</a>', unsafe_allow_html=True)
                # এডিট বাটন
                if btn_col2.button("📝", key=f"p_ed_{i}"):
                    st.session_state.edit_phone_data = row
                    st.rerun()
                # ডিলিট বাটন
                if btn_col3.button("🗑️", key=f"p_del_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Phonebook")
                    st.cache_data.clear(); st.rerun()
            st.write("-" * 5)
    else:
        st.info("ফোনবুকে কোনো নম্বর নেই।")

# লগআউট
st.sidebar.button("লগআউট", on_click=lambda: st.session_state.update({"logged_in": False}))
