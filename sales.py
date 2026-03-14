import streamlit as st
import sqlite3
import pandas as pd

# ১. ডাটাবেস কানেকশন সেটআপ
def init_db():
    conn = sqlite3.connect('shops_data.db')
    c = conn.cursor()
    # দোকান টেবিল তৈরি (যদি না থাকে)
    c.execute('''CREATE TABLE IF NOT EXISTS shops 
                 (shop_name TEXT, owner_name TEXT, mobile TEXT, route TEXT, address TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# ২. অ্যাপের ইন্টারফেস
st.title("🏪 দোকান ব্যবস্থাপনা")

menu = ["দোকান যোগ করুন", "দোকানের তালিকা দেখুন"]
choice = st.sidebar.selectbox("মেনু", menu)

# --- দোকান যোগ করার অংশ ---
if choice == "দোকান যোগ করুন":
    st.subheader("নতুন দোকান যোগ করুন")
    
    with st.form(key='shop_form'):
        shop_name = st.text_input("দোকানের নাম *")
        owner_name = st.text_input("দোকানদারের নাম")
        mobile = st.text_input("মোবাইল নম্বর *")
        route = st.text_input("রুট")
        address = st.text_area("ঠিকানা")
        
        submit_button = st.form_submit_button(label='সেভ করুন')

    if submit_button:
        if shop_name and mobile:
            c.execute("INSERT INTO shops (shop_name, owner_name, mobile, route, address) VALUES (?,?,?,?,?)", 
                      (shop_name, owner_name, mobile, route, address))
            conn.commit()
            st.success(f"✅ {shop_name} সফলভাবে ডাটাবেসে যোগ হয়েছে!")
        else:
            st.warning("⚠️ দোকানের নাম এবং মোবাইল নম্বর অবশ্যই লিখুন।")

# --- তালিকা দেখার অংশ ---
elif choice == "দোকানের তালিকা দেখুন":
    st.subheader("সব দোকানের তালিকা")
    
    # ডাটাবেস থেকে তথ্য পড়া
    df = pd.read_sql_query("SELECT * FROM shops", conn)
    
    if not df.empty:
        st.dataframe(df) # সুন্দর টেবিল আকারে দেখাবে
        
        # এক্সেল হিসেবে ডাউনলোড করার সুবিধা
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="তালিকা ডাউনলোড করুন (CSV)",
            data=csv,
            file_name='shop_list.csv',
            mime='text/csv',
        )
    else:
        st.info("এখনো কোনো দোকান যোগ করা হয়নি।")

# ডাটাবেস কানেকশন বন্ধ করা
conn.close()
