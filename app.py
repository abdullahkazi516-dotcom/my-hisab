import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটআপ ও ডিজাইন (CSS)
st.set_page_config(page_title="স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .login-box { max-width: 400px; margin: auto; padding: 30px; border-radius: 15px; background-color: #1e1e1e; border: 1px solid #00c853; text-align: center; }
    .balance-card { background: linear-gradient(135deg, #1e1e1e, #252525); padding: 25px; border-radius: 15px; border: 2px solid #00c853; text-align: center; margin-bottom: 20px; }
    
    /* টোটাল হিসাবের ঘরের নতুন কালার (Blue Background) */
    .total-summary-box { 
        padding: 15px; 
        border-radius: 10px; 
        font-weight: bold; 
        background-color: #0d47a1; /* Deep Blue */
        color: white; 
        margin-top: 15px; 
        font-size: 18px;
        text-align: center;
        border: 1px solid #1e88e5;
    }
    
    .call-btn { background-color: #00c853; color: white !important; padding: 6px 12px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন সিস্টেম
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.header("🔐 লগইন")
    pass_input = st.text_input("পাসওয়ার্ড দিন", type="password", key="login_pass_field")
    if st.button("প্রবেশ করুন"):
        if pass_input == "427054":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ৩. শক্তিশালী ডাটা লোড ফাংশন
def get_safe_data(sheet):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet}", timeout=15)
        if res.status_code == 200:
            data = res.json()
            if data and isinstance(data, list):
                return pd.DataFrame(data).astype(str)
    except: pass
    return pd.DataFrame()

# ৪. মাই ব্যালেন্স (হাইড/শো অপশনসহ)
if "hide_bal" not in st.session_state:
    st.session_state["hide_bal"] = True

df_main = get_safe_data("Sheet1")

st.markdown('<div class="balance-card">', unsafe_allow_html=True)
if not df_main.empty:
    df_main['Amount'] = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    total_inc = df_main[df_main['Category'] == "আয়"]['Amount'].sum()
    total_exp = df_main[df_main['Category'] == "ব্যয়"]['Amount'].sum()
    current_bal = total_inc - total_exp
    
    c1, c2 = st.columns([4, 1])
    with c1:
        display_val = "••••••" if st.session_state["hide_bal"] else f"{current_bal} ৳"
        st.markdown(f"## 💰 বর্তমান ব্যালেন্স: {display_val}")
    with c2:
        if st.button("👁️" if st.session_state["hide_bal"] else "🕶️"):
            st.session_state["hide_bal"] = not st.session_state["hide_bal"]
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ৫. ট্যাব সিস্টেম
t_hishab, t_plan, t_exp, t_phone = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

# --- লেনদেন ট্যাব (এডিট ও কালার ফিক্স) ---
with t_hishab:
    categories = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    
    # এডিট ডাটা হ্যান্ডলিং
    edit_item = st.session_state.get('edit_item')
    d_v, c_i, ds_v, am_v = datetime.now(), 0, "", 0
    
    if edit_item is not None:
        try:
            temp_date = str(edit_item.get('Date', ''))
            d_v = pd.to_datetime(temp_date).to_pydatetime() if temp_date != 'nan' else datetime.now()
            ds_v = str(edit_item.get('Description', ''))
            am_v = int(float(edit_item.get('Amount', 0)))
            cat_name = edit_item.get('Category', 'আয়')
            if cat_name in categories: c_i = categories.index(cat_name)
        except: pass

    with st.form("hishab_form_final", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        date_in = col_a.date_input("তারিখ", d_v)
        cat_in = col_b.selectbox("বিভাগ", categories, index=c_i)
        desc_in = st.text_input("বিবরণ", value=ds_v)
        amt_in = st.number_input("পরিমাণ", min_value=0, value=am_v)
        
        if st.form_submit_button("সেভ করুন"):
            if desc_in:
                # এডিট মোডে থাকলে পুরনো ডাটা ডিলিট করা
                if edit_item:
                    requests.delete(f"{API_URL}/Description/{edit_item['Description']}?sheet=Sheet1")
                # নতুন বা আপডেট করা ডাটা সেভ
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(date_in), "Description": desc_in, "Category": cat_in, "Amount": str(amt_in)}]})
                st.session_state.edit_item = None
                st.rerun()

    if not df_main.empty:
        s_tabs = st.tabs(categories)
        for i, s_tab in enumerate(s_tabs):
            with s_tab:
                sub = df_main[df_main['Category'] == categories[i]]
                if not sub.empty:
                    st.dataframe(sub[['Date', 'Description', 'Amount']].iloc[::-1], use_container_width=True, hide_index=True)
                    # রঙিন টোটাল বক্স
                    cat_sum = pd.to_numeric(sub['Amount']).sum()
                    st.markdown(f'<div class="total-summary-box">📊 মোট {categories[i]} ফল: {cat_sum} ৳</div>', unsafe_allow_html=True)
                    
                    with st.expander("এডিট বা ডিলিট"):
                        for idx, row in sub.iterrows():
                            c1, c2, c3 = st.columns([3, 1, 1])
                            c1.write(f"{row['Description']} - {row['Amount']}৳")
                            if c2.button("📝 এডিট", key=f"e_btn_{idx}_{i}"):
                                st.session_state.edit_item = row
                                st.rerun()
                            if c3.button("🗑️", key=f"d_btn_{idx}_{i}"):
                                requests.delete(f"{API_URL}/Description/{row['Description']}?sheet=Sheet1")
                                st.rerun()

# --- অন্যান্য ট্যাব (পরিকল্পনা, অভিজ্ঞতা, ফোনবুক) ফিক্স ---
with t_plan:
    st.subheader("🗓️ পরিকল্পনা")
    p_text = st.text_area("নতুন প্ল্যান লিখুন")
    if st.button("প্ল্যান সেভ করুন"):
        if p_text:
            requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"id": str(datetime.now().timestamp()), "Date": str(datetime.now().date()), "Task": p_text}]})
            st.rerun()
    df_p = get_safe_data("Plans")
    if not df_p.empty: st.table(df_p[['Date', 'Task']].iloc[::-1])

with t_exp:
    st.subheader("🌟 অভিজ্ঞতা")
    with st.form("exp_form"):
        g_in = st.text_input("ভালো অভিজ্ঞতা")
        b_in = st.text_input("খারাপ অভিজ্ঞতা")
        if st.form_submit_button("সেভ"):
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"Date": str(datetime.now().date()), "Good": g_in, "Bad": b_in}]})
            st.rerun()
    df_e = get_safe_data("Experiences")
    if not df_e.empty: st.table(df_e.iloc[::-1])

with t_phone:
    st.subheader("📱 ফোনবুক")
    df_ph = get_safe_data("Phonebook")
    if not df_ph.empty:
        for i, r in df_ph.iterrows():
            col1, col2 = st.columns([3, 1])
            col1.write(f"👤 **{r['Name']}** - {r['Mobile']}")
            col2.markdown(f'<a href="tel:{r["Mobile"]}" class="call-btn">📞 কল</a>', unsafe_allow_html=True)
            st.divider()
