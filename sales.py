import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. সেটিংস ও ডিজাইন
st.set_page_config(page_title="স্মার্ট রুট সেলস", layout="wide")

st.markdown("""
    <style>
    .shop-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #ddd; margin-bottom: 10px; cursor: pointer;
        transition: 0.3s; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .shop-card:hover { border-color: #6c5ce7; background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. ডাটা ফেচিং
@st.cache_data(ttl=5)
def get_all_data():
    try:
        res = requests.get(API_URL)
        df = pd.DataFrame(res.json())
        if not df.empty:
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0)
            df['Total'] = df['Price'] * df['Qty']
        return df
    except:
        return pd.DataFrame(columns=["Date", "Type", "Name", "Details", "Price", "Qty", "Total", "Route"])

df = get_all_data()

# ৩. রুট সিলেকশন
routes = ["রুট ১", "রুট ২", "রুট ৩", "রুট ৪", "রুট ৫", "রুট ৬"]
with st.sidebar:
    st.header("📍 কন্ট্রোল প্যানেল")
    active_route = st.selectbox("আপনার রুট নির্বাচন করুন", routes)
    st.divider()
    if st.button("🔄 ডাটা রিফ্রেশ করুন"):
        st.cache_data.clear()
        st.rerun()

# ডাটা ফিল্টার
all_shops = df[(df['Type'] == "দোকান যোগ (Shop)") & (df['Route'] == active_route)]['Name'].unique().tolist()
all_products = df[df['Type'] == "পণ্য যোগ (Product)"]

# ৪. মেইন কন্টেন্ট
st.title(f"🏬 {active_route} - এর দোকানসমূহ")

# দোকানগুলো গ্রিড আকারে দেখানো (৩ কলামে)
if not all_shops:
    st.info("এই রুটে কোনো দোকান যোগ করা নেই। সেটআপ ট্যাব থেকে দোকান যোগ করুন।")
else:
    cols = st.columns(3)
    for index, shop in enumerate(all_shops):
        col_idx = index % 3
        with cols[col_idx]:
            # প্রতিটি দোকানের জন্য একটি বাটন
            if st.button(f"🏪 {shop}", key=f"shop_{index}"):
                st.session_state.selected_shop = shop

# ৫. পপ-আপ বা এন্ট্রি ফর্ম (যখন দোকানে ক্লিক করা হবে)
if 'selected_shop' in st.session_state:
    st.divider()
    st.subheader(f"📝 {st.session_state.selected_shop} - এর জন্য অর্ডার নিন")
    
    with st.container():
        num_items = st.number_input("কয়টি পণ্য?", 1, 10, 4)
        order_rows = []
        
        # প্রোডাক্ট এন্ট্রি গ্রিড
        for i in range(int(num_items)):
            c1, c2 = st.columns([3, 1])
            p_name = c1.selectbox(f"পণ্য {i+1}", ["--সিলেক্ট--"] + all_products['Name'].tolist(), key=f"prod_{i}")
            p_qty = c2.number_input(f"পরিমাণ", min_value=1, key=f"qty_{i}")
            
            if p_name != "--সিলেক্ট--":
                p_price = all_products[all_products['Name'] == p_name]['Price'].values[0]
                order_rows.append({
                    "Date": str(datetime.now().date()), "Type": "অর্ডার (Order)", 
                    "Name": st.session_state.selected_shop, "Details": p_name, 
                    "Price": p_price, "Qty": p_qty, "Route": active_route
                })
        
        c_save, c_cancel = st.columns(2)
        if c_save.button("✅ অর্ডার সেভ করুন"):
            if order_rows:
                requests.post(API_URL, json={"data": order_rows})
                st.cache_data.clear()
                st.success("অর্ডার সফলভাবে সেভ হয়েছে!")
                del st.session_state.selected_shop
                st.rerun()
        
        if c_cancel.button("❌ বাতিল করুন"):
            del st.session_state.selected_shop
            st.rerun()

# ৬. নিচের দিকে সেটআপ এবং রিপোর্ট ট্যাব
st.divider()
tab_setup, tab_report = st.tabs(["⚙️ নতুন দোকান/পণ্য যোগ", "📊 মেমো ও সামারি"])

with tab_setup:
    with st.form("setup_form"):
        s_type = st.selectbox("টাইপ", ["দোকান যোগ (Shop)", "পণ্য যোগ (Product)"])
        s_name = st.text_input("নাম")
        s_price = st.number_input("দাম (পণ্য হলে)", min_value=0)
        if st.form_submit_button("সেভ"):
            requests.post(API_URL, json={"data": [{"Date":str(datetime.now().date()), "Type":s_type, "Name":s_name, "Price":s_price, "Route":active_route}]})
            st.cache_data.clear()
            st.rerun()

with tab_report:
    # এখানে আপনার মেমো দেখার কোড থাকবে
    view_shop = st.selectbox("মেমো দেখুন", ["--সিলেক্ট--"] + all_shops)
    if view_shop != "--সিলেক্ট--":
        shop_data = df[(df['Name'] == view_shop) & (df['Type'] == "অর্ডার (Order)") & (df['Date'] == str(datetime.now().date()))]
        st.table(shop_data[['Details', 'Price', 'Qty', 'Total']])
        st.write(f"**মোট: {shop_data['Total'].sum()} টাকা**")
