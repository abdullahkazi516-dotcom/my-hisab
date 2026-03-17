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

# ৩. ডাটা লোড ফাংশন ও মোবাইল নম্বর ঠিক করা
@st.cache_data(ttl=5)
def get_data(sheet_name="Sheet1"):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet_name}")
        df = pd.DataFrame(res.json())
        if not df.empty:
            df = df.astype(str)
            # যদি কলামে 'Mobile' থাকে, তবে শুরুতে '0' আছে কিনা চেক করে ঠিক করা
            if 'Mobile' in df.columns:
                def fix_mobile(num):
                    num = str(num).strip()
                    if num.startswith('1') and len(num) == 10:
                        return '0' + num
                    return num
                df['Mobile'] = df['Mobile'].apply(fix_mobile)
            return df
        return df
    except:
        return pd.DataFrame()

# ৪. ব্যালেন্স ক্যালকুলেশন
df_main = get_data("Sheet1")
current_balance = 0
if not df_main.empty:
    amounts = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    income = amounts[df_main['Category'] == 'আয়'].sum()
    expense = amounts[df_main['Category'] == 'ব্যয়'].sum()
    current_balance = income - expense

# ৫. ড্যাশবোর্ড ট্যাবসমূহ
st.subheader("🏦 ক্যাশ স্ট্যাটাস")
if "show_balance" not in st.session_state: st.session_state.show_balance = False
balance_label = f"ব্যালেন্স: {current_balance} ৳" if st.session_state.show_balance else "ব্যালেন্স দেখতে ক্লিক করুন"
if st.button(balance_label, use_container_width=True, type="primary"):
    st.session_state.show_balance = not st.session_state.show_balance
    st.rerun()

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
        amt = st.number_input("পরিমাণ", min_value=0, value=0 if not edit_mode else int(float(edit_mode['Amount'])))
        if st.form_submit_button("সেভ"):
            if desc:
                if edit_mode: requests.delete(f"{API_URL}/Description/{edit_mode['Description']}?sheet=Sheet1")
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(date), "Description": desc, "Category": cat, "Amount": str(amt)}]})
                st.session_state.edit_data = None
                st.cache_data.clear(); st.rerun()

    cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    h_tabs = st.tabs(cats)
    for i, h_tab in enumerate(h_tabs):
        with h_tab:
            filtered = df_main[df_main['Category'] == cats[i]] if not df_main.empty else pd.DataFrame()
            if not filtered.empty:
                st.dataframe(filtered[['Date', 'Description', 'Amount']].iloc[::-1], use_container_width=True, hide_index=True)
                total_val = pd.to_numeric(filtered['Amount']).sum()
                st.markdown(f'<div class="total-summary">মোট {cats[i]}: {total_val} ৳</div>', unsafe_allow_html=True)
                with st.expander("এডিট/ডিলিট"):
                    for idx, row in filtered.iterrows():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        col1.write(f"{row['Date']} - {row['Description']}")
                        if col2.button("📝", key=f"ed_h_{idx}"): st.session_state.edit_data = row; st.rerun()
                        if col3.button("🗑️", key=f"del_h_{idx}"):
                            requests.delete(f"{API_URL}/Description/{row['Description']}?sheet=Sheet1")
                            st.cache_data.clear(); st.rerun()

# --- ট্যাব ২: পরিকল্পনা ---
with tab_plan:
    st.subheader("🗓️ পরিকল্পনা")
    with st.form("plan_form", clear_on_submit=True):
        p_date = st.date_input("তারিখ", datetime.now(), key="p_date")
        p_task = st.text_area("কি কাজ করতে চান?")
        if st.form_submit_button("প্ল্যান সেভ"):
            if p_task:
                p_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"id": p_id, "Date": str(p_date), "Task": p_task}]})
                st.cache_data.clear(); st.rerun()
    p_df = get_data("Plans")
    if not p_df.empty:
        st.dataframe(p_df[['Date', 'Task']].iloc[::-1], use_container_width=True, hide_index=True)
        with st.expander("ডিলিট"):
            for i, row in p_df.iterrows():
                c1, c2 = st.columns([5, 1])
                c1.write(f"📅 {row['Date']}: {row['Task']}")
                if c2.button("🗑️", key=f"p_del_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Plans")
                    st.cache_data.clear(); st.rerun()

