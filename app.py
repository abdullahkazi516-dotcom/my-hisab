import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটআপ ও ডিজাইন
st.set_page_config(page_title="আমার হিসাব ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .main-balance { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #00c853; text-align: center; margin-bottom: 20px; }
    .total-box { padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 10px; background-color: #262730; }
    .cat-income { color: #00c853; } .cat-expense { color: #ff5252; }
    .call-btn { background-color: #00c853; color: white !important; padding: 5px 10px; text-decoration: none; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. শক্তিশালী ডাটা লোড ফাংশন
def get_all_data(sheet):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet}", timeout=10)
        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            return df.astype(str) if not df.empty else pd.DataFrame()
    except: pass
    return pd.DataFrame()

# ৩. ডাটা সংগ্রহ
df_main = get_all_data("Sheet1")
df_p = get_all_data("Plans")
df_e = get_all_data("Experiences")
df_ph = get_all_data("Phonebook")

# ৪. বর্তমান ব্যালেন্স হিসাব
st.markdown('<div class="main-balance">', unsafe_allow_html=True)
if not df_main.empty:
    df_main['Amount'] = pd.to_numeric(df_main['Amount'], errors='coerce').fillna(0)
    income = df_main[df_main['Category'] == "আয়"]['Amount'].sum()
    expense = df_main[df_main['Category'] == "ব্যয়"]['Amount'].sum()
    balance = income - expense
    st.markdown(f"### 💰 বর্তমান ব্যালেন্স: {balance} ৳")
    st.caption(f"মোট আয়: {income} | মোট ব্যয়: {expense}")
else:
    st.markdown("### 💰 বর্তমান ব্যালেন্স: 0 ৳")
st.markdown('</div>', unsafe_allow_html=True)

# ৫. ট্যাব সিস্টেম
t1, t2, t3, t4 = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

with t1:
    # এডিট লজিক (ValueError প্রোটেকশন)
    edit_data = st.session_state.get('edit_data')
    categories = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    d_v, c_i, ds_v, am_v = datetime.now(), 0, "", 0
    
    if edit_data:
        try:
            d_v = pd.to_datetime(edit_data.get('Date', datetime.now())).to_pydatetime()
            if edit_data.get('Category') in categories: c_i = categories.index(edit_data['Category'])
            ds_v = edit_data.get('Description', "")
            am_v = int(float(edit_data.get('Amount', 0)))
        except: pass

    with st.form("hishab_form_final", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_in = col1.date_input("তারিখ", d_v, key="date_in")
        cat_in = col2.selectbox("বিভাগ", categories, index=c_i, key="cat_in")
        desc_in = st.text_input("বিবরণ", value=ds_v, key="desc_in")
        amt_in = st.number_input("পরিমাণ", min_value=0, value=am_v, key="amt_in")
        if st.form_submit_button("সেভ করুন"):
            if desc_in:
                if edit_data: requests.delete(f"{API_URL}/Description/{edit_data['Description']}?sheet=Sheet1")
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(date_in), "Description": desc_in, "Category": cat_in, "Amount": str(amt_in)}]})
                st.session_state.edit_data = None
                st.rerun()

    # লিস্ট ও টোটাল প্রদর্শন
    if not df_main.empty:
        sub_tabs = st.tabs(categories)
        for i, s_tab in enumerate(sub_tabs):
            with s_tab:
                sub_df = df_main[df_main['Category'] == categories[i]]
                if not sub_df.empty:
                    st.dataframe(sub_df[['Date', 'Description', 'Amount']].iloc[::-1], use_container_width=True, hide_index=True)
                    total_cat = sub_df['Amount'].sum()
                    st.markdown(f'<div class="total-box">📊 মোট {categories[i]}: {total_cat} ৳</div>', unsafe_allow_html=True)
                    with st.expander("এডিট/ডিলিট"):
                        for idx, row in sub_df.iterrows():
                            c_a, c_b, c_c = st.columns([3, 1, 1])
                            c_a.write(f"{row['Description']} ({row['Amount']}৳)")
                            if c_b.button("📝", key=f"ed_{idx}_{i}"):
                                st.session_state.edit_data = row; st.rerun()
                            if c_c.button("🗑️", key=f"de_{idx}_{i}"):
                                requests.delete(f"{API_URL}/Description/{row['Description']}?sheet=Sheet1"); st.rerun()

with t2:
    st.subheader("🗓️ পরিকল্পনা")
    p_task = st.text_area("নতুন কাজ", key="p_in")
    if st.button("প্ল্যান সেভ"):
        if p_task:
            requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"id": str(datetime.now().timestamp()), "Date": str(datetime.now().date()), "Task": p_task}]})
            st.rerun()
    if not df_p.empty: st.dataframe(df_p[['Date', 'Task']].iloc[::-1], use_container_width=True, hide_index=True)

with t3:
    st.subheader("🌟 অভিজ্ঞতা")
    with st.form("exp_f"):
        g = st.text_input("ভালো")
        b = st.text_input("খারাপ")
        if st.form_submit_button("সেভ"):
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"Date": str(datetime.now().date()), "Good": g, "Bad": b}]})
            st.rerun()
    if not df_e.empty: st.dataframe(df_e.iloc[::-1], use_container_width=True, hide_index=True)

with t4:
    st.subheader("📱 ফোনবুক")
    if not df_ph.empty:
        for i, r in df_ph.iterrows():
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"👤 {r['Name']} ({r['Mobile']})")
            col_b.markdown(f'<a href="tel:{r["Mobile"]}" class="call-btn">📞 কল</a>', unsafe_allow_html=True)
            st.divider()
