import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও সিএসএস (কল বাটনের রঙ উজ্জ্বল করা হয়েছে)
st.set_page_config(page_title="আমার স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .total-summary { background-color: #f1f3f4; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 18px; color: #1967d2; margin: 10px 0; }
    
    /* কল বাটনের স্টাইল - উজ্জ্বল সবুজ */
    .call-link {
        background-color: #00c853; 
        color: white !important;
        padding: 6px 12px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
        border: 1px solid #00a040;
    }
    .call-link:hover {
        background-color: #00e676;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
    }
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

# ৪. ব্যালেন্স ও ট্যাব সিস্টেম
df_main = get_data("Sheet1")
tab_hishab, tab_plan, tab_exp, tab_phone = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

# --- ট্যাব ৪: 📱 ফোনবুক (টেবিল ভিউ + কল, এডিট, ডিলিট) ---
with tab_phone:
    st.subheader("📱 ফোনবুক")
    
    # এডিট চেক
    edit_ph_mode = st.session_state.get('edit_phone_data')
    
    # ইনপুট ফর্ম
    with st.form("phone_form", clear_on_submit=True):
        col_n, col_m, col_note = st.columns([2, 2, 2])
        p_name = col_n.text_input("নাম", value="" if not edit_ph_mode else edit_ph_mode['Name'])
        p_mobile = col_m.text_input("মোবাইল নম্বর", value="" if not edit_ph_mode else edit_ph_mode['Mobile'])
        p_note = col_note.text_input("নোট", value="" if not edit_ph_mode else edit_ph_mode['Note'])
        
        if st.form_submit_button("সংরক্ষণ করুন"):
            if p_name and p_mobile:
                if edit_ph_mode:
                    requests.delete(f"{API_URL}/id/{edit_ph_mode['id']}?sheet=Phonebook")
                
                ph_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Phonebook", json={"data": [{"id": ph_id, "Name": p_name, "Mobile": p_mobile, "Note": p_note}]})
                st.session_state.edit_phone_data = None
                st.cache_data.clear(); st.success("সফলভাবে সংরক্ষিত!"); st.rerun()

    st.divider()
    ph_df = get_data("Phonebook")
    
    if not ph_df.empty:
        # টেবিল হেডার
        h1, h2, h3, h4 = st.columns([2, 2, 2, 3])
        h1.write("**নাম**")
        h2.write("**মোবাইল**")
        h3.write("**নোট**")
        h4.write("**অ্যাকশন**")
        st.write("---")
        
        for i, row in ph_df.iterrows():
            c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
            c1.write(row['Name'])
            c2.write(row['Mobile'])
            c3.write(row['Note'])
            
            # কল, এডিট এবং ডিলিট বাটন একসাথে
            with c4:
                btn_col1, btn_col2, btn_col3 = st.columns([1.2, 1, 1])
                # কল বাটন (HTML)
                btn_col1.markdown(f'<a href="tel:{row["Mobile"]}" class="call-link">📞 কল</a>', unsafe_allow_html=True)
                # এডিট বাটন
                if btn_col2.button("📝", key=f"ph_ed_{i}"):
                    st.session_state.edit_phone_data = row
                    st.rerun()
                # ডিলিট বাটন
                if btn_col3.button("🗑️", key=f"ph_del_{i}"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Phonebook")
                    st.cache_data.clear(); st.rerun()
            st.write("-" * 10) # রো ডিভাইডার
    else:
        st.info("ফোনবুকে কোনো নম্বর নেই।")

# বাকি ট্যাবগুলো আগের মতোই থাকবে (কোড সংক্ষেপিত)
with tab_hishab:
    st.write("লেনদেন হিসাব এখানে...") # আপনার আগের লেনদেনের কোড এখানে থাকবে
with tab_plan:
    st.write("পরিকল্পনা এখানে...") # আপনার আগের পরিকল্পনার কোড এখানে থাকবে
with tab_exp:
    st.write("অভিজ্ঞতা এখানে...") # আপনার আগের অভিজ্ঞতার কোড এখানে থাকবে

# লগআউট
st.sidebar.button("লগআউট", on_click=lambda: st.session_state.update({"logged_in": False}))
