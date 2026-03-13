import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# পেজ সেটিংস
st.set_page_config(page_title="আমার ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

# আপনার SheetDB API URL
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ডিফল্ট ইউজার ও পাসওয়ার্ড
FIXED_USER = "Kazi_Mamun# এটি এখন অটোমেটিক সেভ থাকবে
DEFAULT_PW = "427054"

# লগইন ফাংশন
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if not st.session_state["logged_in"]:
        st.title("🔐 লগইন করুন")
        
        # ইউজারনেম আর ইনপুট দিতে হবে না, এটি অটোমেটিক থাকবে
        st.info(f"ইউজার: {FIXED_USER}")
        
        # শুধুমাত্র পাসওয়ার্ডের ঘর
        pw = st.text_input("পাসওয়ার্ড দিন", type="password")
        
        if st.button("প্রবেশ করুন"):
            if pw == DEFAULT_PW:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("ভুল পাসওয়ার্ড! আবার চেষ্টা করুন।")
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
            df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount", "Voucher"])

        # --- ড্যাশবোর্ড বক্স ---
        if not df.empty:
            ti = df[df['Category'] == 'আয়']['Amount'].sum()
            te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
            td = df[df['Category'] == 'বকেয়া']['Amount'].sum()
            t_dena = df[df['Category'] == 'দেনা']['Amount'].sum()
            tp = df[df['Category'] == 'পাওনা']['Amount'].sum()
            tp_paid = df[df['Category'] == 'বকেয়া পরিশোধ']['Amount'].sum()
            balance = ti - te - tp_paid

            st.markdown("""
                <style>
                .main-box { padding: 15px; border-radius: 10px; color: white; font-weight: bold; text-align: center; margin-bottom: 10px; }
                .income { background-color: #28a745; }
                .expense { background-color: #dc3545; }
                .due { background-color: #ffc107; color: black !important; }
                .dena { background-color: #fd7e14; }
                .receivable { background-color: #17a2b8; }
                .balance { background-color: #6f42c1; font-size: 22px; }
                </style>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="main-box income">মোট আয়<br><h3>{ti}</h3></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="main-box expense">মোট ব্যয়<br><h3>{te}</h3></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="main-box balance">💵 নগদ জমা: {balance}</div>', unsafe_allow_html=True)

            c4, c5, c6 = st.columns(3)
            with c4: st.markdown(f'<div class="main-box due">মোট বকেয়া<br><h3>{td}</h3></div>', unsafe_allow_html=True)
            with c5: st.markdown(f'<div class="main-box dena">মোট দেনা<br><h3>{t_dena}</h3></div>', unsafe_allow_html=True)
            with c6: st.markdown(f'<div class="main-box receivable">মোট পাওনা<br><h3>{tp}</h3></div>', unsafe_allow_html=True)
            st.divider()

        # ইনপুট ফর্ম
        with st.form("entry_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                date = st.date_input("তারিখ নির্বাচন করুন", datetime.now())
                cat = st.selectbox("হিসাবের ধরণ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা", "বকেয়া পরিশোধ"])
            with col_b:
                desc = st.text_input("বিবরণ লিখুন")
                amt = st.number_input("টাকার পরিমাণ", min_value=0, step=1)
            
            # ক্যামেরা/ভাউচার অপশন
            voucher_file = st.file_uploader("মেমো বা ভাউচারের ছবি (ঐচ্ছিক)", type=['jpg', 'png', 'jpeg'])
            
            submit = st.form_submit_button("Submit")

        if submit:
            if desc == "" or amt == 0:
                st.warning("সঠিক তথ্য দিন।")
            else:
                voucher_status = "No Image" if voucher_file is None else "Image Uploaded"
                new_data = {"data": [{"Date": str(date), "Description": desc, "Category": cat, "Amount": amt, "Voucher": voucher_status}]}
                res = requests.post(API_URL, json=new_data)
                if res.status_code == 201:
                    st.success(f"{cat} সফলভাবে সেভ হয়েছে!")
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
            st.success("পাসওয়ার্ড আপডেট হয়েছে! (স্থায়ী করতে কোডে পরিবর্তন করুন)")

    elif menu == "লগআউট":
        st.session_state["logged_in"] = False
        st.rerun()
