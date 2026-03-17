import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও ডিজাইন
st.set_page_config(page_title="স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .call-btn {
        background-color: #00c853; color: white !important; padding: 5px 10px;
        text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px;
        display: inline-block; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# API লিঙ্ক
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন সিস্টেম
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("🔐 নিরাপদ প্রবেশ")
    password = st.text_input("পাসওয়ার্ড দিন", type="password", key="main_login_pass")
    if st.button("লগইন", key="main_login_btn"):
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
        df = pd.DataFrame(res.json())
        return df.astype(str) if not df.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

# ৪. ডাটা তৈরি
df_main = get_data("Sheet1")

# ৫. ট্যাব সিস্টেম
tab_hishab, tab_plan, tab_exp, tab_phone = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

# --- ট্যাব ১: লেনদেন ---
with tab_hishab:
    st.subheader("📝 লেনদেন এন্ট্রি")
    edit_mode = st.session_state.get('edit_data')
    
    # এরর প্রোটেকশন: তারিখ ও অ্যামাউন্ট চেক
    try:
        if edit_mode and 'Date' in edit_mode:
            d_val = pd.to_datetime(edit_mode['Date']).to_pydatetime()
        else:
            d_val = datetime.now()
    except:
        d_val = datetime.now()

    with st.form("hishab_form_new", clear_on_submit=True):
        c1, c2 = st.columns(2)
        date = c1.date_input("তারিখ", d_val, key="h_date_input")
        categories = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
        current_cat = edit_mode['Category'] if edit_mode and edit_mode['Category'] in categories else "আয়"
        cat = c2.selectbox("বিভাগ", categories, index=categories.index(current_cat), key="h_cat_select")
        
        desc_val = edit_mode['Description'] if edit_mode else ""
        desc = st.text_input("বিবরণ", value=desc_val, key="h_desc_input")
        
        try:
            amt_default = int(float(edit_mode['Amount'])) if edit_mode else 0
        except:
            amt_default = 0
        amt = st.number_input("পরিমাণ", min_value=0, value=amt_default, key="h_amt_input")
        
        if st.form_submit_button("সেভ করুন"):
            if desc:
                if edit_mode: requests.delete(f"{API_URL}/Description/{edit_mode['Description']}?sheet=Sheet1")
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(date), "Description": desc, "Category": cat, "Amount": str(amt)}]})
                st.session_state.edit_data = None
                st.cache_data.clear(); st.rerun()

    st.divider()
    if not df_main.empty:
        cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
        h_tabs = st.tabs(cats)
        for i, h_tab in enumerate(h_tabs):
            with h_tab:
                filtered = df_main[df_main['Category'] == cats[i]]
                if not filtered.empty:
                    st.dataframe(filtered[['Date', 'Description', 'Amount']].iloc[::-1], use_container_width=True, hide_index=True)
                    total = pd.to_numeric(filtered['Amount'], errors='coerce').sum()
                    st.success(f"মোট {cats[i]}: {total} ৳")
                    with st.expander("এডিট বা ডিলিট"):
                        for idx, row in filtered.iterrows():
                            col1, col2, col3 = st.columns([3, 1, 1])
                            col1.write(f"{row['Date']} - {row['Description']}")
                            if col2.button("📝", key=f"ed_h_{idx}_{i}"):
                                st.session_state.edit_data = row; st.rerun()
                            if col3.button("🗑️", key=f"del_h_{idx}_{i}"):
                                requests.delete(f"{API_URL}/Description/{row['Description']}?sheet=Sheet1")
                                st.cache_data.clear(); st.rerun()

# --- ট্যাব ২: পরিকল্পনা ---
with tab_plan:
    st.subheader("🗓️ পরিকল্পনা")
    with st.form("plan_form_new", clear_on_submit=True):
        p_task = st.text_area("নতুন পরিকল্পনা", key="p_task_input")
        if st.form_submit_button("প্ল্যান সেভ"):
            if p_task:
                p_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"id": p_id, "Date": str(datetime.now().date()), "Task": p_task}]})
                st.cache_data.clear(); st.rerun()
    
    p_df = get_data("Plans")
    if not p_df.empty:
        st.dataframe(p_df[['Date', 'Task']].iloc[::-1], use_container_width=True, hide_index=True)
        with st.expander("ডিলিট করুন"):
            for i, row in p_df.iterrows():
                c1, c2 = st.columns([5, 1])
                c1.write(f"📅 {row['Date']}: {row['Task']}")
                if c2.button("🗑️", key=f"p_del_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Plans")
                    st.cache_data.clear(); st.rerun()

