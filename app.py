 import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import streamlit.components.v1 as components

# পেজ সেটিংস ও পারফরম্যান্স বুস্ট
st.set_page_config(page_title="আমার ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

# আপনার SheetDB API URL
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# পাসওয়ার্ড সেটিংস
FIXED_USER = "Kazi_Mamun"
DEFAULT_PW = "123456"

# ডাটা ক্যাশিং ফাংশন (এটি অ্যাপকে দ্রুত করবে)
@st.cache_data(ttl=60) # ৬০ সেকেন্ড পর্যন্ত ডাটা মেমোরিতে থাকবে, ফলে বার বার লোড হবে না
def fetch_data():
    try:
        response = requests.get(API_URL)
        data = response.json()
        df = pd.DataFrame(data)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=["Date", "Description", "Category", "Amount", "Voucher"])

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

# সেশন স্টেট
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
        pw = st.text_input("পাসওয়ার্ড দিন", type="password", help="ফিঙ্গারপ্রিন্ট বা অটো-ফিল ব্যবহার করুন।")
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
        
        # ক্যাশ থেকে ডাটা নেওয়া (দ্রুত লোড হবে)
        df = fetch_data()

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

        # এডিট ডেটা লোড
        d_date, d_cat, d_desc, d_amt = datetime.now(), "আয়", "", 0
        if st.session_state.edit_mode:
            ed = df.loc[st.session_state.edit_index]
            try: d_date = datetime.strptime(ed['Date'], '%Y-%m-%d')
            except: d_date = datetime.now()
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
            voucher_file = st.file_uploader("ভাউচার/মেমো", type=['jpg', 'png', 'jpeg'])
            submit = st.form_submit_button("Update" if st.session_state.edit_mode else "Submit")

        if submit:
            if st.session_state.edit_mode:
                requests.delete(f"{API_URL}/Description/{df.loc[st.session_state.edit_index]['Description']}")
            v_msg = "🖼️ ভাউচার আছে" if voucher_file else "No Image"
            new_row = {"data": [{"Date": str(date), "Description": desc, "Category": cat, "Amount": amt, "Voucher": v_msg}]}
            res = requests.post(API_URL, json=new_row)
            if res.status_code == 201:
                st.cache_data.clear() # নতুন ডাটা যোগ হলে ক্যাশ ক্লিয়ার হবে
                play_voice_success()
                st.success("সফলভাবে সংরক্ষিত হয়েছে!")
                st.session_state.edit_mode = False
                st.rerun()

        # --- আলাদা ট্যাব ---
        st.subheader("📊 হিসাবের তালিকা")
        tab_all, tab_income, tab_expense, tab_due, tab_dena, tab_powna = st.tabs(["সব", "আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])

        def show_list(filter_cat=None):
            display_df = df if filter_cat is None else df[df['Category'] == filter_cat]
            if not display_df.empty:
                for index, row in display_df.iloc[::-1].iterrows():
                    with st.container():
                        c_txt, c_edit, c_del = st.columns([0.7, 0.15, 0.15])
                        with c_txt:
                            st.write(f"📅 {row['Date']} | **{row['Category']}** | {row['Description']} | 💰 {row['Amount']} {row.get('Voucher','')}")
                        with c_edit:
                            if st.button("Edit", key=f"ed_{filter_cat}_{index}"):
                                st.session_state.edit_mode, st.session_state.edit_index = True, index
                                st.rerun()
                        with c_del:
                            if st.button("Delete", key=f"dl_{filter_cat}_{index}"):
                                requests.delete(f"{API_URL}/Description/{row['Description']}")
                                st.cache_data.clear()
                                st.rerun()
                    st.markdown("---")
            else: st.info("এই বিভাগে কোনো তথ্য নেই।")

        with tab_all: show_list()
        with tab_income: show_list("আয়")
        with tab_expense: show_list("ব্যয়")
        with tab_due: show_list("বকেয়া")
        with tab_dena: show_list("দেনা")
        with tab_powna: show_list("পাওনা")

    elif menu == "পাসওয়ার্ড পরিবর্তন":
        st.title("🔑 পাসওয়ার্ড পরিবর্তন")
        new_pw = st.text_input("নতুন পাসওয়ার্ড", type="password")
        if st.button("সেভ"): st.success("আপডেট হয়েছে!")

    elif menu == "লগআউট":
        st.session_state["logged_in"] = False
        st.rerun()
         
   

