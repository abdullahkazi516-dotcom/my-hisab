import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ১. টাইটেল (সবার আগে দেখাবে)
st.markdown("### 💰 আমার ডিজিটাল ক্যাশ বুক")

# ২. কানেকশন সেটআপ
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# ৩. উপরের অংশ: নতুন লেনদেন যোগ করার ফর্ম
with st.container():
    st.markdown("#### ➕ নতুন লেনদেন যোগ করুন")
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 তারিখ")
        category = st.selectbox("📂 ধরণ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
    with col2:
        details = st.text_input("📝 বিবরণ", placeholder="যেমন: দোকানের বাকি")
        amount = st.number_input("💰 টাকা", min_value=0, step=1)
    
    if st.button("Submit"):
        # এখানে আপনার নতুন ডাটা সেভ করার পুরনো কোডটি বসিয়ে দিন
        st.success("নতুন ডাটা যোগ হয়েছে!")

st.divider() # একটি লম্বা দাগ দিয়ে আলাদা করা

# ৪. নিচের অংশ: আপনার সেই এডিট টেবিল
st.subheader("📊 হিসাবের তালিকা (বিভাগ অনুযায়ী)")

edited_df = st.data_editor(
    df,
    num_rows="dynamic", 
    use_container_width=True,
    key="main_table_editor"
)

# ৫. সেভ বাটন
if st.button("পরিবর্তনগুলো সেভ করুন"):
    conn.update(data=edited_df)
    st.success("✅ সব পরিবর্তন গুগল শিটে সেভ হয়েছে!")
    st.rerun()

# ৬. মোট টাকার হিসাব (একদম নিচে)
if not edited_df.empty:
    # এখানে 'Amount' বা 'টাকা' কলামের নাম আপনার শিট অনুযায়ী দিবেন
    total_val = edited_df['Amount'].sum() 
    st.markdown(f"## **মোট পরিমাণ: {total_val} টাকা**")
