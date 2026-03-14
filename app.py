import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import streamlit.components.v1 as components
import json

# ১. পেজ সেটিংস ও পারফরম্যান্স বুস্ট
st.set_page_config(page_title="ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"
FIXED_USER = "Kazi_Mamun"
DEFAULT_PW = "427054" # আপনার ছবি অনুযায়ী পাসওয়ার্ড আপডেট করা হয়েছে

# ২. অফলাইন ডাটা সেভ ও অটো-সিঙ্ক (JavaScript)
def offline_logic():
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

# ৩. দ্রুত ডাটা লোড করার জন্য ক্যাশিং
@st.cache_data(ttl=20)
def get_data():
    try:
        res = requests.get(API_URL, timeout=5)
        df = pd.DataFrame(res.json())
        if not df.empty:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=["Date", "Description", "Category", "Amount", "Voucher"])

# ৪. ভয়েস ফাংশন
def speak():
    components.html(
        """<script>
        var msg = new SpeechSynthesisUtterance("আপনার লেনদেনটি সফল ভাবে আপডেট হয়েছে");
        msg.lang = 'bn-BD';
        window.speechSynthesis.speak(msg);
        </script>""", height=0
    )

# ৫. লগইন ইন্টারফেস
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 লগইন করুন")
    pw = st.text_input("পাসওয়ার্ড দিন", type="password")
    if st.button("প্রবেশ করুন"):
        if pw == DEFAULT_PW:
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড!") #
else:
    offline_logic()
    menu = st.sidebar.selectbox("মেনু", ["ড্যাশবোর্ড ও এন্ট্রি", "লগআউট"])

    if menu == "ড্যাশবোর্ড ও এন্ট্রি":
        st.title("💰 আমার ডিজিটাল ক্যাশ বুক")
        df = get_data()

        # ড্যাশবোর্ড বক্স
        if not df.empty:
            ti = df[df['Category'] == 'আয়']['Amount'].sum()
            te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
            st.success(f"💵 বর্তমান নগদ জমা: {ti - te} টাকা")

        # এন্ট্রি ফর্ম
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("তারিখ", datetime.now())
            cat = st.selectbox("ধরণ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
            desc = st.text_input("বিবরণ")
            amt = st.number_input("টাকা", min_value=0)
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
                    speak()

        # ৬. আলাদা আলাদা বিভাগ (Tabs)
        st.subheader("📊 হিসাবের তালিকা")
        tabs = st.tabs(["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
        
        categories = ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"]
        for i, tab in enumerate(tabs):
            with tab:
                filtered_df = df[df['Category'] == categories[i]]
                if not filtered_df.empty:
                    for idx, row in filtered_df.iloc[::-1].iterrows():
                        st.write(f"📅 {row['Date']} | {row['Description']} | 💰 {row['Amount']}")
                        st.divider()
                else:
                    st.info("কোনো তথ্য নেই")

    elif menu == "লগআউট":
        st.session_state["logged_in"] = False
        st.rerun()
