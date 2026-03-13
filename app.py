import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# টাইটেল
st.title("💰 আমার ডিজিটাল ক্যাশ বুক")

# কানেকশন তৈরি
conn = st.connection("gsheets", type=GSheetsConnection)

# ডাটা পড়া (রিফ্রেশ করার জন্য ttl="0s")
df = conn.read(ttl="0s")

# নতুন হিসাব এন্ট্রি দেওয়ার ফর্ম
with st.form("entry_form"):
    date = st.date_input("তারিখ")
    desc = st.text_input("বিবরণ")
    cat = st.selectbox("ধরণ", ["আয়", "ব্যয়"])
    amt = st.number_input("টাকা", min_value=0)
    submit = st.form_submit_button("সেভ করুন")

if submit:
    # নতুন ডাটা তৈরি
    new_data = pd.DataFrame([{"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}])
    
    # আগের ডাটার সাথে নতুন ডাটা যোগ করা
    updated_df = pd.concat([df, new_data], ignore_index=True)
    
    # গুগল শিটে আপডেট করা
    conn.update(data=updated_df)
    
    st.success("হিসাব সফলভাবে সেভ হয়েছে!")
    st.rerun()

# নিচেই বর্তমান হিসাবের টেবিল দেখানো
st.subheader("হিসাবের তালিকা")
st.dataframe(df)
