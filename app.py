import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# গুগল শিট কানেকশন
conn = st.connection("gsheets", type=GSheetsConnection)

# ডাটা পড়া এবং পরিষ্কার করা
raw_data = conn.read()
df = pd.DataFrame(raw_data) # ডাটাকে ডাটাফ্রেমে রূপান্তর

st.subheader("📊 হিসাবের তালিকা (বিভাগ অনুযায়ী)")

# এডিট করার সিস্টেম (সহজভাবে)
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key="cashbook_editor_simple"
)

# সেভ বাটন
if st.button("পরিবর্তনগুলো সেভ করুন"):
    try:
        # গুগল শিট আপডেট
        conn.update(data=edited_df)
        st.success("✅ সফলভাবে সেভ হয়েছে!")
        st.rerun()
    except Exception as e:
        st.error(f"ভুল হয়েছে: {e}")

# মোট হিসাব
if not edited_df.empty:
    total_val = edited_df['Amount'].sum()
    st.markdown(f"### **মোট পরিমাণ: {total_val} টাকা**")
