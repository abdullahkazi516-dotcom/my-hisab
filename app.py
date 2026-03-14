import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import streamlit.components.v1 as components
import json

# ১. পেজ সেটিংস
st.set_page_config(page_title="আমার ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"
FIXED_USER = "Kazi_Mamun"
DEFAULT_PW = "123456"

# ২. জাভাস্ক্রিপ্ট দিয়ে অফলাইন সাপোর্ট ও অটো-সিঙ্ক (Offline Local Storage)
def offline_sync_logic():
    components.html(
        f"""
        <script>
        function syncData() {{
            const pendingData = JSON.parse(localStorage.getItem('pending_entries') || '[]');
            if (navigator.onLine && pendingData.length > 0) {{
                pendingData.forEach((data, index) => {{
                    fetch('{API_URL}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ "data": [data] }})
                    }}).then(res => {{
                        if (res.status === 201) {{
                            pendingData.splice(index, 1);
                            localStorage.setItem('pending_entries', JSON.stringify(pendingData));
                            console.log('Synced successfully');
                        }}
                    }});
                }});
            }}
        }}
        // প্রতি ৫ সেকেন্ড পর পর চেক করবে ইন্টারনেট আছে কি না
        setInterval(syncData, 5000);
        </script>
        """, height=0
    )

# ৩. ডাটা ক্যাশিং
@st.cache_data(ttl=30)
def fetch_data():
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            if not df.empty:
                df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            return df
    except:
        pass
    return pd.DataFrame(columns=["Date", "Description", "Category", "Amount", "Voucher"])

# ৪. লগইন চেক
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def check_password():
    if not st.session_state["logged_in"]:
        st.title("🔐 লগইন করুন")
        pw = st.text_input("পাসওয়ার্ড দিন", type="password")
        if st.button("প্রবেশ করুন"):
            if pw == DEFAULT_PW:
                st.session_state["logged_in"] = True
                st.rerun()
            else: st.error("ভুল পাসওয়ার্ড!")
        return False
    return True

if check_password():
    offline_sync_logic() # অফলাইন সিঙ্ক চালু
    
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
        st.session_state.edit_index = None

    menu = st.sidebar.selectbox("মেনু", ["ড্যাশবোর্ড ও এন্ট্রি", "লগআউট"])

    if menu == "ড্যাশবোর্ড ও এন্ট্রি":
        st.title("💰 আমার ডিজিটাল ক্যাশ বুক")
        df = fetch_data()

        # ড্যাশবোর্ড বক্স (সংক্ষিপ্ত)
        if not df.empty:
            ti = df[df['Category'] == 'আয়']['Amount'].sum()
            te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
            balance = ti - te
            st.info(f"💵 নগদ জমা: {balance} টাকা")

        # ডাটা এন্ট্রি ফর্ম
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("তারিখ", datetime.now())
            cat = st.selectbox("ধরণ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
            desc = st.text_input("বিবরণ")
            amt = st.number_input("টাকা", min_value=0)
            submit = st.form_submit_button("Submit")

        if submit and desc:
            new_entry = {{"Date": str(date), "Description": desc, "Category": cat, "Amount": amt, "Voucher": "No"}}
            
            # অফলাইন হ্যান্ডলিং জাভাস্ক্রিপ্ট এর মাধ্যমে
            components.html(f"""
                <script>
                const entry = {json.dumps(new_entry)};
                if (!navigator.onLine) {{
                    const pending = JSON.parse(localStorage.getItem('pending_entries') || '[]');
                    pending.push(entry);
                    localStorage.setItem('pending_entries', JSON.stringify(pending));
                    alert('ইন্টারনেট নেই! ডাটা অফলাইনে সেভ হয়েছে। অনলাইনে এলে অটো আপডেট হবে।');
                }} else {{
                    // সরাসরি অনলাইনে সেভ করার চেষ্টা
                    fetch('{API_URL}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ "data": [entry] }})
                    }}).then(() => window.parent.location.reload());
                }}
                </script>
            """, height=0)
            st.success("প্রসেসিং হচ্ছে...")

        # তালিকা
        st.subheader("📊 লেনদেনের তালিকা")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    elif menu == "লগআউট":
        st.session_state["logged_in"] = False
        st.rerun()
