import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# পেজ সেটআপ
st.set_page_config(page_title="আমার ডিজিটাল ক্যাশ বুক", page_icon="💰")

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

    # ডাটা ইনপুট ফর্ম
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("তারিখ")
            desc = st.text_input("বিবরণ (কার কাছে পাওনা বা কী বাবদ)")
        with col2:
            # এখানে 'বকেয়া পাওনা' অপশনটি যোগ করা হয়েছে
            cat = st.selectbox("ধরণ", ["আয়", "ব্যয়", "বকেয়া পাওনা"])
            amt = st.number_input("টাকা", min_value=0)
        
        submit = st.form_submit_button("হিসাব সেভ করুন")

    if submit:
        # নতুন ডাটা তৈরি
        new_data = pd.DataFrame([{"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}])
        
        # আগের ডাটার সাথে নতুন ডাটা যোগ করা
        updated_df = pd.concat([df, new_data], ignore_index=True)
        
        # গুগল শিটে আপডেট করা
        conn.update(data=updated_df)
        
        st.success(f"{cat} হিসেবে সফলভাবে সেভ হয়েছে!")
        st.rerun()

    # হিসাবের তালিকা দেখানো
    st.subheader("📊 আপনার বর্তমান হিসাব তালিকা")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("এখনো কোনো হিসাব যোগ করা হয়নি।")

    # লগআউট বাটন
    if st.button("লগআউট"):
        st.session_state["logged_in"] = False
        st.rerun()
