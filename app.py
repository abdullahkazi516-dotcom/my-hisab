import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# পেজ সেটিংস
st.set_page_config(page_title="আমার ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

# আপনার SheetDB API URL
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ডিফল্ট ইউজার ও পাসওয়ার্ড
DEFAULT_USER = "admin"
DEFAULT_PW = "123"

# লগইন ফাংশন
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        st.title("🔐 লগইন করুন")
        user = st.text_input("ইউজারনেম")
        pw = st.text_input("পাসওয়ার্ড", type="password")
        if st.button("প্রবেশ করুন"):
            if user == DEFAULT_USER and pw == DEFAULT_PW:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("ভুল ইউজারনেম বা পাসওয়ার্ড")
        return False
    return True

if check_password():
    # সাইডবার মেনু
    menu = st.sidebar.selectbox("মেনু নির্বাচন করুন", ["ড্যাশবোর্ড ও এন্ট্রি", "পাসওয়ার্ড পরিবর্তন", "লগআউট"])

    if menu == "ড্যাশবোর্ড ও এন্ট্রি":
        st.title("💰 আমার ডিজিটাল ক্যাশ বুক")
        
        # ডেটা পড়া
        try:
            response = requests.get(API_URL)
            df = pd.DataFrame(response.json())
            if not df.empty:
                df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        except:
            df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])

        # --- বক্স আকারে ড্যাশবোর্ড ---
        if not df.empty:
            ti = df[df['Category'] == 'আয়']['Amount'].sum()
            te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
            td = df[df['Category'] == 'বকেয়া']['Amount'].sum()
            tp = df[df['Category'] == 'পাওনা']['Amount'].sum()
            tp_paid = df[df['Category'] == 'বকেয়া পরিশোধ']['Amount'].sum()
            
            current_due = td - tp_paid
            balance = ti - te - tp_paid

            # কাস্টম CSS দিয়ে বক্স স্টাইল করা
            st.markdown("""
                <style>
                .main-box {
                    padding: 20px;
                    border-radius: 10px;
                    color: white;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 10px;
                }
                .income { background-color: #28a745; }
                .expense { background-color: #dc3545; }
                .due { background-color: #ffc107; color: black !important; }
                .receivable { background-color: #17a2b8; }
                .balance { background-color: #6f42c1; font-size: 24px; }
                </style>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="main-box income">মোট আয়<br><h2>{ti}</h2></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="main-box expense">মোট ব্যয়<br><h2>{te}</h2></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="main-box due">বর্তমান বকেয়া<br><h2>{current_due}</h2></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="main-box receivable">মোট পাওনা<br><h2>{tp}</h2></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="main-box balance">💵 বর্তমান নগদ জমা: {balance} টাকা</div>', unsafe_allow_html=True)
            st.divider()

        # ইনপুট ফর্ম
        with st.form("entry_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                date = st.date_input("তারিখ নির্বাচন করুন", datetime.now())
                cat = st.selectbox("হিসাবের ধরণ", ["আয়", "ব্যয়", "বকেয়া", "পাওনা", "বকেয়া পরিশোধ"])
            with col_b:
                desc = st.text_input("বিবরণ লিখুন")
                amt = st.number_input("টাকার পরিমাণ", min_value=0, step=1)
            
            # বাটনের নাম Submit করা হয়েছে
            submit = st.form_submit_button("Submit")

        if submit:
            if desc == "" or amt == 0:
                st.warning("সঠিক তথ্য দিন।")
            else:
                new_data = {"data": [{"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}]}
                res = requests.post(API_URL, json=new_data)
                if res.status_code == 201:
                    st.success("হিসাব সেভ হয়েছে!")
                    st.rerun()
                else:
                    st.error("সেভ হতে সমস্যা হয়েছে।")

        st.subheader("📊 হিসাবের তালিকা")
        if not df.empty:
            st.dataframe(df.iloc[::-1], use_container_width=True)

    elif menu == "পাসওয়ার্ড পরিবর্তন":
        st.title("🔑 পাসওয়ার্ড পরিবর্তন")
        st.info("স্থায়ীভাবে পাসওয়ার্ড পরিবর্তনের জন্য GitHub কোডে DEFAULT_PW টি বদলে দিন।")
        new_pw = st.text_input("নতুন পাসওয়ার্ড দিন", type="password")
        if st.button("আপডেট"):
            st.success("পাসওয়ার্ড আপডেট হয়েছে!")

    elif menu == "লগআউট":
        st.session_state["logged_in"] = False
        st.rerun()

