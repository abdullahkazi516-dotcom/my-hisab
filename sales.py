import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ১. সুপাবেস কানেকশন (এগুলো আপনার সেটিংস থেকে কপি করা)
SUPABASE_URL = "https://fmnnaspdmdnepeaeercb.supabase.co"
# এখানে আপনার কপি করা লম্বা anonymous API key-টি বসান
SUPABASE_KEY = "আপনার_কপি_করা_লম্বা_KEY_এখানে_দিন"

# সেশন স্টেট ঠিক করা (যাতে এরর না আসে)
if "edit_data" not in st.session_state:
    st.session_state.edit_data = None

# সুপাবেস ক্লায়েন্ট তৈরি
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ২. মেইন মেনু ও ডিজাইন
st.sidebar.title("🏢 বিজনেস ম্যানেজমেন্ট")
menu = ["🏠 ড্যাশবোর্ড", "📦 প্রোডাক্ট লিস্ট", "🏪 দোকান যোগ করুন"]
choice = st.sidebar.selectbox("মেনু বেছে নিন", menu)

# --- ৩. ড্যাশবোর্ড সেকশন ---
if choice == "🏠 ড্যাশবোর্ড":
    st.title("📊 বিজনেস ড্যাশবোর্ড")
    
    try:
        # ডাটাবেস থেকে তথ্য নিয়ে আসা
        shops_res = supabase.table("shops").select("*").execute()
        prods_res = supabase.table("products").select("*").execute()
        
        total_shops = len(shops_res.data) if shops_res.data else 0
        total_prods = len(prods_res.data) if prods_res.data else 0

        # মেত্রিক বা বক্স আকারে দেখানো
        col1, col2 = st.columns(2)
        col1.metric("🏪 মোট দোকান", f"{total_shops} টি")
        col2.metric("📦 মোট প্রোডাক্ট", f"{total_prods} টি")
        
        # ডাটা টেবিল দেখানো
        if shops_res.data:
            st.subheader("দোকানের তালিকা")
            df = pd.DataFrame(shops_res.data)
            st.dataframe(df[['shop_name', 'route']])
            
    except Exception as e:
        st.error("ডাটাবেস কানেকশনে সমস্যা হচ্ছে। টেবিল তৈরি করা আছে কি না চেক করুন।")

# --- ৪. প্রোডাক্ট লিস্ট সেকশন ---
elif choice == "📦 প্রোডাক্ট লিস্ট":
    st.subheader("🛠 নতুন প্রোডাক্ট যোগ করুন")
    with st.form("prod_form"):
        p_name = st.text_input("পণ্যের নাম")
        p_price = st.number_input("দাম", min_value=0.0)
        if st.form_submit_button("সেভ করুন"):
            if p_name:
                supabase.table("products").insert({"p_name": p_name, "p_price": p_price}).execute()
                st.success(f"{p_name} সফলভাবে সেভ হয়েছে!")
                st.rerun()

# --- ৫. দোকান যোগ করুন সেকশন ---
elif choice == "🏪 দোকান যোগ করুন":
    st.subheader("🏪 নতুন দোকান যোগ করুন")
    with st.form("shop_form"):
        s_name = st.text_input("দোকানের নাম")
        s_route = st.text_input("রুট বা এলাকা")
        if st.form_submit_button("দোকান সেভ করুন"):
            if s_name:
                supabase.table("shops").insert({"shop_name": s_name, "route": s_route}).execute()
                st.success(f"{s_name} দোকানটি যোগ করা হয়েছে!")
                st.rerun()
