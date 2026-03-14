import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ১. ডাটাবেস সেটআপ
def init_db():
    conn = sqlite3.connect('business_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS shops (shop_name TEXT PRIMARY KEY, route TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (p_name TEXT PRIMARY KEY, p_price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT, shop_name TEXT, 
                  product_name TEXT, qty REAL, price REAL, total REAL, date TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# সাইডবার মেনু
menu = ["অর্ডার এন্ট্রি (মাল্টি SKU)", "প্রোডাক্ট যোগ করুন", "নতুন দোকান যোগ", "অর্ডার রিপোর্ট"]
choice = st.sidebar.selectbox("মেনু", menu)

# --- প্রোডাক্ট ও দোকান যোগ করার অংশ (সংক্ষিপ্ত রাখা হয়েছে) ---
if choice == "প্রোডাক্ট যোগ করুন":
    p_name = st.text_input("পণ্যের নাম")
    p_price = st.number_input("দাম", min_value=0.0)
    if st.button("সেভ পণ্য"):
        c.execute("INSERT OR IGNORE INTO products VALUES (?,?)", (p_name, p_price))
        conn.commit()
        st.success("পণ্য যোগ হয়েছে")

elif choice == "নতুন দোকান যোগ":
    s_name = st.text_input("দোকানের নাম")
    if st.button("সেভ দোকান"):
        c.execute("INSERT OR IGNORE INTO shops VALUES (?,?)", (s_name, ""))
        conn.commit()
        st.success("দোকান যোগ হয়েছে")

# --- মাল্টি SKU অর্ডার এন্ট্রি (প্রধান অংশ) ---
elif choice == "অর্ডার এন্ট্রি (মাল্টি SKU)":
    st.subheader("🛒 নতুন অর্ডার লিস্ট তৈরি করুন")
    
    shops = pd.read_sql_query("SELECT shop_name FROM shops", conn)['shop_name'].tolist()
    products_df = pd.read_sql_query("SELECT * FROM products", conn)
    
    if not shops or products_df.empty:
        st.warning("আগে দোকান এবং প্রোডাক্ট যোগ করুন।")
    else:
        # ১. দোকান ও তারিখ নির্বাচন
        col1, col2 = st.columns(2)
        selected_shop = col1.selectbox("দোকান বেছে নিন", shops)
        order_date = col2.date_input("অর্ডারের তারিখ", datetime.now())
        
        # সেশন স্টেট ব্যবহার করে আইটেম লিস্ট ধরে রাখা
        if 'cart' not in st.session_state:
            st.session_state.cart = []

        # ২. প্রোডাক্ট যোগ করার সেকশন
        st.write("---")
        c1, c2, c3 = st.columns([3, 1, 1])
        item = c1.selectbox("পণ্য সিলেক্ট করুন", products_df['p_name'].tolist())
        qty = c2.number_input("পরিমাণ", min_value=1.0, step=1.0)
        
        # সিলেক্ট করা আইটেমের দাম বের করা
        u_price = products_df[products_df['p_name'] == item]['p_price'].values[0]
        
        if st.button("কার্টে যোগ করুন ➕"):
            st.session_state.cart.append({
                'পণ্য': item,
                'পরিমাণ': qty,
                'দর': u_price,
                'মোট': qty * u_price
            })

        # ৩. কার্ট বা অর্ডার লিস্ট দেখানো
        if st.session_state.cart:
            st.write("### বর্তমান অর্ডার লিস্ট:")
            cart_df = pd.DataFrame(st.session_state.cart)
            st.table(cart_df)
            
            grand_total = cart_df['মোট'].sum()
            st.write(f"**সর্বমোট বিল: {grand_total} টাকা**")
            
            col_save, col_clear = st.columns(2)
            if col_save.button("অর্ডার কনফার্ম করুন ✅"):
                import uuid
                o_id = str(uuid.uuid4())[:8] # ইউনিক অর্ডার আইডি
                for row in st.session_state.cart:
                    c.execute("INSERT INTO orders (order_id, shop_name, product_name, qty, price, total, date) VALUES (?,?,?,?,?,?,?)",
                              (o_id, selected_shop, row['পণ্য'], row['পরিমাণ'], row['দর'], row['মোট'], str(order_date)))
                conn.commit()
                st.session_state.cart = [] # কার্ট খালি করা
                st.success("অর্ডার সফলভাবে ডাটাবেসে সেভ হয়েছে!")
            
            if col_clear.button("লিস্ট মুছুন ❌"):
                st.session_state.cart = []
                st.rerun()

# --- রিপোর্ট দেখার অংশ ---
elif choice == "অর্ডার রিপোর্ট":
    st.subheader("📋 সব অর্ডারের তালিকা")
    report_df = pd.read_sql_query("SELECT date, order_id, shop_name, product_name, qty, total FROM orders", conn)
    if not report_df.empty:
        st.dataframe(report_df)
    else:
        st.info("কোনো অর্ডার পাওয়া যায়নি।")

conn.close()
