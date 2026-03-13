import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# পেজ সেটিংস
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

# লগইন সফল হলে অ্যাপ চলবে
if check_password():
    st.title("💰 আমার ডিজিটাল ক্যাশ বুক")
    
    # কানেকশন তৈরি
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # ডাটা পড়া
    try:
        df = conn.read(ttl="0s")
    except:
        df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])

    # ড্যাশবোর্ড (হিসাব কিতাব)
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        
        total_income = df[df['Category'] == 'আয়']['Amount'].sum()
        total_expense = df[df['Category'] == 'ব্যয়']['Amount'].sum()
        total_due = df[df['Category'] == 'বকেয়া']['Amount'].sum()
        total_receivable = df[df['Category'] == 'পাওনা']['Amount'].sum()
        total_due_paid = df[df['Category'] == 'বকেয়া পরিশোধ']['Amount'].sum()
        
        # নিট বকেয়া = মোট বকেয়া - বকেয়া পরিশোধ
        current_due = total_due - total_due_paid
        # নগদ ব্যালেন্স = আয় - ব্যয় - বকেয়া পরিশোধ
        balance = total_income - total_expense - total_due_paid

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("মোট আয়", f"{total_income} টাকা")
        col2.metric("মোট ব্যয়", f"-{total_expense} টাকা")
        col3.metric("বর্তমান বকেয়া (দেনা)", f"{current_due} টাকা")
        col4.metric("মোট পাওনা", f"{total_receivable} টাকা")
        
        st.info(f"💵 **বর্তমান নগদ জমা: {balance} টাকা**")
        st.divider()

    # ডাটা ইনপুট ফর্ম (ধরণ আগে, বিবরণ পরে)
    with st.expander("➕ নতুন হিসাব যোগ করুন", expanded=True):
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("তারিখ নির্বাচন করুন", datetime.now())
                cat = st.selectbox("হিসাবের ধরণ", ["আয়", "ব্যয়", "বকেয়া", "পাওনা", "বকেয়া পরিশোধ"])
            with col2:
                desc = st.text_input("বিবরণ লিখুন")
                amt = st.number_input("টাকার পরিমাণ", min_value=0, step=1)
            
            submit = st.form_submit_button("✅ নিশ্চিত করুন ও সেভ করুন")

    if submit:
        if desc == "" or amt == 0:
            st.warning("অনুগ্রহ করে বিবরণ এবং টাকার পরিমাণ দিন।")
        else:
            new_data = pd.DataFrame([{"Date": date.strftime('%Y-%m-%d'), "Description": desc, "Category": cat, "Amount": amt}])
            updated_df = pd.concat([df, new_data], ignore_index=True)
            
            try:
                conn.update(data=updated_df)
                st.success(f"সফলভাবে '{cat}' হিসেবে সেভ হয়েছে!")
                st.rerun()
            except:
                st.error("সেভ হতে সমস্যা হয়েছে। আপনার Google Sheets-এ Everyone with the link > Editor পারমিশন আছে কি না চেক করুন।")

    # হিসাবের তালিকা
    st.subheader("📊 হিসাবের তালিকা")
    if not df.empty:
        st.dataframe(df.iloc[::-1], use_container_width=True) # নতুন হিসাব উপরে দেখাবে
    else:
        st.info("এখনো কোনো হিসাব যোগ করা হয়নি।")

    # লগআউট বাটন (সাইডবারে)
    if st.sidebar.button("লগআউট"):
        st.session_state["logged_in"] = False
        st.rerun()

