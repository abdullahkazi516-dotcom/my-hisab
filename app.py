import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও রঙিন ডিজাইন (CSS)
st.set_page_config(page_title="স্মার্ট ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    /* ক্যাটাগরি অনুযায়ী রঙ */
    .cat-income { color: #00c853; font-weight: bold; border-left: 5px solid #00c853; padding-left: 10px; }
    .cat-expense { color: #ff5252; font-weight: bold; border-left: 5px solid #ff5252; padding-left: 10px; }
    .cat-arrears { color: #ffd600; font-weight: bold; border-left: 5px solid #ffd600; padding-left: 10px; }
    .cat-debt { color: #ff9100; font-weight: bold; border-left: 5px solid #ff9100; padding-left: 10px; }
    .cat-receivable { color: #2979ff; font-weight: bold; border-left: 5px solid #2979ff; padding-left: 10px; }
    
    .call-btn {
        background-color: #00c853; color: white !important; padding: 5px 10px;
        text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 13px;
        display: inline-block; text-align: center; border: 1px solid #00a040;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 18px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# API লিঙ্ক
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. লগইন সিস্টেম
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("🔐 নিরাপদ প্রবেশ")
    password = st.text_input("পাসওয়ার্ড দিন", type="password", key="login_pass")
    if st.button("লগইন", key="login_btn"):
        if password == "427054": 
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!")
    st.stop()

# ৩. ডাটা লোড ফাংশন
@st.cache_data(ttl=5)
def get_all_data(sheet_name="Sheet1"):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet_name}")
        df = pd.DataFrame(res.json())
        return df.astype(str) if not df.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

df_main = get_all_data("Sheet1")

# ৪. ট্যাব সিস্টেম
tab_hishab, tab_plan, tab_exp, tab_phone = st.tabs(["💰 লেনদেন", "🗓️ পরিকল্পনা", "🌟 অভিজ্ঞতা", "📱 ফোনবুক"])

# --- ট্যাব ১: লেনদেন ---
with tab_hishab:
    st.subheader("📝 লেনদেন এন্ট্রি")
    edit_data = st.session_state.get('edit_data')
    categories = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    
    # ডিফল্ট ভ্যালু সেটআপ (ValueError প্রোটেকশন)
    d_val = datetime.now()
    cat_idx, desc_val, amt_val = 0, "", 0
    
    if edit_data:
        try:
            d_val = pd.to_datetime(edit_data['Date']).to_pydatetime()
            if edit_data['Category'] in categories: cat_idx = categories.index(edit_data['Category'])
            desc_val, amt_val = edit_data['Description'], int(float(edit_data['Amount']))
        except: pass

    with st.form("hishab_form_color", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date_in = col1.date_input("তারিখ", d_val, key="h_date")
        cat_in = col2.selectbox("বিভাগ", categories, index=cat_idx, key="h_cat")
        desc_in = st.text_input("বিবরণ", value=desc_val, key="h_desc")
        amt_in = st.number_input("পরিমাণ", min_value=0, value=amt_val, key="h_amt")
        
        if st.form_submit_button("সেভ করুন"):
            if desc_in:
                if edit_data: requests.delete(f"{API_URL}/Description/{edit_data['Description']}?sheet=Sheet1")
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [{"Date": str(date_in), "Description": desc_in, "Category": cat_in, "Amount": str(amt_in)}]})
                st.session_state.edit_data = None
                st.cache_data.clear(); st.rerun()

    st.divider()
    # রঙিন টেবিল ও ডাটা
    if not df_main.empty:
        h_tabs = st.tabs(categories)
        css_classes = ["cat-income", "cat-expense", "cat-arrears", "cat-debt", "cat-receivable"]
        
        for i, h_tab in enumerate(h_tabs):
            with h_tab:
                sub_df = df_main[df_main['Category'] == categories[i]]
                if not sub_df.empty:
                    st.markdown(f'<div class="{css_classes[i]}">{categories[i]} লিস্ট</div>', unsafe_allow_html=True)
                    st.dataframe(sub_df[['Date', 'Description', 'Amount']].iloc[::-1], use_container_width=True, hide_index=True)
                    total = pd.to_numeric(sub_df['Amount'], errors='coerce').sum()
                    st.info(f"মোট {categories[i]}: {total} ৳")
                    
                    with st.expander("এডিট বা ডিলিট"):
                        for idx, row in sub_df.iterrows():
                            c1, c2, c3 = st.columns([3, 1, 1])
                            c1.write(f"{row['Date']} - {row['Description']}")
                            if c2.button("📝", key=f"ed_{idx}_{i}_u"):
                                st.session_state.edit_data = row; st.rerun()
                            if c3.button("🗑️", key=f"del_{idx}_{i}_u"):
                                requests.delete(f"{API_URL}/Description/{row['Description']}?sheet=Sheet1")
                                st.cache_data.clear(); st.rerun()

# --- ট্যাব ৪: ফোনবুক (০ ফিক্সসহ) ---
with tab_phone:
    st.subheader("📱 ফোনবুক")
    edit_ph = st.session_state.get('edit_phone_data')
    with st.form("ph_form_color", clear_on_submit=True):
        n_in = st.text_input("নাম", value=edit_ph['Name'] if edit_ph else "", key="ph_name")
        m_in = st.text_input("মোবাইল", value=edit_ph['Mobile'] if edit_ph else "", key="ph_mob")
        note_in = st.text_input("নোট", value=edit_ph['Note'] if edit_ph else "", key="ph_note")
        if st.form_submit_button("সেভ"):
            if n_in and m_in:
                mob = str(m_in).strip()
                if not mob.startswith('0'): mob = '0' + mob
                if edit_ph: requests.delete(f"{API_URL}/id/{edit_ph['id']}?sheet=Phonebook")
                ph_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Phonebook", json={"data": [{"id": ph_id, "Name": n_in, "Mobile": mob, "Note": note_in}]})
                st.session_state.edit_phone_data = None
                st.cache_data.clear(); st.rerun()

    ph_df = get_all_data("Phonebook")
    if not ph_df.empty:
        ph_df['Mobile'] = ph_df['Mobile'].apply(lambda x: '0' + str(x) if (str(x).startswith('1') and len(str(x)) == 10) else str(x))
        for i, row in ph_df.iloc[::-1].iterrows():
            r1, r2, r3 = st.columns([3, 1.5, 2])
            r1.write(f"👤 {row['Name']}")
            r2.markdown(f'<a href="tel:{row["Mobile"]}" class="call-btn">📞 কল</a>', unsafe_allow_html=True)
            with r3:
                bb1, bb2 = st.columns(2)
                if bb1.button("📝", key=f"ph_ed_{i}_u"): st.session_state.edit_phone_data = row; st.rerun()
                if bb2.button("🗑️", key=f"ph_de_{i}_u"):
                    requests.delete(f"{API_URL}/id/{row['id']}?sheet=Phonebook")
                    st.cache_data.clear(); st.rerun()
            st.write("-" * 10)
