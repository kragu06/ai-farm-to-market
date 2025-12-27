import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests, json, urllib.parse

# =========================
# PAGE CONFIG & STYLE
# =========================
st.set_page_config(page_title="AI Farm-to-Market Cockpit", layout="wide")

st.markdown("""
<style>
.card {
    background-color: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.caption("Reducing distress sales using long-term market intelligence and AI-driven execution support.")

# =========================
# LOAD DATA
# =========================
data = pd.read_csv("price_data.csv")

required_cols = {"commodity", "year", "month", "price"}
if not required_cols.issubset(data.columns):
    st.error("CSV must contain: commodity, year, month, price")
    st.stop()

month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
             7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
data["month_name"] = data["month"].map(month_map)

# =========================
# HEADER
# =========================
st.title("🌾 AI Farm-to-Market Decision Cockpit")
st.caption("Decision → Infrastructure → Sales → Execution")

# =========================
# FARMER CONTEXT
# =========================
st.subheader("👨‍🌾 Farmer Context")
col1, col2, col3 = st.columns(3)

with col1:
    crop = st.selectbox("Commodity", sorted(data["commodity"].unique()))
with col2:
    quantity = st.number_input("Quantity (kg)", min_value=100, step=100)
with col3:
    urgency = st.selectbox("Urgency", ["Low", "Medium", "High"])

st.divider()
farmer_location = st.text_input("📍 Location", placeholder="Eg: Kolar, Karnataka")

# =========================
# DATA FILTER
# =========================
commodity_data = data[data["commodity"] == crop]
if commodity_data.empty:
    st.warning("No data for this commodity.")
    st.stop()

# =========================
# CURRENT PRICE (₹ / 100 kg)
# =========================
recent_window = min(6, len(commodity_data))
sell_now_price = commodity_data.tail(recent_window)["price"].mean()

# =========================
# SEASONAL PATTERN
# =========================
st.subheader("📈 Long-Term Seasonal Price Pattern")
seasonal_avg = commodity_data.groupby("month")["price"].mean().reset_index()
seasonal_avg["month_name"] = seasonal_avg["month"].map(month_map)

fig, ax = plt.subplots()
ax.plot(seasonal_avg["month_name"], seasonal_avg["price"], marker="o")
st.pyplot(fig)

# =========================
# RISK ANALYSIS
# =========================
current_month = pd.Timestamp.now().month
seasonal_price = seasonal_avg.loc[
    seasonal_avg["month"] == current_month, "price"
].values[0]

deviation_pct = ((sell_now_price - seasonal_price) / seasonal_price) * 100

def risk_label(dev):
    if dev < -30: return "🔴 High Crash Risk"
    if dev < -15: return "🟠 Medium Risk"
    return "🟢 Normal"

risk = risk_label(deviation_pct)

# =========================
# AI INFRASTRUCTURE DECISION
# =========================
perishability = {
    "Tomato":"High","Brinjal":"High",
    "Onion":"Medium","Green Chilli":"Medium",
    "Potato":"Low"
}

if "High" in risk:
    infra_choice = "Solar Dryer" if perishability[crop]=="High" else "Cold Storage"
elif "Medium" in risk:
    infra_choice = "Cold Storage"
else:
    infra_choice = "Fresh Market Sale"

# =========================
# AI DECISION BANNER
# =========================
emoji = "🚨" if "High" in risk else "⚠️" if "Medium" in risk else "✅"
bg = "#ffebee" if "High" in risk else "#fff8e1" if "Medium" in risk else "#e8f5e9"

st.markdown(f"""
<div style="background:{bg};padding:30px;border-radius:18px;text-align:center;">
<h1>{emoji} AI DECISION</h1>
<h2>{infra_choice}</h2>
<p><b>Risk:</b> {risk}</p>
</div>
""", unsafe_allow_html=True)

# =========================
# MAP LINK
# =========================
if farmer_location:
    keyword = {
        "Solar Dryer":"food processing unit",
        "Cold Storage":"cold storage warehouse",
        "Fresh Market Sale":"APMC market"
    }[infra_choice]

    maps_url = "https://www.google.com/maps/search/" + urllib.parse.quote(
        f"{keyword} near {farmer_location}"
    )

    st.link_button(f"📍 View Nearby {infra_choice}", maps_url)

# =========================
# ₹ COST–BENEFIT (PER 100 KG)
# =========================
st.subheader("💰 Cost–Benefit (per 100 kg fresh input)")

cold_storage_cost_per_day = 1.5
storage_days = 14
expected_price_recovery_pct = 18

dry_yield = {"Tomato":0.10,"Onion":0.12,"Brinjal":0.08,"Green Chilli":0.15,"Potato":0.20}
dried_price = {"Tomato":220,"Onion":180,"Brinjal":200,"Green Chilli":320,"Potato":150}

sell_now_value = sell_now_price

cold_storage_value = (
    sell_now_price * (1 + expected_price_recovery_pct/100)
    - cold_storage_cost_per_day * storage_days
)

solar_drying_value = (
    (100 * dry_yield[crop]) * dried_price[crop]
    - 100 * 2
)

comparison_df = pd.DataFrame({
    "Option":["Sell Now","Cold Storage","Solar Drying"],
    "Net Value (₹ per 100 kg)":[
        round(sell_now_value),
        round(cold_storage_value),
        round(solar_drying_value)
    ]
})

st.table(comparison_df)

# =========================
# AVAIL AI LEADS (REAL BACKEND) – FIXED
# =========================
st.subheader("🚀 Avail AI-Identified Leads")

if st.button("Request Buyer Connection"):
    payload = {
        "crop": crop,
        "quantity": quantity,
        "location": farmer_location,
        "infra_choice": infra_choice,
        "risk": risk,
        "urgency": urgency
    }

    try:
        response = requests.post(
            AWS_EXECUTION_API = "https://api-id.execute-api.region.amazonaws.com/prod/execute",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10
        )

        if response.status_code == 200:
            st.success(
                "✅ Request submitted successfully\n\n"
                "• Platform team notified\n"
                "• Buyer matching initiated\n"
                "• You will be contacted shortly"
            )
        else:
            st.error("⚠️ Server responded, but request failed.")

    except Exception as e:
        st.error(f"❌ Unable to submit request: {e}")
st.caption("Prototype uses historical intelligence. Live integrations are roadmap items.")
