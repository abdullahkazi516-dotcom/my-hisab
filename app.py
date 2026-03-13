import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# পেজ সেটিংস
st.set_page_config(page_title="আমার ডিজিটাল ক্যাশ বুক", page_icon="💰")

#
API_URL =https://sheetdb.io/api/v1/7mzpsfz9aa5r7

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
    
    # ডেটা পড়া
    try:
        response = requests.get(API_URL)
        df = pd.DataFrame(response.json())
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    except:
        df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])

    # ড্যাশবোর্ড (হিসাব কিতাব)
    if not df.empty:
        ti = df[df['Category'] == 'আয়']['Amount'].sum()
        te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
        td = df[df['Category'] == 'বকেয়া']['Amount'].sum()
        tp = df[df['Category'] == 'পাওনা']['Amount'].sum()
        tp_paid = df[df['Category'] == 'বকেয়া পরিশোধ']['Amount'].sum()
        
        current_due = td - tp_paid
        balance = ti - te - tp_paid

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("মোট আয়", f"{ti}")
        col2.metric("মোট ব্যয়", f"-{te}")
        col3.metric("বর্তমান বকেয়া", f"{current_due}")
        col4.metric("মোট পাওনা", f"{tp}")
        st.info(f"💵 **বর্তমান নগদ জমা: {balance} টাকা**")

    # ইনপুট ফর্ম
    with st.form("entry_form", clear_on_submit=True):
        date = st.date_input("তারিখ নির্বাচন করুন", datetime.now())
        cat = st.selectbox("হিসাবের ধরণ", ["আয়", "ব্যয়", "বকেয়া", "পাওনা", "বকেয়া পরিশোধ"])
        desc = st.text_input("বিবরণ")
        amt = st.number_input("টাকার পরিমাণ", min_value=0, step=1)
        submit = st.form_submit_button("✅ নিশ্চিত করুন ও সেভ করুন")

    if submit:
        if desc == "" or amt == 0:
            st.warning("সঠিক তথ্য দিন।")
        else:
            new_data = {"data": [{"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}]}
            res = requests.post(API_URL, json=new_data)
            if res.status_code == 201:
                st.success(f"সফলভাবে {cat} হিসেবে সেভ হয়েছে!")
                st.rerun()
            else:
                st.error("গুগল শিটে সেভ হতে পারছে না।")

    st.subheader("📊 হিসাবের তালিকা")
    st.dataframe(df.iloc[::-1], use_container_width=True)

    if st.sidebar.button("লগআউট"):
        st.session_state["logged_in"] = False
        st.rerun()


