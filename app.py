
import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# পেজ সেটআপ
st.set_page_config(page_title="আমার ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

# লগইন ফাংশন
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        st.title("🔐 লগইন করুন")
        user = st.text_input("ইউজারনেম")
        pw = st.text_input("পাসওয়ার্ড", type="password")
        if st.button("প্রবেশ করুন"):
            if user == "admin" and pw == "123":
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("ভুল ইউজারনেম বা পাসওয়ার্ড")
        return False
    return True

if check_password():
    st.title("💰 আমার ডিজিটাল ক্যাশ বুক")
    
    # গুগল শিট লিঙ্ক (CSV ফরম্যাটে পড়ার জন্য)
    sheet_id = "191eFwqQGyYT4Ip67pa_hjTZthWLExugah63UAqQ44Ag"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    
    try:
        df = pd.read_csv(csv_url)
    except:
        df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])

    # ড্যাশবোর্ড
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        ti = df[df['Category'] == 'আয়']['Amount'].sum()
        te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
        td = df[df['Category'] == 'বকেয়া']['Amount'].sum()
        tp = df[df['Category'] == 'পাওনা']['Amount'].sum()
        tp_paid = df[df['Category'] == 'বকেয়া পরিশোধ']['Amount'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("মোট আয়", f"{ti} টাকা")
        col2.metric("মোট ব্যয়", f"-{te} টাকা")
        col3.metric("বর্তমান বকেয়া", f"{td - tp_paid} টাকা")
        col4.metric("মোট পাওনা", f"{tp} টাকা")
        st.info(f"💵 **বর্তমান নগদ: {ti - te - tp_paid} টাকা**")

    # ডাটা ইনপুট ফর্ম
    with st.expander("➕ নতুন হিসাব যোগ করুন", expanded=True):
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("তারিখ", datetime.now())
                cat = st.selectbox("ধরণ", ["আয়", "ব্যয়", "বকেয়া", "পাওনা", "বকেয়া পরিশোধ"])
            with col2:
                desc = st.text_input("বিবরণ")
                amt = st.number_input("টাকার পরিমাণ", min_value=0, step=1)
            submit = st.form_submit_button("✅ নিশ্চিত করুন ও সেভ করুন")

    if submit:
        if desc == "" or amt == 0:
            st.warning("সঠিক তথ্য দিন।")
        else:
            # ডাটা সেভ করার জন্য streamlit-gsheets ব্যবহার
            from streamlit_gsheets import GSheetsConnection
            conn = st.connection("gsheets", type=GSheetsConnection)
            full_df = conn.read(ttl="0s")
            new_row = pd.DataFrame([{"Date": date.strftime('%Y-%m-%d'), "Description": desc, "Category": cat, "Amount": amt}])
            updated_df = pd.concat([full_df, new_row], ignore_index=True)
            
            try:
                conn.update(data=updated_df)
                st.success("হিসাব সেভ হয়েছে!")
                st.rerun()
            except Exception as e:
                st.error("গুগল শিট পারমিশন এরর। অনুগ্রহ করে শিটটি Share > Anyone with link > Editor আছে কি না চেক করুন।")

    st.subheader("📊 হিসাবের তালিকা")
    st.dataframe(df.iloc[::-1], use_container_width=True)

    if st.sidebar.button("লগআউট"):
        st.session_state["logged_in"] = False
        st.rerun()
