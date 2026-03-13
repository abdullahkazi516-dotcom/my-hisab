import streamlit as st
import pandas as pd
from datetime import datetime

# পেজ সেটিংস
st.set_page_config(page_title="আমার ডিজিটাল ক্যাশ বুক", page_icon="💰")

# কানেকশন (সরাসরি আপনার শিট আইডি ব্যবহার করা হয়েছে)
SHEET_ID = "191eFwqQGyYT4Ip67pa_hjTZthWLExugah63UAqQ44Ag"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

st.title("💰 আমার ডিজিটাল ক্যাশ বুক")

# ডাটা ইনপুট ফর্ম
with st.expander("➕ নতুন হিসাব যোগ করুন", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        date = st.date_input("তারিখ", datetime.now())
        cat = st.selectbox("ধরণ", ["আয়", "ব্যয়", "বকেয়া", "পাওনা", "বকেয়া পরিশোধ"])
        desc = st.text_input("বিবরণ")
        amt = st.number_input("টাকার পরিমাণ", min_value=0, step=1)
        submit = st.form_submit_button("✅ সেভ করুন")

if submit:
    # ডাটা সেভ করার জন্য আগের কানেকশনটি ব্যবহার করবে
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        # বর্তমান ডাটা পড়া
        existing_data = conn.read(ttl="0s")
        # নতুন ডাটা তৈরি
        new_row = pd.DataFrame([{"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}])
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        # শিট আপডেট
        conn.update(data=updated_df)
        st.success("হিসাব সফলভাবে সেভ হয়েছে!")
        st.rerun()
    except Exception as e:
        st.error("সেভ হচ্ছে না। অনুগ্রহ করে নিশ্চিত করুন গুগল শিটটি 'Editor' মুডে শেয়ার করা আছে।")

# ডাটা টেবিল দেখানো
try:
    df = pd.read_csv(CSV_URL)
    st.subheader("📊 বর্তমান হিসাবের তালিকা")
    st.dataframe(df.iloc[::-1], use_container_width=True)
except:
    st.info("এখনো কোনো ডাটা নেই।")
