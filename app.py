import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ১. গুগল শিট কানেকশন (আপনার বিদ্যমান কানেকশনটি ব্যবহার করুন)
conn = st.connection("gsheets", type=GSheetsConnection)

# ২. ডাটা রিড করা
df = conn.read()

st.subheader("📊 হিসাবের তালিকা (বিভাগ অনুযায়ী)")

# ৩. ডাটা এডিটর (যেখানে এডিট ও ডিলিট করা যাবে)
# এটি আপনার আগের সব কলাম (তারিখ, ধরণ, বিবরণ, টাকা) প্রদর্শন করবে
edited_df = st.data_editor(
    df, 
    num_rows="dynamic", # এর মাধ্যমে আপনি নতুন সারি যোগ বা পুরনো সারি ডিলিট করতে পারবেন
    use_container_width=True,
    column_config={
        "Date": st.column_config.DateColumn("তারিখ"),
        "Category": "ধরণ",
        "Description": "বিবরণ",
        "Amount": st.column_config.NumberColumn("টাকা", format="%d ৳"),
    },
    key="cashbook_editor"
)

# ৪. এডিট বা ডিলিট করার পর ডাটা সেভ করার বাটন
if st.button("পরিবর্তনগুলো পাকাপাকিভাবে সেভ করুন"):
    try:
        # এডিট করা ডাটা গুগল শিটে আপডেট করা
        conn.update(data=edited_df)
        st.success("✅ অভিনন্দন! আপনার করা পরিবর্তনগুলো গুগল শিটে সেভ হয়েছে।")
        # পেজ রিফ্রেশ করা যাতে আপডেট ডাটা দেখায়
        st.rerun()
    except Exception as e:
        st.error(f"দুঃখিত, সেভ করার সময় সমস্যা হয়েছে: {e}")

# ৫. মোট হিসাব দেখানো (অটোমেটিক আপডেট হবে)
total_val = edited_df['Amount'].sum()
st.markdown(f"---")
st.markdown(f"### **মোট পরিমাণ: {total_val} টাকা**")
