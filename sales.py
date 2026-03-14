import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও ডিজাইন
st.set_page_config(page_title="স্মার্ট সেলস ট্র্যাকার", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    div[data-baseweb="input"] { border: 2px solid #6c5ce7 !important; border-radius: 8px !important; }
    div[data-baseweb="select"] { border: 2px solid #fd7e14 !important; border-radius: 8px !important; }
    .memo-card { border: 2px solid #333; padding: 15px; border-radius: 10px; background: white; margin-bottom: 15px; }
    .total-summary { background-color: #f1f3f4; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 18px; color: #1967d2; }
    </style>
    """, unsafe_allow_html=True)

# ২. আপনার API লিঙ্কটি সেট করা হলো
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ৩. ডাটা ফেচিং ফাংশন
@st.cache_data(ttl=5)
def get_all_data():
    try:
        res = requests.get(API_URL)
        df = pd.DataFrame(res.json())
        if not df.empty:
            # ডাটা টাইপ ঠিক করা
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0)
            df['Total'] = df['Price'] * df['Qty']
        return df
    except:
        return pd.DataFrame(columns=["Date", "Type", "Name", "Details", "Price", "Qty", "Total", "Route"])

st.title("🚚 রুট ভিত্তিক সেলস ও অর্ডার ম্যানেজার")
df = get_all_data()

# ৪. রুট সিলেকশন (সাইডবারে)
routes = ["রুট ১", "রুট ২", "রুট ৩", "রুট ৪", "রুট ৫", "রুট ৬"]
with st.sidebar:
    st.header("📍 আজকের টার্গেট")
    active_route = st.selectbox("আজ কোন রুটে কাজ করবেন?", routes)
    st.info(f"বর্তমান রুট: {active_route}")
    
    if st.button("ডাটা রিফ্রেশ করুন"):
        st.cache_data.clear()
        st.rerun()

# রুট অনুযায়ী ফিল্টার করা ডাটা
all_shops = df[(df['Type'] == "দোকান যোগ (Shop)") & (df['Route'] == active_route)]['Name'].unique().tolist()
all_products = df[df['Type'] == "পণ্য যোগ (Product)"]

# ৫. ট্যাব সিস্টেম
tab_order, tab_setup, tab_report = st.tabs(["🛒 অর্ডার এন্ট্রি", "⚙️ সেটআপ", "📄 মেমো ও সামারি"])

# ট্যাব ১: অর্ডার এন্ট্রি
with tab_order:
    st.subheader(f"📝 {active_route} - এর অর্ডার")
    target_shop = st.selectbox("দোকান নির্বাচন করুন", ["--সিলেক্ট শপ--"] + all_shops)
    
    if target_shop != "--সিলেক্ট শপ--":
        num_items = st.slider("কয়টি পণ্য অর্ডার হবে?", 1, 10, 4)
        order_rows = []
        
        for i in range(int(num_items)):
            c1, c2 = st.columns([3, 1])
            p_name = c1.selectbox(f"পণ্য {i+1}", ["--সিলেক্ট--"] + all_products['Name'].tolist(), key=f"p_{i}")
            p_qty = c2.number_input(f"পরিমাণ", min_value=1, key=f"q_{i}")
            
            if p_name != "--সিলেক্ট--":
                # ওই পণ্যের দাম ডাটাবেস থেকে খুঁজে নেওয়া
                p_price = all_products[all_products['Name'] == p_name]['Price'].values[0]
                order_rows.append({
                    "Date": str(datetime.now().date()), "Type": "অर्डर (Order)", "Name": target_shop,
                    "Details": p_name, "Price": p_price, "Qty": p_qty, "Route": active_route
                })
        
        if st.button("সবগুলো অর্ডার সেভ করুন"):
            if order_rows:
                requests.post(API_URL, json={"data": order_rows})
                st.cache_data.clear()
                st.success("সফলভাবে সেভ হয়েছে!")
                st.rerun()

# ট্যাব ২: সেটআপ (দোকান ও পণ্য যোগ)
with tab_setup:
    st.subheader("➕ নতুন ডাটা যোগ")
    with st.form("setup_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        s_type = c1.selectbox("টাইপ", ["দোকান যোগ (Shop)", "পণ্য যোগ (Product)"])
        s_name = c1.text_input("নাম")
        s_price = c2.number_input("দাম (পণ্য হলে)", min_value=0)
        s_route = c2.selectbox("রুট", routes, index=routes.index(active_route))
        
        if st.form_submit_button("সংরক্ষণ"):
            if s_name:
                new_entry = {"Date": str(datetime.now().date()), "Type": s_type, "Name": s_name, "Price": s_price, "Route": s_route}
                requests.post(API_URL, json={"data": [new_entry]})
                st.cache_data.clear()
                st.success(f"{s_name} যোগ হয়েছে!")
                st.rerun()

# ট্যাব ৩: রিপোর্ট
with tab_report:
    st.subheader("📊 মেমো জেনারেটর")
    memo_shop = st.selectbox("দোকান নির্বাচন", ["--সিলেক্ট--"] + all_shops)
    if memo_shop != "--সিলেক্ট--":
        today = str(datetime.now().date())
        shop_orders = df[(df['Name'] == memo_shop) & (df['Type'] == "অর্ডার (Order)") & (df['Date'] == today)]
        
        if not shop_orders.empty:
            st.markdown(f'<div class="memo-card"><h3>মেমো: {memo_shop}</h3><p>তারিখ: {today}</p></div>', unsafe_allow_html=True)
            st.table(shop_orders[['Details', 'Price', 'Qty', 'Total']])
            st.markdown(f'<div class="total-summary">মোট: {shop_orders["Total"].sum()} টাকা</div>', unsafe_allow_html=True)
        else:
            st.warning("আজ কোনো অর্ডার নেই।")

# ৬. ডাটা ডিলিট
with st.expander("🗑️ ডিলিট অপশন"):
    st.dataframe(df.iloc[::-1], use_container_width=True)
    del_val = st.text_input("ডিলিট করতে নাম লিখুন")
    if st.button("কনফার্ম ডিলিট"):
        requests.delete(f"{API_URL}/Name/{del_val}")
        st.cache_data.clear()
        st.rerun()
