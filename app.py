import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import streamlit.components.v1 as components
import json

# ১. পেজ সেটিংস ও সিএসএস ডিজাইন (Custom CSS for Beautiful Borders)
st.set_page_config(page_title="ডিজিটাল ক্যাশ বুক", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    /* বক্স ডিজাইন */
    .reportview-container .main .block-container { padding-top: 2rem; }
    .stTable { border: 1px solid #e6e9ef; border-radius: 10px; overflow: hidden; }
    
    /* ক্যাটাগরি অনুযায়ী আলাদা বর্ডার ও ব্যাকগ্রাউন্ড */
    .box-income { border-left: 8px solid #28a745; background-color: #f8fff9; padding: 15px; border-radius: 5px; margin-bottom: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .box-expense { border-left: 8px solid #dc3545; background-color: #fff8f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .box-due { border-left: 8px solid #ffc107; background-color: #fffdf5; padding: 15px; border-radius: 5px; margin-bottom: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .box-dena { border-left: 8px solid #fd7e14; background-color: #fff9f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .box-powna { border-left: 8px solid #17a2b8; background-color: #f5fcff; padding: 15px; border-radius: 5px; margin-bottom: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    
    h3 { margin-bottom: 10px; color: #333; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/7mzpsfz9aa5r7"
FIXED_USER = "Kazi_Mamun"
DEFAULT_PW = "427054"

# ২. অফলাইন সিঙ্ক
def sync_offline():
    components.html(
        f"""<script>
        function sync() {{
            const pending = JSON.parse(localStorage.getItem('off_data') || '[]');
            if (navigator.onLine && pending.length > 0) {{
                pending.forEach((item, index) => {{
                    fetch('{API_URL}', {{
                        method: 'POST', headers: {{ 'Content-Type': 'application/json' }},
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
        </script>""", height=0
    )

# ৩. ডাটা লোড
@st.cache_data(ttl=15)
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
    st.sidebar.title(f"স্বাগতম, {FIXED_USER}")
    menu = st.sidebar.selectbox("মেনু", ["ড্যাশবোর্ড ও এন্ট্রি", "লগআউট"])

    if menu == "ড্যাশবোর্ড ও এন্ট্রি":
        st.title("💰 ডিজিটাল ক্যাশ বুক")
        df = get_data()

        # ড্যাশবোর্ড সামারি
        if not df.empty:
            ti = df[df['Category'] == 'আয়']['Amount'].sum()
            te = df[df['Category'] == 'ব্যয়']['Amount'].sum()
            st.success(f"### 💵 মোট নগদ জমা: {ti - te} টাকা")

        # এন্ট্রি ফর্ম
        with st.expander("➕ নতুন লেনদেন যোগ করুন"):
            with st.form("entry_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                date = c1.date_input("তারিখ", datetime.now())
                cat = c1.selectbox("ধরণ", ["আয়", "ব্যয়", "বকেয়া", "দেনা", "পাওনা"])
                desc = c2.text_input("বিবরণ")
                amt = c2.number_input("টাকা", min_value=0)
                if st.form_submit_button("সংরক্ষণ করুন"):
                    if desc:
                        entry = {"Date": str(date), "Description": desc, "Category": cat, "Amount": amt}
                        components.html(f"""<script>
                            const data = {json.dumps(entry)};
                            if (!navigator.onLine) {{
                                const p = JSON.parse(localStorage.getItem('off_data') || '[]');
                                p.push(data); localStorage.setItem('off_data', JSON.stringify(p));
                                alert('অফলাইনে সেভ হয়েছে!');
                            }} else {{
                                fetch('{API_URL}', {{
                                    method: 'POST', headers: {{ 'Content-Type': 'application/json' }},
                                    body: JSON.stringify({{ "data": [data] }})
                                }}).then(() => window.parent.location.reload());
                            }}
                        </script>""", height=0)

        # ৫. সুন্দর বর্ডার ও কালার দিয়ে আলাদা বিভাগ
        st.subheader("📊 বিভাগ অনুযায়ী লেনদেনের তালিকা")
        
        # ক্যাটাগরি ম্যাপিং (রঙের ক্লাস ও নাম)
        cat_info = {
            "আয়": "box-income",
            "ব্যয়": "box-expense",
            "বকেয়া": "box-due",
            "দেনা": "box-dena",
            "পাওনা": "box-powna"
        }

        for category, css_class in cat_info.items():
            filtered_df = df[df['Category'] == category]
            
            # প্রতিটি বিভাগের জন্য আলাদা বক্স ডিজাইন
            st.markdown(f'<div class="{css_class}"><h3>📁 {category} তালিকা</h3>', unsafe_allow_html=True)
            if not filtered_df.empty:
                # টেবিলটিকে সুন্দরভাবে দেখানোর জন্য
                display_df = filtered_df[['Date', 'Description', 'Amount']].iloc[::-1].reset_index(drop=True)
                st.table(display_df)
            else:
                st.write("এই বিভাগে কোনো ডাটা নেই।")
            st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "লগআউট":
        st.session_state["logged_in"] = False
        st.rerun()
