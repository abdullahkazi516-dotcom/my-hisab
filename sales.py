import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ১. ডাটাবেস সেটআপ
def init_db():
    conn = sqlite3.connect('business_inventory.db')
    c = conn.cursor()
    # দোকান টেবিল
    c.execute('''CREATE TABLE IF NOT EXISTS shops 
                 (shop_name TEXT PRIMARY KEY, route TEXT)''')
    # প্রোডাক্ট টেবিল (নতুন)
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (p_name TEXT PRIMARY KEY, p_price REAL)''')
    # অর্ডার টেবিল
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, shop_name TEXT, item_name TEXT, 
                  quantity REAL, total_price REAL, date TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

st.sidebar.title("মেনু কার্ড")
menu = ["অর্ডার এন্ট্রি", "প্রোডাক্ট যোগ করুন", "নতুন দোকান যোগ", "রিপোর্ট/লিস্ট"]
choice = st.sidebar.selectbox("অপশন বেছে নিন", menu)

# --- প্রোডাক্ট যোগ করার অংশ ---
if choice == "প্রোডাক্ট যোগ করুন":
    st.subheader("নতুন পণ্য তালিকাভুক্ত করুন")
    with st.form("product_form"):
        p_name = st.text_input("পণ্যের নাম *")
        p_price = st.number_input("পাইকারি মূল্য (প্রতি ইউনিট)", min_value=0.0)
        if st.form_submit_button("পণ্য সেভ করুন"):
            if p_name:
                try:
                    c.execute("INSERT INTO products VALUES (?,?)", (p_name, p_price))
                    conn.commit()
                    st.success(f"✅ {p_name} লিস্টে যোগ হয়েছে!")
                except:
                    st.error("এই পণ্যটি অলরেডি লিস্টে আছে।")

# --- নতুন দোকান যোগ ---
elif choice == "নতুন দোকান যোগ":
    st.subheader("নতুন দোকান যোগ করুন")
    with st.form("shop_form"):
        s_name = st.text_input("দোকানের নাম *")
        s_route = st.text_input("রুট/এলাকা")
        if st.form_submit_button("দোকান সেভ করুন"):
            if s_name:
                try:
                    c.execute("INSERT INTO shops VALUES (?,?)", (s_name, s_route))
                    conn.commit()
                    st.success("✅ দোকান সফলভাবে সেভ হয়েছে!")
                except:
                    st.error("এই নামের দোকান আগে থেকেই আছে।")

# --- অর্ডার এন্ট্রি (আপডেটেড) ---
elif choice == "অর্ডার এন্ট্রি":
    st.subheader("অর্ডার নিন")
    
    # ডাটাবেস থেকে দোকান ও প্রোডাক্টের লিস্ট আনা
    shops = pd.read_sql_query("SELECT shop_name FROM shops", conn)['shop_name'].tolist()
    products_df = pd.read_sql_query("SELECT * FROM products", conn)
    product_list = products_df['p_name'].tolist()
    
    if not shops or not product_list:
        st.warning("আগে 'দোকান' এবং 'প্রোডাক্ট' যোগ করে নিন।")
    else:
        with st.form("order_form"):
            selected_shop = st.selectbox("দোকান বেছে নিন", shops)
            selected_product = st.selectbox("পণ্য বেছে নিন", product_list)
            
            # সিলেক্ট করা প্রোডাক্টের দাম খুঁজে বের করা
            unit_price = products_df[products_df['p_name'] == selected_product]['p_price'].values[0]
            st.info(f"এই পণ্যের দাম: {unit_price} টাকা")
            
            qty = st.number_input("পরিমাণ (Quantity)", min_value=1.0, step=1.0)
            date = st.date_input("তারিখ", datetime.now())
            
            if st.form_submit_button("অর্ডার কনফার্ম"):
                total = unit_price * qty
                c.execute("INSERT INTO orders (shop_name, item_name, quantity, total_price, date) VALUES (?,?,?,?,?)",
                          (selected_shop, selected_product, qty, total, str(date)))
                conn.commit()
                st.success(f"✅ {total} টাকার অর্ডার সেভ হয়েছে!")

# --- রিপোর্ট দেখার অংশ ---
elif choice == "রিপোর্ট/লিস্ট":
    tab1, tab2, tab3 = st.tabs(["অর্ডার হিস্ট্রি", "পণ্য তালিকা", "দোকান তালিকা"])
    
    with tab1:
        orders = pd.read_sql_query("SELECT * FROM orders", conn)
        st.dataframe(orders)
        st.write(f"**সর্বমোট বিক্রি: {orders['total_price'].sum()} টাকা**")
    
    with tab2:
        prods = pd.read_sql_query("SELECT * FROM products", conn)
        st.table(prods)
        
    with tab3:
        shps = pd.read_sql_query("SELECT * FROM shops", conn)
        st.table(shps)

conn.close()