# --- ট্যাব ৩: অভিজ্ঞতা ---
with tab_exp:
    st.subheader("🌟 ডায়েরি/অভিজ্ঞতা")
    edit_exp_mode = st.session_state.get('edit_exp_data')
    with st.form("exp_form", clear_on_submit=True):
        e_date = st.date_input("তারিখ", datetime.now() if not edit_exp_mode else pd.to_datetime(edit_exp_mode['Date']))
        good = st.text_area("ভালো অভিজ্ঞতা 😊", value="" if not edit_exp_mode else edit_exp_mode['Good'])
        bad = st.text_area("খারাপ অভিজ্ঞতা ☹️", value="" if not edit_exp_mode else edit_exp_mode['Bad'])
        if st.form_submit_button("সেভ"):
            if edit_exp_mode: requests.delete(f"{API_URL}/id/{edit_exp_mode['id']}?sheet=Experiences")
            e_id = str(datetime.now().timestamp()).replace(".", "")
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"id": e_id, "Date": str(e_date), "Good": good, "Bad": bad}]})
            st.session_state.edit_exp_data = None
            st.cache_data.clear(); st.rerun()
    e_df = get_data("Experiences")
    if not e_df.empty:
        st.dataframe(e_df[['Date', 'Good', 'Bad']].iloc[::-1], use_container_width=True, hide_index=True)
        with st.expander("এডিট/ডিলিট"):
            for i, row in e_df.iterrows():
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.write(f"📅 {row['Date']}")
                if c2.button("📝", key=f"ed_e_{i}"): st.session_state.edit_exp_data = row; st.rerun()
                if c3.button("🗑️", key=f"del_e_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Experiences")
                    st.cache_data.clear(); st.rerun()

# --- ট্যাব ৪: ফোনবুক (টেবিল সামারি ও '0' ফিক্স) ---
with tab_phone:
    st.subheader("📱 ফোনবুক টেবিল")
    edit_ph_mode = st.session_state.get('edit_phone_data')
    with st.form("phone_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        p_name = col1.text_input("নাম", value="" if not edit_ph_mode else str(edit_ph_mode['Name']))
        p_mobile = col2.text_input("মোবাইল নম্বর", value="" if not edit_ph_mode else str(edit_ph_mode['Mobile']))
        p_note = col3.text_input("নোট/পরিচয়", value="" if not edit_ph_mode else str(edit_ph_mode['Note']))
        if st.form_submit_button("নম্বর সেভ"):
            if p_name and p_mobile:
                num_to_save = str(p_mobile).strip()
                if not num_to_save.startswith('0'): num_to_save = '0' + num_to_save # সেভ করার সময় ০ নিশ্চিত করা
                
                if edit_ph_mode: requests.delete(f"{API_URL}/id/{edit_ph_mode['id']}?sheet=Phonebook")
                ph_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Phonebook", json={"data": [{"id": ph_id, "Name": str(p_name), "Mobile": num_to_save, "Note": str(p_note)}]})
                st.session_state.edit_phone_data = None
                st.cache_data.clear(); st.rerun()

    ph_df = get_data("Phonebook")
    if not ph_df.empty:
        st.divider()
        h1, h2, h3, h4 = st.columns([2, 2, 2, 3])
        h1.write("**নাম**"); h2.write("**মোবাইল**"); h3.write("**নোট**"); h4.write("**অ্যাকশন**")
        st.write("---")
        for i, row in ph_df.iloc[::-1].iterrows():
            r1, r2, r3, r4 = st.columns([2, 2, 2, 3])
            r1.write(row['Name']); r2.write(row['Mobile']); r3.write(row['Note'])
            with r4:
                btn1, btn2, btn3 = st.columns([1.2, 0.8, 0.8])
                btn1.markdown(f'<a href="tel:{row["Mobile"]}" class="call-btn">📞 কল দিন</a>', unsafe_allow_html=True)
                if btn2.button("📝", key=f"p_ed_{i}"): st.session_state.edit_phone_data = row; st.rerun()
                if btn3.button("🗑️", key=f"p_del_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Phonebook")
                    st.cache_data.clear(); st.rerun()
            st.write("-" * 5)

st.sidebar.button("লগআউট", on_click=lambda: st.session_state.update({"logged_in": False}))
