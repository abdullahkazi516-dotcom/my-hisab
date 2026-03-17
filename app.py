import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ কনফিগারেশন ও কালার ডিজাইন
st.set_page_config(page_title="স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .cat-income { color: #00c853; font-weight: bold; border-left: 5px solid #00c853; padding-left: 10px; margin-bottom: 5px; }
    .cat-expense { color: #ff5252; font-weight: bold; border-left: 5px solid #ff5252; padding-left: 10px; margin-bottom: 5px; }
    .cat-arrears { color: #ffd600; font-weight: bold; border-left: 5px solid #ffd600; padding-left: 10px; margin-bottom: 5px; }
    .cat-debt { color: #ff9100; font-weight: bold; border-left: 5px solid #ff9100; padding-left: 10px; margin-bottom: 5px; }
    .cat-receivable { color: #2979ff; font-weight: bold; border-left: 5px solid #2979ff; padding-left: 10px; margin-bottom: 5px; }
    .call-btn {
        background-color: #00c853; color: white !important; padding: 5px 10px;
        text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px;
        display: inline-block; text-align: center; border: 1px solid #00a040;
    }
    </style>
    """, unsafe_allow_html=True)

# ২. লগইন সিস্টেম (পাসওয়ার্ড: 427054)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("🔐 নিরাপদ প্রবেশ")
    password = st.text_input("পাসওয়ার্ড দিন", type="password", key="login_sys_key")
    if st.button("লগইন", key="login_sys_btn"):
        if password == "427054": 
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!")
    st.stop()

# ৩. শক্তিশালী ডাটা লোড ফাংশন
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

def fetch_data(sheet_name):
    try:
        response = requests.get(f"{API_URL}?sheet={sheet_name}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return pd.DataFrame(data).astype(str)
    except Exception as e:
        st.warning(f"{sheet_name} ট্যাব লোড হতে সমস্যা হচ্ছে।")
    return pd.DataFrame()

# ৪. ট্যাব সিস্টেম
tab_hishab, tab_plan, tab_exp, tab_phone = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

# --- লেনদেন ট্যাব ---
with tab_hishab:
    df_main = fetch_data("Sheet1")
    edit_data = st.session_state.get('edit_data')
    categories = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    
    # এরর প্রোটেকশনসহ ভেরিয়েবল
    d_val, cat_idx, desc_val, amt_val = datetime.now(), 0, "", 0
    if edit_data:
        try:
            # তারিখ ফিক্স
            raw_date = str(edit_data.get('Date', ''))
            d_val = pd.to_datetime(raw_date).to_pydatetime() if raw_date else datetime.now()
            # ক্যাটাগরি ফিক্স
            raw_cat = edit_data.get('Category', 'আয়')
            cat_idx = categories.index(raw_cat) if raw_cat in categories else 0
            # অন্যান্য
            desc_val = edit_data.get('Description', "")
            amt_val = int(float(edit_data.get('Amount', 0)))
        except:
            d_val, cat_idx, desc_val, amt_val = datetime.now(), 0, "", 0

    with st.form("form_hishab_safe", clear_on_submit=True):
        c1, c2 = st.columns(2)
        date_in = c1.date_input("তারিখ", d_val, key="h_date_in")
        cat_in = c2.selectbox("বিভাগ", categories, index=cat_idx, key="h_cat_in")
        desc_in = st.text_input("বিবরণ", value=desc_val, key="h_desc_in")
        amt_in = st.number_input("পরিমাণ", min_value=0, value=amt_val, key="h_amt_in")
        
        if st.form_submit_button("সেভ করুন"):
            if desc_in:
                if edit_data: requests.delete(f"{API_URL}/Description/{edit_data['Description']}?sheet=Sheet1")
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(date_in), "Description": desc_in, "Category": cat_in, "Amount": str(amt_in)}]})
                st.session_state.edit_data = None
                st.rerun()

    if not df_main.empty:
        h_tabs = st.tabs(categories)
        colors = ["cat-income", "cat-expense", "cat-arrears", "cat-debt", "cat-receivable"]
        for i, h_tab in enumerate(h_tabs):
            with h_tab:
                sub = df_main[df_main['Category'] == categories[i]]
                if not sub.empty:
                    st.markdown(f'<div class="{colors[i]}">{categories[i]} লিস্ট</div>', unsafe_allow_html=True)
                    st.dataframe(sub[['Date', 'Description', 'Amount']].iloc[::-1], use_container_width=True, hide_index=True)
                    with st.expander("এডিট বা ডিলিট"):
                        for idx, row in sub.iterrows():
                            col1, col2, col3 = st.columns([3, 1, 1])
                            col1.write(f"{row['Date']} - {row['Description']}")
                            if col2.button("📝", key=f"ed_h_{idx}_{i}"):
                                st.session_state.edit_data = row; st.rerun()
                            if col3.button("🗑️", key=f"del_h_{idx}_{i}"):
                                requests.delete(f"{API_URL}/Description/{row['Description']}?sheet=Sheet1")
                                st.rerun()

# --- পরিকল্পনা ট্যাব ---
with tab_plan:
    st.subheader("🗓️ পরিকল্পনা")
    with st.form("form_plan_safe", clear_on_submit=True):
        p_task = st.text_area("নতুন কাজ/পরিকল্পনা", key="p_task_input")
        if st.form_submit_button("সেভ"):
            if p_task:
                p_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"id": p_id, "Date": str(datetime.now().date()), "Task": p_task}]})
                st.rerun()
    
    df_p = fetch_data("Plans")
    if not df_p.empty:
        st.dataframe(df_p[['Date', 'Task']].iloc[::-1], use_container_width=True, hide_index=True)
        for i, row in df_p.iterrows():
            with st.container():
                c1, c2 = st.columns([5, 1])
                c1.write(f"📌 {row['Task']}")
                if c2.button("🗑️", key=f"p_del_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Plans"); st.rerun()

# --- অভিজ্ঞতা ট্যাব ---
with tab_exp:
    st.subheader("🌟 অভিজ্ঞতা")
    with st.form("form_exp_safe", clear_on_submit=True):
        good = st.text_area("ভালো অভিজ্ঞতা", key="e_good")
        bad = st.text_area("খারাপ অভিজ্ঞতা", key="e_bad")
        if st.form_submit_button("সেভ করুন"):
            e_id = str(datetime.now().timestamp()).replace(".", "")
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"id": e_id, "Date": str(datetime.now().date()), "Good": good, "Bad": bad}]})
            st.rerun()
    
    df_e = fetch_data("Experiences")
    if not df_e.empty:
        st.dataframe(df_e[['Date', 'Good', 'Bad']].iloc[::-1], use_container_width=True, hide_index=True)

# --- ফোনবুক ট্যাব ---
with tab_phone:
    st.subheader("📱 ফোনবুক")
    df_ph = fetch_data("Phonebook")
    edit_ph = st.session_state.get('edit_phone_data')
    with st.form("form_phone_safe", clear_on_submit=True):
        n_in = st.text_input("নাম", value=edit_ph['Name'] if edit_ph else "", key="ph_n")
        m_in = st.text_input("মোবাইল", value=edit_ph['Mobile'] if edit_ph else "", key="ph_m")
        if st.form_submit_button("সেভ"):
            if n_in and m_in:
                mob = str(m_in).strip()
                if not mob.startswith('0'): mob = '0' + mob
                if edit_ph: requests.delete(f"{API_URL}/id/{edit_ph['id']}?sheet=Phonebook")
                ph_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Phonebook", json={"data": [{"id": ph_id, "Name": n_in, "Mobile": mob}]})
                st.session_state.edit_phone_data = None; st.rerun()

    if not df_ph.empty:
        for i, row in df_ph.iloc[::-1].iterrows():
            r1, r2, r3 = st.columns([3, 1, 1])
            r1.write(f"👤 {row['Name']} ({row['Mobile']})")
            r2.markdown(f'<a href="tel:{row["Mobile"]}" class="call-btn">📞 কল</a>', unsafe_allow_html=True)
            if r3.button("🗑️", key=f"ph_del_{i}"):
                requests.delete(f"{API_URL}/id/{row['id']}?sheet=Phonebook"); st.rerun()
