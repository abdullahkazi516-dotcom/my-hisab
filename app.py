import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও ডিজাইন
st.set_page_config(page_title="আমার ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .total-summary { background-color: #f1f3f4; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 18px; color: #1967d2; margin: 10px 0; }
    .exp-card-good { border-left: 5px solid #28a745; background-color: #f8fff9; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .exp-card-bad { border-left: 5px solid #dc3545; background-color: #fff8f8; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# API লিঙ্ক
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন সিস্টেম
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("🔐 নিরাপদ প্রবেশ")
    password = st.text_input("পাসওয়ার্ড দিন", type="password")
    if st.button("লগইন"):
        if password == "1234": 
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

# --- ব্যালেন্স শো/হাইড বাটন ---
st.subheader("🏦 ক্যাশ স্ট্যাটাস")
if "show_balance" not in st.session_state:
    st.session_state.show_balance = False

balance_label = f"আপনার ব্যালেন্স: {current_balance} ৳" if st.session_state.show_balance else "ব্যালেন্স দেখতে এখানে ক্লিক করুন"
if st.button(balance_label, use_container_width=True, type="primary"):
    st.session_state.show_balance = not st.session_state.show_balance
    st.rerun()

# ৫. ট্যাব সিস্টেম
tab_hishab, tab_plan, tab_exp = st.tabs(["💰 লেনদেন হিসাব", "🗓️ কর্ম পরিকল্পনা", "🌟 আজকের অভিজ্ঞতা"])

# --- ট্যাব ১: লেনদেন হিসাব ---
with tab_hishab:
    st.subheader("📝 নতুন লেনদেন")
    edit_mode = st.session_state.get('edit_data')
    with st.form("hishab_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date = col1.date_input("তারিখ", datetime.now() if not edit_mode else pd.to_datetime(edit_mode['Date']))
        cat = col2.selectbox("বিভাগ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"], index=0 if not edit_mode else ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"].index(edit_mode['Category']))
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
                total_v = pd.to_numeric(filtered['Amount']).sum()
                st.markdown(f'<div class="total-summary">মোট {cats[i]}: {total_v} টাকা</div>', unsafe_allow_html=True)
                with st.expander("এডিট/ডিলিট"):
                    for idx, row in filtered.iterrows():
                        c1, c2, c3 = st.columns([3, 1, 1])
                        c1.write(f"{row['Date']} - {row['Description']}")
                        if c2.button("📝", key=f"ed_h_{idx}"): st.session_state.edit_data = row; st.rerun()
                        if c3.button("🗑️", key=f"del_h_{idx}"):
                            requests.delete(f"{API_URL}/Description/{row['Description']}?sheet=Sheet1")
                            st.cache_data.clear(); st.rerun()

# --- ট্যাব ২: কর্ম পরিকল্পনা (টেবিল সামারি সহ) ---
with tab_plan:
    st.subheader("📝 নতুন পরিকল্পনা যোগ করুন")
    with st.form("plan_form", clear_on_submit=True):
        p_date = st.date_input("পরিকল্পনার তারিখ", datetime.now())
        p_task = st.text_area("কি কাজ করতে চান?")
        if st.form_submit_button("প্ল্যান সেভ করুন"):
            if p_task:
                p_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"id": p_id, "Date": str(p_date), "Task": p_task}]})
                st.cache_data.clear(); st.success("প্ল্যান সেভ হয়েছে!"); st.rerun()

    st.divider()
    st.subheader("📋 সকল পরিকল্পনার সামারি")
    p_df = get_data("Plans")
    if not p_df.empty:
        # এখানে টেবিল আকারে দেখা যাবে
        st.dataframe(p_df[['Date', 'Task']].iloc[::-1], use_container_width=True, hide_index=True)
        
        with st.expander("এডিট বা ডিলিট করতে এখানে ক্লিক করুন"):
            for i, row in p_df.iloc[::-1].iterrows():
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"📅 {row['Date']}: {row['Task']}")
                if col_b.button("🗑️", key=f"p_del_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Plans")
                    st.cache_data.clear(); st.rerun()
    else:
        st.info("কোনো পরিকল্পনা খুঁজে পাওয়া যায়নি।")

# --- ট্যাব ৩: আজকের অভিজ্ঞতা ---
with tab_exp:
    st.subheader("✍️ ডায়েরি এন্ট্রি")
    with st.form("exp_form", clear_on_submit=True):
        e_date = st.date_input("তারিখ", datetime.now(), key="diary_date")
        good = st.text_area("ভালো অভিজ্ঞতা 😊")
        bad = st.text_area("খারাপ অভিজ্ঞতা ☹️")
        if st.form_submit_button("অভিজ্ঞতা সেভ"):
            e_id = str(datetime.now().timestamp()).replace(".", "")
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"id": e_id, "Date": str(e_date), "Good": good, "Bad": bad}]})
            st.cache_data.clear(); st.success("সেভ হয়েছে!"); st.rerun()

    e_df = get_data("Experiences")
    if not e_df.empty:
        for i, row in e_df.iloc[::-1].iterrows():
            st.markdown(f'<div class="exp-card-good"><b>📅 {row["Date"]} (ভালো):</b><br>{row["Good"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="exp-card-bad"><b>খারাপ:</b><br>{row["Bad"]}</div>', unsafe_allow_html=True)
            if st.button("🗑️ ডিলিট করুন", key=f"e_del_{i}"):
                requests.delete(f"{API_URL}/id/{row['id']}?sheet=Experiences")
                st.cache_data.clear(); st.rerun()
            st.divider()

# লগআউট
st.sidebar.button("লগআউট", on_click=lambda: st.session_state.update({"logged_in": False}))
