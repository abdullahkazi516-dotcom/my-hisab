import streamlit as st
import sqlite3
import pandas as pd

# ডাটাবেস কানেকশন
def init_db():
    conn = sqlite3.connect('business_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (p_name TEXT PRIMARY KEY, p_price REAL)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

st.sidebar.title("ম্যানেজমেন্ট")
menu = ["অর্ডার এন্ট্রি", "প্রোডাক্ট লিস্ট ও দাম সংশোধন", "নতুন দোকান যোগ"]
choice = st.sidebar.selectbox("মেনু", menu)

# --- প্রোডাক্ট লিস্ট ও দাম সংশোধন (আপনার সমস্যার সমাধান এখানে) ---
if choice == "প্রোডাক্ট লিস্ট ও দাম সংশোধন":
    st.subheader("🛠 পণ্যের তালিকা ও দাম আপডেট করুন")
    
    # বর্তমান প্রোডাক্টের তালিকা দেখা
    products_df = pd.read_sql_query("SELECT * FROM products", conn)
    
    if not products_df.empty:
        st.write("বর্তমান লিস্ট:")
        st.dataframe(products_df)
        
        st.write("---")
        st.write("#### দাম পরিবর্তন করুন")
        product_to_update = st.selectbox("কোন পণ্যের দাম বদলাবেন?", products_df['p_name'].tolist())
        new_price = st.number_input("নতুন সঠিক দাম লিখুন", min_value=0.0, step=0.5)
        
        if st.button("দাম আপডেট করুন ✅"):
            c.execute("UPDATE products SET p_price = ? WHERE p_name = ?", (new_price, product_to_update))
            conn.commit()
            st.success(f"সফলভাবে {product_to_update}-এর দাম আপডেট করা হয়েছে!")
            st.rerun() # পেজ রিফ্রেশ করে নতুন দাম দেখাবে
            
        if st.button("পণ্যটি ডিলিট করুন ❌"):
            c.execute("DELETE FROM products WHERE p_name = ?", (product_to_update,))
            conn.commit()
            st.warning(f"{product_to_update} লিস্ট থেকে মুছে ফেলা হয়েছে।")
            st.rerun()
    else:
        st.info("লিস্টে কোনো পণ্য নেই।")

# --- নতুন প্রোডাক্ট যোগ করার অপশন ---
    st.write("---")
    st.write("#### নতুন পণ্য যোগ করুন")
    with st.form("add_product"):
        new_p_name = st.text_input("পণ্যের নাম")
        new_p_price = st.number_input("দাম", min_value=0.0)
        if st.form_submit_button("সেভ"):
            if new_p_name:
                try:
                    c.execute("INSERT INTO products VALUES (?,?)", (new_p_name, new_p_price))
                    conn.commit()
                    st.success("যোগ হয়েছে!")
                    st.rerun()
                except:
                    st.error("এই পণ্যটি আগে থেকেই আছে।")

# বাকি মেনুগুলো (অর্ডার এন্ট্রি ইত্যাদি) আগের মতোই থাকবে...

conn.close()
