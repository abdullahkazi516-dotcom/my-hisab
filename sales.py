import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও ডিজাইন
st.set_page_config(page_title="সেলস ও রুট ম্যানেজার", page_icon="🚚", layout="wide")

st.markdown("""
    <style>
    /* ইনপুট ঘরগুলোর বর্ডার কালার */
    div[data-baseweb="input"] { border: 2px solid #6c5ce7 !important; border-radius: 8px !important; }
    div[data-baseweb="select"] { border: 2px solid #fd7e14 !important; border-radius: 8px !important; }
    
    /* মেমো এবং সামারি বক্স ডিজাইন */
    .memo-card { border: 2px solid #333; padding: 15px; border-radius: 10px; background: white; margin-bottom: 15px; }
    .total-summary { background-color: #f1f3f4; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 18px; color: #1967d2; }
    </style>
    """, unsafe_allow_html=True)

# ২. আপনার নতুন গুগল শিটের API লিঙ্ক এখানে বসান
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7" # আপনার লিঙ্কটি এখানে দিয়ে দিন

# ৩. ডাটা ফেচিং ফাংশন
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

st.title("🚚 স্মার্ট সেলস ও রুট ট্র্যাকার")
df = get_all_data()

# ৪. রুট সিলেকশন (সাইডবারে)
routes = ["রুট ১", "রুট ২", "রুট ৩", "রুট ৪", "রুট ৫", "রুট ৬"]
with st.sidebar:
    st.header("📍 আজকের রুট")
    active_route = st.selectbox("কোন রুটে কাজ করবেন?", routes)
    st.info(f"বর্তমান রুট: {active_route}")
    
    st.divider()
    if st.button("ডাটা রিফ্রেশ করুন"):
        st.cache_data.clear()
        st.rerun()

# রুট অনুযায়ী ফিল্টার করা দোকান ও প্রোডাক্ট লিস্ট
all_shops = df[(df['Type'] == "দোকান যোগ (Shop)") & (df['Route'] == active_route)]['Name'].unique().tolist()
all_products = df[df['Type'] == "পণ্য যোগ (Product)"]

# ৫. অ্যাপের মূল কাজ (ট্যাব সিস্টেম)
tab_order, tab_setup, tab_report = st.tabs(["🛒 অর্ডার এন্ট্রি", "⚙️ সেটআপ (দোকান/পণ্য)", "📄 মেমো ও সামারি"])

# ট্যাব ১: অর্ডার এন্ট্রি (৪-৬টি পন্যের জন্য)
with tab_order:
    st.subheader(f"📝 {active_route} - এর নতুন অর্ডার")
    target_shop = st.selectbox("দোকান নির্বাচন করুন", ["--সিলেক্ট শপ--"] + all_shops)
    
    if target_shop != "--সিলেক্ট শপ--":
        num_items = st.slider("কয়টি পণ্য অর্ডার হবে?", 1, 10, 4)
        order_rows = []
        
        st.write("পণ্যের বিবরণ দিন:")
        for i in range(int(num_items)):
            c1, c2 = st.columns([3, 1])
            p_name = c1.selectbox(f"পণ্য {i+1}", ["--সিলেক্ট--"] + all_products['Name'].tolist(), key=f"p_{i}")
            p_qty = c2.number_input(f"পরিমাণ", min_value=1, key=f"q_{i}")
            
            if p_name != "--সিলেক্ট--":
                p_price = all_products[all_products['Name'] == p_name]['Price'].values[0]
                order_rows.append({
                    "Date": str(datetime.now().date()), "Type": "অর্ডার (Order)", "Name": target_shop,
                    "Details": p_name, "Price": p_price, "Qty": p_qty, "Route": active_route
                })
        
        if st.button("সবগুলো অর্ডার একসাথে সেভ করুন"):
            if order_rows:
                requests.post(API_URL, json={"data": order_

