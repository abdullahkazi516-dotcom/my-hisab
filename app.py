import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# পেজ সেটিংস
st.set_page_config(page_title="আমার ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

# আপনার SheetDB API URL
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# --- পাসওয়ার্ড ম্যানেজমেন্ট ---
# ডিফল্ট পাসওয়ার্ড (আপনি চাইলে এখান থেকে পরিবর্তন করতে পারেন)
DEFAULT_USER = "kazi_Mamun"
DEFAULT_PW = "427054"

def check_password():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if not st.session_state["logged_in"]:
        st.title("🔐 লগইন করুন")
        user = st.text_input("ইউজারনেম")
        pw = st.text_input("পাসওয়ার্ড", type="password")
        if st.button("প্রবেশ করুন"):
            # এখানে আপনি আপনার পছন্দমতো ইউজার ও পাসওয়ার্ড সেট করে রাখতে পারেন
            if user == DEFAULT_USER and pw == DEFAULT_PW:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("ভুল ইউজারনেম বা পাসওয়ার্ড")
        return False
    return True

if check_password():
    # --- সাইডবার মেনু ---
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

        # ড্যাশবোর্ড
        if not df.empty:
            ti = df[df['Category'] == 'আয়']['Amount'].sum()
            te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
            td = df[df['Category'] == 'বকেয়া']['Amount'].sum()
            tp = df[df['Category'] == 'পাওনা']['Amount'].sum()
            tp_paid = df[df['Category'] == 'বকেয়া পরিশোধ']['Amount'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("মোট আয়", f"{ti}")
            col2.metric("মোট ব্যয়", f"-{te}")
            col3.metric("বর্তমান বকেয়া", f"{td - tp_paid}")
            col4.metric("মোট পাওনা", f"{tp}")
            st.info(f"💵 **বর্তমান নগদ জমা: {ti - te - tp_paid} টাকা**")

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
                    st.success("হিসাব সেভ হয়েছে!")
                    st.rerun()
                else:
                    st.error("সেভ হতে সমস্যা হয়েছে।")

        st.subheader("📊 হিসাবের তালিকা")
        if not df.empty:
            st.dataframe(df.iloc[::-1], use_container_width=True)

    elif menu == "পাসওয়ার্ড পরিবর্তন":
        st.title("🔑 পাসওয়ার্ড পরিবর্তন")
        st.warning("মনে রাখবেন: এখান থেকে পাসওয়ার্ড পরিবর্তন করলে তা শুধুমাত্র এই সেশনের জন্য কাজ করতে পারে যদি না আপনি কোড লেভেলে পরিবর্তন করেন।")
        
        new_pw = st.text_input("নতুন পাসওয়ার্ড দিন", type="password")
        confirm_pw = st.text_input("নতুন পাসওয়ার্ড পুনরায় দিন", type="password")
        
        if st.button("আপডেট করুন"):
            if new_pw == confirm_pw and new_pw != "":
                st.success("পাসওয়ার্ড সফলভাবে সেট হয়েছে! (স্থায়ীভাবে পরিবর্তনের জন্য GitHub কোডে DEFAULT_PW টি বদলে দিন)")
            else:
                st.error("পাসওয়ার্ড মিলেনি!")

    elif menu == "লগআউট":
        st.session_state["logged_in"] = False
        st.rerun()