# --- ট্যাব ৩: অভিজ্ঞতা ---
with tab_exp:
    st.subheader("🌟 অভিজ্ঞতা")
    with st.form("exp_form_new", clear_on_submit=True):
        good = st.text_area("ভালো অভিজ্ঞতা", key="exp_good_in")
        bad = st.text_area("খারাপ অভিজ্ঞতা", key="exp_bad_in")
        if st.form_submit_button("ডায়েরি সেভ"):
            e_id = str(datetime.now().timestamp()).replace(".", "")
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"id": e_id, "Date": str(datetime.now().date()), "Good": good, "Bad": bad}]})
            st.cache_data.clear(); st.rerun()
    
    e_df = get_data("Experiences")
    if not e_df.empty:
        st.dataframe(e_df[['Date', 'Good', 'Bad']].iloc[::-1], use_container_width=True, hide_index=True)
        with st.expander("ডিলিট করুন"):
            for i, row in e_df.iterrows():
                c1, c2 = st.columns([5, 1])
                c1.write(f"📅 {row['Date']}")
                if c2.button("🗑️", key=f"e_del_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Experiences")
                    st.cache_data.clear(); st.rerun()

# --- ট্যাব ৪: ফোনবুক ---
with tab_phone:
    st.subheader("📱 ফোনবুক টেবিল")
    edit_ph_mode = st.session_state.get('edit_phone_data')
    with st.form("phone_form_new", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        p_name = col1.text_input("নাম", value=edit_ph_mode['Name'] if edit_ph_mode else "", key="ph_name_in")
        p_mobile = col2.text_input("মোবাইল নম্বর", value=edit_ph_mode['Mobile'] if edit_ph_mode else "", key="ph_mob_in")
        p_note = col3.text_input("নোট", value=edit_ph_mode['Note'] if edit_ph_mode else "", key="ph_note_in")
        if st.form_submit_button("সেভ"):
            if p_name and p_mobile:
                mob = str(p_mobile).strip()
                if not mob.startswith('0'): mob = '0' + mob
                if edit_ph_mode: requests.delete(f"{API_URL}/id/{edit_ph_mode['id']}?sheet=Phonebook")
                ph_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Phonebook", json={"data": [{"id": ph_id, "Name": p_name, "Mobile": mob, "Note": p_note}]})
                st.session_state.edit_phone_data = None
                st.cache_data.clear(); st.rerun()

    ph_df = get_data("Phonebook")
    if not ph_df.empty:
        # '0' ফিক্স
        ph_df['Mobile'] = ph_df['Mobile'].apply(lambda x: '0' + str(x) if (str(x).startswith('1') and len(str(x)) == 10) else str(x))
        st.write("---")
        h1, h2, h3, h4 = st.columns([2, 2, 2, 3])
        h1.write("**নাম**"); h2.write("**মোবাইল**"); h3.write("**নোট**"); h4.write("**অ্যাকশন**")
        for i, row in ph_df.iloc[::-1].iterrows():
            r1, r2, r3, r4 = st.columns([2, 2, 2, 3])
            r1.write(row['Name']); r2.write(row['Mobile']); r3.write(row['Note'])
            with r4:
                b1, b2, b3 = st.columns([1.2, 0.8, 0.8])
                b1.markdown(f'<a href="tel:{row["Mobile"]}" class="call-btn">📞 কল</a>', unsafe_allow_html=True)
                if b2.button("📝", key=f"ph_ed_{i}"):
                    st.session_state.edit_phone_data = row; st.rerun()
                if b3.button("🗑️", key=f"ph_de_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Phonebook")
                    st.cache_data.clear(); st.rerun()
            st.write("-" * 5)
