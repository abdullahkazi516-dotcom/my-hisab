import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. সেটিংস
st.set_page_config(page_title="স্মার্ট সেলস ট্র্যাকার", layout="wide")

# আপনার API লিঙ্ক
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. ডাটা লোড করার নিরাপদ ফাংশন
@st.cache_data(ttl=5)
def get_all_data():
    cols = ["Date", "Type", "Name", "Pack_Size", "Stock_Qty", "Price", "Route", "Owner", "Mobile", "Address", "Details", "Total"]
    try:
        res = requests.get(API_URL)
        data = res.json()
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(columns=cols)
        # কলাম চেক করা
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df
    except:
        return pd.DataFrame(columns=cols)

df = get_all_data()

# ৩. সাইডবার
routes = ["রুট ১", "রুট ২", "রুট ৩", "রুট ৪", "রুট ৫", "রুট ৬"]
with st.sidebar:
    st.header("📍 কন্ট্রোল প্যানেল")
    active_route = st.selectbox("রুট নির্বাচন করুন", routes)
    if st.button("🔄 ডাটা রিফ্রেশ"):
        st.cache_data.clear()
        st.rerun()

# ৪. ট্যাব সিস্টেম
tab_order, tab_setup = st.tabs(["🛒 অর্ডার এন্ট্রি", "⚙️ সেটআপ (দোকান/পণ্য)"])

with tab_setup:
    st.subheader("➕ নতুন দোকান বা পণ্য যোগ করুন")
    choice = st.radio("কি যোগ করবেন?", ["দোকান (Shop)", "পণ্য (Product)"], horizontal=True)
    
    with st.form("setup_form", clear_on_submit=True):
        if choice == "দোকান (Shop)":
            c1, c2 = st.columns(2)
            s_name = c1.text_input("দোকানের নাম*")
            s_owner = c1.text_input("দোকানদারের নাম")
            s_mob = c2.text_input("মোবাইল")
            s_addr = c2.text_area("ঠিকানা")
            if st.form_submit_button("সেভ করুন"):
                if s_name:
                    new_data = {"Date":str(datetime.now().date()), "Type":"দোকান যোগ (Shop)", "Name":s_name, "Owner":s_owner, "Mobile":s_mob, "Address":s_addr, "Route":active_route}
                    requests.post(API_URL, json={"data": [new_data]})
                    st.cache_data.clear()
                    st.success("দোকান সেভ হয়েছে! এবার অর্ডার এন্ট্রি ট্যাবে যান।")
                    st.rerun()
        else:
            c1, c2 = st.columns(2)
            p_name = c1.text_input("পণ্যের নাম*")
            p_pack = c1.text_input("প্যাক সাইজ")
            p_price = c2.number_input("দাম*", min_value=0)
            if st.form_submit_button("পণ্য সেভ করুন"):
                if p_name:
                    new_p = {"Date":str(datetime.now().date()), "Type":"পণ্য যোগ (Product)", "Name":p_name, "Pack_Size":p_pack, "Price":p_price}
                    requests.post(API_URL, json={"data": [new_p]})
                    st.cache_data.clear()
                    st.success("পণ্য সেভ হয়েছে!")
                    st.rerun()

with tab_order:
    all_shops = df[(df['Type'] == "দোকান যোগ (Shop)") & (df['Route'] == active_route)]
    if all_shops.empty:
        st.info("এই রুটে কোনো দোকান নেই। 'সেটআপ' ট্যাব থেকে আগে দোকান যোগ করুন।")
    else:
        st.subheader(f"🏬 {active_route} - এর দোকানসমূহ")
        cols = st.columns(3)
        for i, row in all_shops.reset_index().iterrows():
            if cols[i % 3].button(f"🏪 {row['Name']}"):
                st.session_state.selected_shop = row['Name']
        
        if 'selected_shop' in st.session_state:
            st.write(f"### অর্ডার নিচ্ছেন: {st.session_state.selected_shop}")
            # এখানে অর্ডারের বাকি অংশ...
            if st.button("বন্ধ করুন"):
                del st.session_state.selected_shop
                st.rerun()
