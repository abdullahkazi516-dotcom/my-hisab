import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. সেটিংস ও ডিজাইন
st.set_page_config(page_title="আমার ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .balance-box { background-color: #1e1e1e; color: white; padding: 20px; border-radius: 10px; text-align: center; cursor: pointer; margin-bottom: 20px; }
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
    st.subheader("🔐 লগইন করুন")
    password = st.text_input("পাসওয়ার্ড দিন", type="password")
    if st.button("প্রবেশ করুন"):
        if password == "1234": # এখানে আপনার ইচ্ছেমতো পাসওয়ার্ড দিন
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!")
    st.stop()

# ৩. ডাটা ফেচিং
@st.cache_data(ttl=5)
def get_data(sheet_name="Sheet1"):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet_name}")
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

# ৪. ব্যালেন্স ক্যালকুলেশন ও শো-হাইড
df_main = get_data("Sheet1")
if not df_main.empty:
    income = pd.to_numeric(df_main[df_main['Category'] == 'আয়']['Amount']).sum()
    expense = pd.to_numeric(df_main[df_main['Category'] == 'ব্যয়']['Amount']).sum()
    current_balance = income - expense
else:
    current_balance = 0

st.sidebar.title("💰 ব্যালেন্স চেক")
if st.sidebar.button("বর্তমান ব্যালেন্স দেখুন"):
    st.sidebar.success(f"আপনার ব্যালেন্স: {current_balance} টাকা")

# ৫. মেইন ট্যাব সিস্টেম
tab_hishab, tab_plan, tab_exp = st.tabs(["💰 লেনদেন হিসাব", "🗓️ কর্ম পরিকল্পনা", "🌟 আজকের অভিজ্ঞতা"])

# --- ট্যাব ১: লেনদেন হিসাব ---
with tab_hishab:
    st.subheader("📝 নতুন লেনদেন এন্ট্রি")
    edit_mode = st.session_state.get('edit_data')
    
    with st.form("hishab_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date = col1.date_input("তারিখ", datetime.now() if not edit_mode else pd.to_datetime(edit_mode['Date']))
        cat = col2.selectbox("বিভাগ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"], index=0 if not edit_mode else ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"].index(edit_mode['Category']))
        desc = st.text_input("বিবরণ", value="" if not edit_mode else edit_mode['Description'])
        amt = st.number_input("পরিমাণ (টাকা)", min_value=0, value=0 if not edit_mode else int(edit_mode['Amount']))
        
        if st.form_submit_button("সংরক্ষণ করুন"):
            if desc:
                if edit_mode:
                    requests.delete(f"{API_URL}/Description/{edit_mode['Description']}?sheet=Sheet1")
                new_entry = {"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [new_entry]})
                st.session_state.edit_data = None
                st.cache_data.clear(); st.success("সফলভাবে সম্পন্ন হয়েছে!"); st.rerun()

    cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    h_tabs = st.tabs(cats)
    for i, h_tab in enumerate(h_tabs):
        with h_tab:
            filtered = df_main[df_main['Category'] == cats[i]] if not df_main.empty else pd.DataFrame()
            if not filtered.empty:
                st.dataframe(filtered[['Date', 'Description', 'Amount']].iloc[::-1], use_container_width=True, hide_index=True)
                total_v = pd.to_numeric(filtered['Amount']).sum()
                st.markdown(f'<div class="total-summary">মোট {cats[i]}: {total_v} টাকা</div>', unsafe_allow_html=True)
                
                with st.expander("📝 এডিট বা 🗑️ ডিলিট"):
                    for idx, row in filtered.iterrows():
                        c1, c2, c3 = st.columns([3, 1, 1])
                        c1.write(f"{row['Date']} - {row['Description']} ({row['Amount']}৳)")
                        if c2.button("📝", key=f"ed_h_{idx}"):
                            st.session_state.edit_data = row; st.rerun()
                        if c3.button("🗑️", key=f"del_h_{idx}"):
                            requests.delete(f"{API_URL}/Description/{row['Description']}?sheet=Sheet1")
                            st.cache_data.clear(); st.rerun()

# --- ট্যাব ২: কর্ম পরিকল্পনা (Plan) ---
with tab_plan:
    st.subheader("🗓️ ভবিষ্যৎ পরিকল্পনার তালিকা")
    with st.form("plan_form", clear_on_submit=True):
        p_date = st.date_input("তারিখ", datetime.now())
        p_task = st.text_area("পরিকল্পনা")
        if st.form_submit_button("সেভ"):
            p_id = str(datetime.now().timestamp()).replace(".", "")
            requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"id": p_id, "Date": str(p_date), "Task": p_task}]})
            st.cache_data.clear(); st.success("সেভ হয়েছে!"); st.rerun()

    p_df = get_data("Plans")
    if not p_df.empty:
        for i, row in p_df.iloc[::-1].iterrows():
            st.info(f"📅 {row['Date']}: {row['Task']}")
            if st.button("🗑️ ডিলিট", key=f"p_del_{i}"):
                requests.delete(f"{API_URL}/id/{row['id']}?sheet=Plans")
                st.cache_data.clear(); st.rerun()

# --- ট্যাব ৩: আজকের অভিজ্ঞতা (Experience) ---
with tab_exp:
    st.subheader("🌟 ভালো ও খারাপ অভিজ্ঞতা")
    with st.form("exp_form", clear_on_submit=True):
        e_date = st.date_input("তারিখ", datetime.now())
        good = st.text_area("কি ভালো হয়েছে? 😊")
        bad = st.text_area("কি খারাপ হয়েছে? ☹️")
        if st.form_submit_button("ডায়েরি সেভ করুন"):
            e_id = str(datetime.now().timestamp()).replace(".", "")
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"id": e_id, "Date": str(e_date), "Good": good, "Bad": bad}]})
            st.cache_data.clear(); st.success("সেভ হয়েছে!"); st.rerun()

    e_df = get_data("Experiences")
    if not e_df.empty:
        for i, row in e_df.iloc[::-1].iterrows():
            st.markdown(f'<div class="exp-card-good"><b>{row["Date"]} (ভালো):</b><br>{row["Good"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="exp-card-bad"><b>খারাপ:</b><br>{row["Bad"]}</div>', unsafe_allow_html=True)
            if st.button("🗑️ মুছুন", key=f"e_del_{i}"):
                requests.delete(f"{API_URL}/id/{row['id']}?sheet=Experiences")
                st.cache_data.clear(); st.rerun()

# সাইডবার লগআউট
if st.sidebar.button("লগআউট"):
    st.session_state["logged_in"] = False
    st.rerun()
