import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও সিএসএস (ডিজাইন)
st.set_page_config(page_title="স্মার্ট পার্সোনাল ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .total-summary { background-color: #f1f3f4; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 18px; color: #1967d2; margin: 10px 0; }
    .call-link {
        background-color: #00c853; color: white !important; padding: 6px 12px;
        text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 14px;
        display: inline-block; border: 1px solid #00a040;
    }
    .call-link:hover { background-color: #00e676; }
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

# ৩. ডাটা লোড ফাংশন
@st.cache_data(ttl=5)
def get_data(sheet_name="Sheet1"):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet_name}")
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

# ৪. ব্যালেন্স ক্যালকুলেশন
df_main = get_data("Sheet1")
current_balance = 0
if not df_main.empty:
    df_main['Amount'] = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    income = df_main[df_main['Category'] == 'আয়']['Amount'].sum()
    expense = df_main[df_main['Category'] == 'ব্যয়']['Amount'].sum()
    current_balance = income - expense

# ব্যালেন্স বাটন
st.subheader("🏦 ক্যাশ স্ট্যাটাস")
if "show_balance" not in st.session_state: st.session_state.show_balance = False
balance_label = f"ব্যালেন্স: {current_balance} ৳" if st.session_state.show_balance else "ব্যালেন্স দেখতে ক্লিক করুন"
if st.button(balance_label, use_container_width=True, type="primary"):
    st.session_state.show_balance = not st.session_state.show_balance
    st.rerun()

# ৫. ট্যাব সিস্টেম
tab_hishab, tab_plan, tab_exp, tab_phone = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

# --- ট্যাব ১: লেনদেন হিসাব ---
with tab_hishab:
    st.subheader("📝 নতুন লেনদেন")
    edit_mode = st.session_state.get('edit_data')
    with st.form("hishab_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        date = c1.date_input("তারিখ", datetime.now() if not edit_mode else pd.to_datetime(edit_mode['Date']))
        cat = c2.selectbox("বিভাগ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"], index=0 if not edit_mode else ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"].index(edit_mode['Category']))
        desc = st.text_input("বিবরণ", value="" if not edit_mode else edit_mode['Description'])
        amt = st.number_input("পরিমাণ", min_value=0, value=0 if not edit_mode else int(edit_mode['Amount']))
        if st.form_submit_button("সেভ করুন"):
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
    st.subheader("🗓️ নতুন পরিকল্পনা")
    with st.form("plan_form", clear_on_submit=True):
        p_date = st.date_input("তারিখ", datetime.now())
        p_task = st.text_area("আপনার পরিকল্পনা")
        if st.form_submit_button("প্ল্যান সেভ"):
            p_id = str(datetime.now().timestamp()).replace(".", "")
            requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"id": p_id, "Date": str(p_date), "Task": p_task}]})
            st.cache_data.clear(); st.success("প্ল্যান সেভ হয়েছে!"); st.rerun()
    p_df = get_data("Plans")
    if not p_df.empty:
        st.subheader("📋 সকল পরিকল্পনা")
        st.dataframe(p_df[['Date', 'Task']].iloc[::-1], use_container_width=True, hide_index=True)
        with st.expander("পরিকল্পনা ডিলিট করুন"):
            for i, row in p_df.iterrows():
                c1, c2 = st.columns([5, 1])
                c1.write(f"📅 {row['Date']}: {row['Task']}")
                if c2.button("🗑️", key=f"p_del_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Plans")
                    st.cache_data.clear(); st.rerun()

# --- ট্যাব ৩: অভিজ্ঞতা ---
with tab_exp:
    st.subheader("✍️ ডায়েরি এন্ট্রি")
    edit_exp_mode = st.session_state.get('edit_exp_data')
    with st.form("exp_form", clear_on_submit=True):
        e_date = st.date_input("তারিখ", datetime.now() if not edit_exp_mode else pd.to_datetime(edit_exp_mode['Date']))
        good = st.text_area("ভালো 😊", value="" if not edit_exp_mode else edit_exp_mode['Good'])
        bad = st.text_area("খারাপ ☹️", value="" if not edit_exp_mode else edit_exp_mode['Bad'])
        if st.form_submit_button("অভিজ্ঞতা সেভ"):
            if edit_exp_mode: requests.delete(f"{API_URL}/id/{edit_exp_mode['id']}?sheet=Experiences")
            e_id = str(datetime.now().timestamp()).replace(".", "")
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"id": e_id, "Date": str(e_date), "Good": good, "Bad": bad}]})
            st.session_state.edit_exp_data = None
            st.cache_data.clear(); st.success("সেভ হয়েছে!"); st.rerun()
    e_df = get_data("Experiences")
    if not e_df.empty:
        st.subheader("📋 অভিজ্ঞতার সামারি")
        st.dataframe(e_df[['Date', 'Good', 'Bad']].iloc[::-1], use_container_width=True, hide_index=True)
        with st.expander("এডিট বা ডিলিট করুন"):
            for i, row in e_df.iterrows():
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.write(f"📅 {row['Date']}")
                if c2.button("📝", key=f"ed_e_{i}"): st.session_state.edit_exp_data = row; st.rerun()
                if c3.button("🗑️", key=f"del_e_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Experiences")
                    st.cache_data.clear(); st.rerun()

# --- ট্যাব ৪: ফোনবুক (কল, এডিট, ডিলিট সহ) ---
with tab_phone:
    st.subheader("📱 ফোনবুক")
    edit_ph_mode = st.session_state.get('edit_phone_data')
    with st.form("phone_form", clear_on_submit=True):
        col_n, col_m, col_note = st.columns(3)
        p_name = col_n.text_input("নাম", value="" if not edit_ph_mode else edit_ph_mode['Name'])
        p_mobile = col_m.text_input("মোবাইল", value="" if not edit_ph_mode else edit_ph_mode['Mobile'])
        p_note = col_note.text_input("নোট", value="" if not edit_ph_mode else edit_ph_mode['Note'])
        if st.form_submit_button("সংরক্ষণ"):
            if p_name and p_mobile:
                if edit_ph_mode: requests.delete(f"{API_URL}/id/{edit_ph_mode['id']}?sheet=Phonebook")
                ph_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Phonebook", json={"data": [{"id": ph_id, "Name": p_name, "Mobile": p_mobile, "Note": p_note}]})
                st.session_state.edit_phone_data = None
                st.cache_data.clear(); st.success("সংরক্ষিত!"); st.rerun()

    ph_df = get_data("Phonebook")
    if not ph_df.empty:
        st.divider()
        h1, h2, h3, h4 = st.columns([2, 2, 2, 3])
        h1.write("**নাম**"); h2.write("**মোবাইল**"); h3.write("**নোট**"); h4.write("**অ্যাকশন**")
        st.write("---")
        for i, row in ph_df.iterrows():
            c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
            c1.write(row['Name']); c2.write(row['Mobile']); c3.write(row['Note'])
            with c4:
                b1, b2, b3 = st.columns([1.2, 1, 1])
                b1.markdown(f'<a href="tel:{row["Mobile"]}" class="call-link">📞 কল</a>', unsafe_allow_html=True)
                if b2.button("📝", key=f"ph_ed_{i}"): st.session_state.edit_phone_data = row; st.rerun()
                if b3.button("🗑️", key=f"ph_del_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Phonebook")
                    st.cache_data.clear(); st.rerun()
            st.write("-" * 5)

# লগআউট
st.sidebar.button("লগআউট", on_click=lambda: st.session_state.update({"logged_in": False}))
