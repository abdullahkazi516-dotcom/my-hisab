import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import streamlit.components.v1 as components
import json

# ১. পেজ সেটিংস
st.set_page_config(page_title="ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"
FIXED_USER = "Kazi_Mamun"
DEFAULT_PW = "427054"

# ২. অফলাইন সিঙ্ক ও বায়োমেট্রিক সাপোর্ট
def sync_offline():
    components.html(
        f"""
        <script>
        function sync() {{
            const pending = JSON.parse(localStorage.getItem('off_data') || '[]');
            if (navigator.onLine && pending.length > 0) {{
                pending.forEach((item, index) => {{
                    fetch('{API_URL}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ "data": [item] }})
                    }}).then(res => {{
                        if (res.status === 201) {{
                            pending.splice(index, 1);
                            localStorage.setItem('off_data', JSON.stringify(pending));
                        }}
                    }});
                }});
            }}
        }}
        setInterval(sync, 5000);
        </script>
        """, height=0
    )

# ৩. ডাটা লোড ফাংশন
@st.cache_data(ttl=20)
def get_data():
    try:
        res = requests.get(API_URL, timeout=5)
        df = pd.DataFrame(res.json())
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    except:
        return pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])

# ৪. লগইন
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 লগইন করুন")
    pw = st.text_input("পাসওয়ার্ড দিন", type="password", autocomplete="current-password")
    if st.button("প্রবেশ করুন"):
        if pw == DEFAULT_PW:
            st.session_state["logged_in"] = True
            st.rerun()
        else: st.error("ভুল পাসওয়ার্ড!")
else:
    sync_offline()
    menu = st.sidebar.selectbox("মেনু", ["ড্যাশবোর্ড ও এন্ট্রি", "লগআউট"])

    if menu == "ড্যাশবোর্ড ও এন্ট্রি":
        st.title("💰 আমার ডিজিটাল ক্যাশ বুক")
        df = get_data()

        # ড্যাশবোর্ড রঙিন সামারি
        if not df.empty:
            ti = df[df['Category'] == 'আয়']['Amount'].sum()
            te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
            st.success(f"💵 বর্তমান নগদ জমা: {ti - te} টাকা")

        # এন্ট্রি ফর্ম
        with st.expander("➕ নতুন লেনদেন যোগ করুন", expanded=True):
            with st.form("entry_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                date = col1.date_input("তারিখ", datetime.now())
                cat = col1.selectbox("ধরণ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
                desc = col2.text_input("বিবরণ")
                amt = col2.number_input("টাকা", min_value=0)
                if st.form_submit_button("Submit"):
                    if desc:
                        entry = {"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}
                        components.html(f"""
                            <script>
                            const data = {json.dumps(entry)};
                            if (!navigator.onLine) {{
                                const pending = JSON.parse(localStorage.getItem('off_data') || '[]');
                                pending.push(data);
                                localStorage.setItem('off_data', JSON.stringify(pending));
                                alert('অফলাইনে সেভ হয়েছে!');
                            }} else {{
                                fetch('{API_URL}', {{
                                    method: 'POST', headers: {{ 'Content-Type': 'application/json' }},
                                    body: JSON.stringify({{ "data": [data] }})
                                }}).then(() => window.parent.location.reload());
                            }}
                            </script>
                        """, height=0)

        # ৫. বিভাগ অনুযায়ী টেবিল (Folders/Tabs)
        st.subheader("📊 হিসাবের তালিকা (বিভাগ অনুযায়ী টেবিল)")
        tabs = st.tabs(["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
        categories = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]

        for i, tab in enumerate(tabs):
            with tab:
                filtered_df = df[df['Category'] == categories[i]]
                if not filtered_df.empty:
                    # টেবিল আকারে প্রদর্শন
                    st.table(filtered_df[['Date', 'Description', 'Amount']].iloc[::-1])
                else:
                    st.info(f"এই মুহূর্তে কোনো {categories[i]} রেকর্ড নেই।")

    elif menu == "লগআউট":
        st.session_state["logged_in"] = False
        st.rerun()
