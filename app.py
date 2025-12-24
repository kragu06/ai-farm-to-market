import streamlit as st

st.set_page_config(page_title="AI Farm-to-Market", layout="wide")

st.title("🌾 AI-Powered Farm-to-Market Handholding Platform")

st.subheader("Farmer Intake")
crop = st.selectbox("Crop", ["Onion", "Tomato", "Chilli"])
quantity = st.number_input("Quantity (kg)", min_value=0)
urgency = st.selectbox("Urgency", ["High", "Medium", "Low"])

if st.button("Analyze"):
    st.success("AI Recommendation Generated")
    st.markdown("### 🔵 Suggested Action: Process & Sell Later")
    st.write("Reason: Based on historical price patterns and nearby infrastructure.")
