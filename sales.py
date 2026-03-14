import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস
st.set_page_config(page_title="স্মার্ট সেলস ট্র্যাকার", layout="wide")

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. ডাটা ফেচিং
@st.cache_data(ttl=5)
def get_all_data():
    try:
        res = requests.get(API_URL)
        df = pd.DataFrame(res.json())
        return df
    except:
        return pd.DataFrame()

df = get_all_data()

# ৩. সাইডবার (রুট নির্বাচন)
routes = ["রুট ১", "রুট ২", "রুট ৩", "রুট ৪", "রুট ৫", "রুট ৬"]
with st.sidebar:
    st.header("📍 কন্ট্রোল প্যানেল")
    active_route = st.selectbox("আপনার রুট নির্বাচন করুন", routes)
    if st.button("🔄 ডাটা রিফ্রেশ করুন"):
        st.cache_data.clear()
        st.rerun()

# ৪. ট্যাব সিস্টেম
tab_order, tab_setup, tab_report = st.tabs(["🛒 অর্ডার এন্ট্রি", "⚙️ সেটআপ (দোকান/পণ্য)", "📄 রিপোর্ট"])

# --- ট্যাব ২: নতুন প্রোডাক্ট ও দোকান এন্ট্রি ---
with tab_setup:
    st.subheader("➕ নতুন ডাটাবেস তৈরি")
    choice = st.radio("কি যোগ করতে চান?", ["পণ্য (Product)", "দোকান (Shop)"], horizontal=True)
    
    with st.form("setup_form", clear_on_submit=True):
        if choice == "পণ্য (Product)":
            col1, col2 = st.columns(2)
            p_name = col1.text_input("পণ্যের নাম*")
            p_pack = col1.text_input("প্যাক সাইজ (যেমন: ৫০০ গ্রাম / ১ কেজি)")
            p_stock = col2.number_input("মজুদ পরিমাণ (Stock)", min_value=0)
            p_price = col2.number_input("টাকা (পাইকারি দাম)*", min_value=0)
            
            if st.form_submit_button("পণ্য সেভ করুন"):
                if p_name:
                    new_prod = {
                        "Date": str(datetime.now().date()),
                        "Type": "পণ্য যোগ (Product)",
                        "Name": p_name,
                        "Pack_Size": p_pack,
                        "Stock_Qty": p_stock,
                        "Price": p_price
                    }
                    requests.post(API_URL, json={"data": [new_prod]})
                    st.cache_data.clear()
                    st.success(f"{p_name} সফলভাবে যোগ হয়েছে!")
                    st.rerun()
        
        else:
            col1, col2 = st.columns(2)
            shop_name = col1.text_input("দোকানের নাম*")
            owner_name = col1.text_input("দোকানদারের নাম")
            mobile = col2.text_input("মোবাইল নম্বর")
            address = col2.text_area("ঠিকানা")
            
            if st.form_submit_button("দোকান সেভ করুন"):
                if shop_name:
                    new_shop = {
                        "Date": str(datetime.now().date()),
                        "Type": "দোকান যোগ (Shop)",
                        "Name": shop_name,
                        "Owner": owner_name,
                        "Mobile": mobile,
                        "Address": address,
                        "Route": active_route
                    }
                    requests.post(API_URL, json={"data": [new_shop]})
                    st.cache_data.clear()
                    st.success(f"{shop_name} যোগ হয়েছে!")
                    st.rerun()

# --- ট্যাব ১: অর্ডার এন্ট্রি ---
with tab_order:
    if not df.empty:
        all_shops = df[(df['Type'] == "দোকান যোগ (Shop)") & (df['Route'] == active_route)]
        all_products = df[df['Type'] == "পণ্য যোগ (Product)"]
        
        st.subheader(f"🏬 {active_route} - এর দোকানসমূহ")
        if not all_shops.empty:
            cols = st.columns(3)
            for index, row in all_shops.iterrows():
                with cols[index % 3]:
                    if st.button(f"🏪 {row['Name']}\n({row['Owner']})", key=f"btn_{index}"):
                        st.session_state.selected_shop = row['Name']
            
            if 'selected_shop' in st.session_state:
                st.divider()
                st.subheader(f"📝 অর্ডার: {st.session_state.selected_shop}")
                
                num_items = st.number_input("কয়টি পণ্য?", 1, 10, 4)
                order_rows = []
                for i in range(int(num_items)):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    # প্রোডাক্ট লিস্টে এখন নাম ও প্যাক সাইজ একসাথে দেখাবে
                    prod_list = all_products.apply(lambda x: f"{x['Name']} ({x['Pack_Size']})", axis=1).tolist()
                    p_select = c1.selectbox(f"পণ্য {i+1}", ["--সিলেক্ট--"] + prod_list, key=f"p_{i}")
                    p_qty = c2.number_input(f"পরিমাণ", min_value=1, key=f"q_{i}")
                    
                    if p_select != "--সিলেক্ট--":
                        # সঠিক প্রাইস খুঁজে বের করা
                        original_name = p_select.split(" (")[0]
                        price = all_products[all_products['Name'] == original_name]['Price'].values[0]
                        c3.write(f"দাম: {price} ৳")
                        
                        order_rows.append({
                            "Date": str(datetime.now().date()), "Type": "অর্ডার (Order)", 
                            "Name": st.session_state.selected_shop, "Details": p_select, 
                            "Price": price, "Qty": p_qty, "Route": active_route
                        })
                
                if st.button("✅ অর্ডার কনফার্ম"):
                    requests.post(API_URL, json={"data": order_rows})
                    st.cache_data.clear()
                    st.success("অর্ডার সেভ হয়েছে!")
                    del st.session_state.selected_shop
                    st.rerun()
