import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ১. পেজ সেটিংস ও ডিজাইন
st.set_page_config(page_title="পার্সোনাল ড্যাশবোর্ড", layout="wide")

st.markdown("""
    <style>
    .total-summary { background-color: #f1f3f4; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 18px; color: #1967d2; margin: 10px 0; }
    .exp-card-good { border-left: 5px solid #28a745; background-color: #f8fff9; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .exp-card-bad { border-left: 5px solid #dc3545; background-color: #fff8f8; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .plan-card { border: 1px solid #ddd; padding: 15px; border-radius: 8px; background-color: #ffffff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# আপনার API লিঙ্ক
API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"

# ২. ডাটা লোড করার ফাংশন
@st.cache_data(ttl=5)
def get_data(sheet_name="Sheet1"):
    try:
        res = requests.get(f"{API_URL}?sheet={sheet_name}")
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

# ৩. মেইন ট্যাব সিস্টেম
tab_hishab, tab_plan, tab_exp = st.tabs(["💰 লেনদেন হিসাব", "🗓️ কর্ম পরিকল্পনা", "🌟 আজকের অভিজ্ঞতা"])

# --- ট্যাব ১: লেনদেন হিসাব (আপনার কোড অনুযায়ী) ---
with tab_hishab:
    df = get_data("Sheet1")
    st.subheader("📝 নতুন লেনদেন এন্ট্রি")
    
    edit_mode = st.session_state.get('edit_data')
    
    with st.form("hishab_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date = col1.date_input("তারিখ", datetime.now() if not edit_mode else pd.to_datetime(edit_mode['Date']))
        cat = col2.selectbox("বিভাগ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"], index=0 if not edit_mode else ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"].index(edit_mode['Category']))
        desc = st.text_input("বিবরণ", value="" if not edit_mode else edit_mode['Description'])
        amt = st.number_input("পরিমাণ (টাকা)", min_value=0, value=0 if not edit_mode else int(edit_mode['Amount']))
        
        if st.form_submit_button("সংরক্ষণ করুন"):
            if desc:
                if edit_mode:
                    requests.delete(f"{API_URL}/Description/{edit_mode['Description']}?sheet=Sheet1")
                
                new_entry = {"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}
                requests.post(f"{API_URL}?sheet=Sheet1", json={"data": [new_entry]})
                st.session_state.edit_data = None
                st.cache_data.clear()
                st.success("সফলভাবে সম্পন্ন হয়েছে!")
                st.rerun()
            else:
                st.error("বিবরণ দিন!")

    st.subheader("📊 বিভাগ অনুযায়ী লেনদেনের তালিকা")
    cats = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
    h_tabs = st.tabs(cats)
    for i, h_tab in enumerate(h_tabs):
        with h_tab:
            filtered = df[df['Category'] == cats[i]] if not df.empty and 'Category' in df.columns else pd.DataFrame()
            if not filtered.empty:
                st.dataframe(filtered[['Date', 'Description', 'Amount']].iloc[::-1], use_container_width=True, hide_index=True)
                total_val = pd.to_numeric(filtered['Amount']).sum()
                st.markdown(f'<div class="total-summary">মোট {cats[i]}: {total_val} টাকা</div>', unsafe_allow_html=True)
                
                with st.expander("📝 এডিট বা 🗑️ ডিলিট করতে ক্লিক করুন"):
                    for idx, row in filtered.iterrows():
                        c1, c2, c3 = st.columns([3, 1, 1])
                        c1.write(f"{row['Date']} - {row['Description']} ({row['Amount']}৳)")
                        if c2.button("📝", key=f"ed_h_{idx}"):
                            st.session_state.edit_data = row
                            st.rerun()
                        if c3.button("🗑️", key=f"del_h_{idx}"):
                            requests.delete(f"{API_URL}/Description/{row['Description']}?sheet=Sheet1")
                            st.cache_data.clear(); st.rerun()

# --- ট্যাব ২: কর্ম পরিকল্পনা (Plan) ---
with tab_plan:
    st.subheader("🗓️ ভবিষ্যৎ পরিকল্পনার তালিকা")
    with st.form("plan_form", clear_on_submit=True):
        p_date = st.date_input("পরিকল্পনার তারিখ", datetime.now())
        p_task = st.text_area("কি কাজ করতে চান?")
        if st.form_submit_button("প্ল্যান সেভ করুন"):
            if p_task:
                # ইউনিক আইডি জেনারেট করা ডিলিট করার জন্য
                p_id = str(datetime.now().timestamp()).replace(".", "")
                requests.post(f"{API_URL}?sheet=Plans", json={"data": [{"id": p_id, "Date": str(p_date), "Task": p_task}]})
                st.cache_data.clear(); st.success("প্ল্যান সেভ হয়েছে!"); st.rerun()

    plans_df = get_data("Plans")
    if not plans_df.empty:
        for i, row in plans_df.iloc[::-1].iterrows():
            st.markdown(f"""<div class="plan-card"><b>তারিখ: {row['Date']}</b><br>{row['Task']}</div>""", unsafe_allow_html=True)
            if st.button("🗑️ ডিলিট করুন", key=f"p_del_{i}"):
                requests.delete(f"{API_URL}/id/{row['id']}?sheet=Plans")
                st.cache_data.clear(); st.rerun()

# --- ট্যাব ৩: আজকের অভিজ্ঞতা (Experience) ---
with tab_exp:
    st.subheader("🌟 আজকের ভালো ও খারাপ অভিজ্ঞতা")
    with st.form("exp_form", clear_on_submit=True):
        e_date = st.date_input("অভিজ্ঞতার তারিখ", datetime.now())
        good_exp = st.text_area("কি ভালো হয়েছে? 😊")
        bad_exp = st.text_area("কি খারাপ হয়েছে? ☹️")
        if st.form_submit_button("অভিজ্ঞতা সেভ করুন"):
            e_id = str(datetime.now().timestamp()).replace(".", "")
            requests.post(f"{API_URL}?sheet=Experiences", json={"data": [{"id": e_id, "Date": str(e_date), "Good": good_exp, "Bad": bad_exp}]})
            st.cache_data.clear(); st.success("অভিজ্ঞতা সেভ হয়েছে!"); st.rerun()

    exp_df = get_data("Experiences")
    if not exp_df.empty:
        for i, row in exp_df.iloc[::-1].iterrows():
            st.write(f"### 📅 তারিখ: {row['Date']}")
            st.markdown(f'<div class="exp-card-good"><b>ভালো অভিজ্ঞতা:</b><br>{row["Good"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="exp-card-bad"><b>খারাপ অভিজ্ঞতা:</b><br>{row["Bad"]}</div>', unsafe_allow_html=True)
            if st.button("🗑️ মুছে ফেলুন", key=f"e_del_{i}"):
                requests.delete(f"{API_URL}/id/{row['id']}?sheet=Experiences")
                st.cache_data.clear(); st.rerun()
            st.divider()

# সাইডবার
if st.sidebar.button("লগআউট"):
    st.session_state["logged_in"] = False
    st.rerun()
