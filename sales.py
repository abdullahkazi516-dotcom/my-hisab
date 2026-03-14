import streamlit as st
import sqlite3
import pandas as pd

# ১. ডাটাবেস কানেকশন
def init_db():
    conn = sqlite3.connect('business_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS shops (shop_name TEXT PRIMARY KEY, route TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (p_name TEXT PRIMARY KEY, p_price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, total REAL, date TEXT)''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# সাইডবার মেনু
st.sidebar.title("মেইন মেনু")
menu = ["🏠 ড্যাশবোর্ড", "🛒 অর্ডার এন্ট্রি", "📦 প্রোডাক্ট ম্যানেজমেন্ট", "🏪 দোকান যোগ করুন"]
choice = st.sidebar.selectbox("অপশন বেছে নিন", menu)

# --- ২. ড্যাশবোর্ড (ডিফল্ট পেজ) ---
if choice == "🏠 ড্যাশবোর্ড":
    st.title("📊 বিজনেস ড্যাশবোর্ড")
    
    # ডাটা সংগ্রহ
    total_shops = pd.read_sql_query("SELECT COUNT(*) as count FROM shops", conn)['count'][0]
    total_prods = pd.read_sql_query("SELECT COUNT(*) as count FROM products", conn)['count'][0]
    total_sales = pd.read_sql_query("SELECT SUM(total) as total FROM orders", conn)['total'][0] or 0
    
    # ৩টি বক্স আকারে তথ্য দেখানো
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🏪 মোট দোকান")
        st.subheader(f"{total_shops} টি")
    with col2:
        st.success("📦 মোট প্রোডাক্ট")
        st.subheader(f"{total_prods} টি")
    with col3:
        st.warning("💰 মোট বিক্রি")
        st.subheader(f"{total_sales} টাকা")
    
    st.write("---")
    st.write("👈 মেনু থেকে কাজ শুরু করতে সাইডবার ব্যবহার করুন।")

# --- ৩. প্রোডাক্ট ম্যানেজমেন্ট (দাম সংশোধনসহ) ---
elif choice == "📦 প্রোডাক্ট ম্যানেজমেন্ট":
    st.subheader("🛠 প্রোডাক্ট লিস্ট ও দাম সংশোধন")
    products_df = pd.read_sql_query("SELECT * FROM products", conn)
    
    if not products_df.empty:
        st.dataframe(products_df, use_container_width=True)
        st.write("---")
        product_to_update = st.selectbox("পণ্য সিলেক্ট করুন", products_df['p_name'].tolist())
        new_price = st.number_input("সঠিক দাম লিখুন", min_value=0.0)
        
        if st.button("দাম আপডেট করুন ✅"):
            c.execute("UPDATE products SET p_price = ? WHERE p_name = ?", (new_price, product_to_update))
            conn.commit()
            st.success("দাম আপডেট হয়েছে!")
            st.rerun()
    
    # নতুন পণ্য যোগ
    st.write("---")
    with st.expander("➕ নতুন পণ্য যোগ করুন"):
        n_p = st.text_input("পণ্যের নাম")
        n_pr = st.number_input("দাম", key="new_pr")
        if st.button("সেভ"):
            c.execute("INSERT OR IGNORE INTO products VALUES (?,?)", (n_p, n_pr))
            conn.commit()
            st.rerun()

# বাকি কাজগুলো (অর্ডার এন্ট্রি ও দোকান যোগ) আগের কোড অনুযায়ী কাজ করবে...

conn.close()
