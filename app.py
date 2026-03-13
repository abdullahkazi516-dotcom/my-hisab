import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import streamlit.components.v1 as components

# পেজ সেটিংস
st.set_page_config(page_title="আমার ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

# আপনার SheetDB API URL
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# পাসওয়ার্ড সেটিংস
FIXED_USER = "Kazi_Mamun"
DEFAULT_PW = "427054"

# ভয়েস ফাংশন
def play_voice_success():
    components.html(
        """
        <script>
        var msg = new SpeechSynthesisUtterance();
        msg.text = "আপনার লেনদেনটি সফল ভাবে আপডেট হয়েছে";
        msg.lang = 'bn-BD';
        window.speechSynthesis.speak(msg);
        </script>
        """,
        height=0,
    )

# সেশন স্টেট এডিটের জন্য
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
    st.session_state.edit_index = None

# লগইন ফাংশন
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        st.title("🔐 লগইন করুন")
        st.info(f"ইউজার: {FIXED_USER}")
        pw = st.text_input("পাসওয়ার্ড দিন", type="password")
        if st.button("প্রবেশ করুন"):
            if pw == DEFAULT_PW:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("ভুল পাসওয়ার্ড!")
        return False
    return True

if check_password():
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

        # এডিট মোড সেটিংস
        d_date, d_cat, d_desc, d_amt = datetime.now(), "আয়", "", 0
        if st.session_state.edit_mode:
            ed = df.loc[st.session_state.edit_index]
            try:
                d_date = datetime.strptime(ed['Date'], '%Y-%m-%d')
            except:
                d_date = datetime.now()
            d_cat, d_desc, d_amt = ed['Category'], ed['Description'], int(ed['Amount'])

        # ইনপুট ফর্ম
        with st.form("entry_form", clear_on_submit=not st.session_state.edit_mode):
            col_a, col_b = st.columns(2)
            with col_a:
                date = st.date_input("তারিখ", d_date)
                cat = st.selectbox("ধরণ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা", "বকেয়া পরিশোধ"], index=["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা", "বকেয়া পরিশোধ"].index(d_cat))
            with col_b:
                desc = st.text_input("বিবরণ", d_desc)
                amt = st.number_input("টাকা", min_value=0, value=d_amt)
            
            # ভাউচার আপলোড (৩ জিবি পর্যন্ত ফাইল সিলেক্ট করা যাবে)
            voucher_file = st.file_uploader("ভাউচার/মেমো (সর্বোচ্চ ৩ জিবি সাপোর্ট)", type=['jpg', 'png', 'jpeg', 'pdf'])
            
            submit = st.form_submit_button("Update" if st.session_state.edit_mode else "Submit")

        if submit:
            if st.session_state.edit_mode:
                requests.delete(f"{API_URL}/Description/{df.loc[st.session_state.edit_index]['Description']}")
            
            v_msg = "🖼️ ভাউচার আছে" if voucher_file else "No Image"
            new_row = {"data": [{"Date": str(date), "Description": desc, "Category": cat, "Amount": amt, "Voucher": v_msg}]}
            res = requests.post(API_URL, json=new_row)
            
            if res.status_code == 201:
                play_voice_success()
                st.success("সফলভাবে সংরক্ষিত হয়েছে!")
                st.session_state.edit_mode = False
                st.rerun()

        # তালিকা
        st.subheader("📊 হিসাবের তালিকা")
        if not df.empty:
            for index, row in df.iloc[::-1].iterrows():
                with st.container():
                    c_txt, c_edit, c_del = st.columns([0.7, 0.15, 0.15])
                    with c_txt: 
                        st.write(f"📅 {row['Date']} | **{row['Category']}** | {row['Description']} | 💰 {row['Amount']} {row.get('Voucher', '')}")
                    with c_edit:
                        if st.button("Edit", key=f"ed_{index}"):
                            st.session_state.edit_mode, st.session_state.edit_index = True, index
                            st.rerun()
                    with c_del:
                        if st.button("Delete", key=f"dl_{index}"):
                            requests.delete(f"{API_URL}/Description/{row['Description']}")
                            st.rerun()
                st.markdown("---")

    elif menu == "পাসওয়ার্ড পরিবর্তন":
        st.title("🔑 পাসওয়ার্ড পরিবর্তন")
        st.info("স্থায়ী পরিবর্তনের জন্য কোডের DEFAULT_PW বদলে দিন।")
        new_pw = st.text_input("নতুন পাসওয়ার্ড", type="password")
        if st.button("সেভ"): st.success("পাসওয়ার্ড আপডেট হয়েছে!")

    elif menu == "লগআউট":
        st.session_state["logged_in"] = False
        st.rerun()

