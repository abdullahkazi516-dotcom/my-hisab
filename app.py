import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

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
    
    # কানেকশন তৈরি
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="0s")

    # ড্যাশবোর্ড (Dashboard)
    if not df.empty:
        total_income = pd.to_numeric(df[df['Category'] == 'আয়']['Amount']).sum()
        total_expense = pd.to_numeric(df[df['Category'] == 'ব্যয়']['Amount']).sum()
        total_due = pd.to_numeric(df[df['Category'] == 'বকেয়া']['Amount']).sum()
        total_receivable = pd.to_numeric(df[df['Category'] == 'পাওনা']['Amount']).sum()
        balance = total_income - total_expense

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("মোট আয়", f"{total_income} টাকা")
        col2.metric("মোট ব্যয়", f"-{total_expense} টাকা")
        col3.metric("মোট বকেয়া", f"{total_due} টাকা")
        col4.metric("মোট পাওনা", f"{total_receivable} টাকা")
        
        st.info(f"💵 **বর্তমান ক্যাশ ব্যালেন্স: {balance} টাকা**")
        st.divider()

    # ডাটা ইনপুট ফর্ম (এখানে আপনার চাহিদা মতো ধরণ আগে দেওয়া হয়েছে)
    with st.expander("➕ নতুন হিসাব যোগ করুন", expanded=True):
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("তারিখ নির্বাচন করুন", datetime.now())
                # 'ধরণ' এখন আগে আসবে
                cat = st.selectbox("হিসাবের ধরণ", ["আয়", "ব্যয়", "বকেয়া", "পাওনা"])
            with col2:
                # 'বিবরণ' এখন পরে আসবে
                desc = st.text_input("বিবরণ লিখুন")
                amt = st.number_input("টাকার পরিমাণ", min_value=0, step=1)
            
            submit = st.form_submit_button("✅ নিশ্চিত করুন ও সেভ করুন")

    if submit:
        if desc == "" or amt == 0:
            st.warning("অনুগ্রহ করে বিবরণ এবং টাকার পরিমাণ সঠিক দিন।")
        else:
            new_data = pd.DataFrame([{"Date": date.strftime('%Y-%m-%d'), "Description": desc, "Category": cat, "Amount": amt}])
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(data=updated_df)
            st.success(f"সফলভাবে {cat} হিসেবে সেভ হয়েছে!")
            st.rerun()

    # হিসাবের তালিকা
    st.subheader("📊 হিসাবের তালিকা")
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by='Date', ascending=False)
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Excel ডাউনলোড করুন", data=csv, file_name="cash_book.csv", mime="text/csv")
    else:
        st.info("এখনো কোনো হিসাব যোগ করা হয়নি।")

    # লগআউট
    if st.sidebar.button("লগআউট"):
        st.session_state["logged_in"] = False
        st.rerun()

