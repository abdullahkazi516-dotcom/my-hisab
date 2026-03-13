import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# লগইন সেটিংস
USER_NAME = "admin" 
USER_PASSWORD = "123" 

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 লগইন করুন")
    user = st.text_input("ইউজারনেম")
    pw = st.text_input("পাসওয়ার্ড", type="password")
    if st.button("প্রবেশ করুন"):
        if user == USER_NAME and pw == USER_PASSWORD:
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("ভুল তথ্য!")
else:
    st.title("💸 আমার ডিজিটাল ক্যাশ বুক")
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="0s")

    with st.sidebar:
        st.header("নতুন এন্ট্রি")
        d = st.date_input("তারিখ", date.today())
        cat = st.selectbox("ধরণ", ["আয় (Income)", "ব্যয় (Expense)", "বকেয়া (Due)", "পাওনা (Receivable)"])
        desc = st.text_input("বিবরণ")
        amt = st.number_input("টাকা", min_value=0.0)
        if st.button("সেভ করুন"):
            new_row = pd.DataFrame([{"Date": str(d), "Description": desc, "Category": cat, "Amount": amt}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("সেভ হয়েছে!")
            st.rerun()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📩 স্টেটমেন্ট ডাউনলোড", csv, "report.csv", "text/csv")
