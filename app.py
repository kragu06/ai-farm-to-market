import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import urllib.parse

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

st.caption(
    "Reducing distress sales through long-term market intelligence and AI-driven execution support."
)

# =========================
# LOAD DATA
# =========================
data = pd.read_csv("price_data.csv")

required_cols = {"commodity", "year", "month", "price"}
if not required_cols.issubset(data.columns):
    st.error("CSV must contain columns: commodity, year, month, price")
    st.stop()

month_map = {
    1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
    7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"
}
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

st.subheader("📍 Farmer Location")
farmer_location = st.text_input(
    "Village / Town / District / Pincode",
    placeholder="Eg: Kolar, Karnataka"
)

# =========================
# FILTER DATA
# =========================
commodity_data = data[data["commodity"] == crop]

if commodity_data.empty:
    st.warning("No historical data available for selected commodity.")
    st.stop()

# =========================
# CURRENT PRICE (ALL YEARS)
# =========================
recent_window = min(6, len(commodity_data))
current_price = commodity_data.tail(recent_window)["price"].mean()

# =========================
# SEASONAL PATTERN
# =========================
st.subheader("📈 Long-Term Seasonal Price Pattern")

seasonal_avg = commodity_data.groupby("month")["price"].mean().reset_index()
seasonal_avg["month_name"] = seasonal_avg["month"].map(month_map)

fig, ax = plt.subplots()
ax.plot(seasonal_avg["month_name"], seasonal_avg["price"], marker="o")
ax.set_xlabel("Month")
ax.set_ylabel("Average Price (₹)")
ax.set_title(f"{crop} – Historical Seasonal Pattern")
st.pyplot(fig)

# =========================
# RISK ANALYSIS
# =========================
current_month = pd.Timestamp.now().month
seasonal_price = seasonal_avg.loc[
    seasonal_avg["month"] == current_month, "price"
].values[0]

deviation_pct = ((current_price - seasonal_price) / seasonal_price) * 100

def risk_label(dev):
    if dev < -30:
        return "🔴 High Crash Risk"
    elif dev < -15:
        return "🟠 Medium Risk"
    return "🟢 Normal"

risk = risk_label(deviation_pct)

# =========================
# MARKET HEALTH
# =========================
health_score = int(max(0, min(100, 60 + deviation_pct)))
health_text = (
    "🔴 Dangerous" if health_score < 35
    else "🟠 Uncertain" if health_score < 60
    else "🟢 Favorable"
)
st.metric("🧠 Market Health Score", f"{health_score}/100", health_text)

# =========================
# AI INFRASTRUCTURE DECISION
# =========================
perishability = {
    "Tomato":"High",
    "Brinjal":"High",
    "Onion":"Medium",
    "Green Chilli":"Medium",
    "Potato":"Low"
}

if "High" in risk:
    infra_choice = "Solar Dryer" if perishability[crop] == "High" else "Cold Storage"
    infra_reason = "Severe price crash risk detected"
elif "Medium" in risk:
    infra_choice = "Cold Storage"
    infra_reason = "Moderate risk – wait for price recovery"
else:
    infra_choice = "Fresh Market Sale"
    infra_reason = "Prices are historically favorable"

# =========================
# AI DECISION BANNER
# =========================
emoji = "🚨" if "High" in risk else "⚠️" if "Medium" in risk else "✅"
bg = "#ffebee" if "High" in risk else "#fff8e1" if "Medium" in risk else "#e8f5e9"

st.markdown(f"""
<div style="background:{bg};padding:30px;border-radius:18px;text-align:center;">
<h1>{emoji} AI DECISION</h1>
<h2>{infra_choice}</h2>
<p><b>Reason:</b> {infra_reason}</p>
<p><b>Risk Level:</b> {risk}</p>
</div>
""", unsafe_allow_html=True)

# =========================
# GOOGLE MAPS (AI-DECIDED)
# =========================
infra_map_keywords = {
    "Solar Dryer": "food processing unit",
    "Cold Storage": "cold storage warehouse",
    "Fresh Market Sale": "APMC market"
}

if farmer_location:
    keyword = infra_map_keywords.get(infra_choice, "vegetable market")
    maps_url = (
        "https://www.google.com/maps/search/"
        + urllib.parse.quote(keyword + " near " + farmer_location)
    )

    st.link_button(
        f"📍 View Nearby {infra_choice} on Google Maps",
        maps_url
    )

# =========================
# DEMAND & SALES INTELLIGENCE
# =========================
st.subheader("🛒 Demand & Sales Intelligence")

demand = (
    "Low" if "High" in risk
    else "Selective" if "Medium" in risk
    else "Strong"
)
st.metric("📊 Demand Signal", demand)

st.subheader("📦 AI Sales Path")

if infra_choice == "Solar Dryer":
    st.write("• Dehydrated food processors\n• Institutional buyers\n• Export aggregators")
elif infra_choice == "Cold Storage":
    st.write("• Wholesale traders\n• Urban retailers\n• Supermarkets")
else:
    st.write("• APMC mandis\n• Local wholesalers\n• Retail vendors")

# =========================
# AVAIL AI LEADS (REAL BACKEND)
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
            "https://script.google.com/macros/s/AKfycbynbBKLTsoZ36y5qaNiHXnbD1c_HpmNFpLSrux_ou_n-j4XwWiRnnU_eQYPV2I6m3Tu/exec",
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
            st.error("⚠️ Request failed. Please try again.")

    except Exception as e:
        st.error(f"❌ Error sending request: {e}")
        else:
            st.error("⚠️ Request failed. Please try again.")

    except Exception:
        st.error("⚠️ Unable to submit request. Check internet connection.")

st.info(
    "🤝 **Handholding Model**\n\n"
    "• Farmers never chase buyers\n"
    "• Platform negotiates & executes\n"
    "• Revenue only on successful outcome"
)

# =========================
# ₹ COST–BENEFIT COMPARISON (CORRECT UNITS)
# =========================
st.subheader("💰 AI Cost–Benefit Comparison (per 100 kg fresh input)")

# Normalize everything to 100 kg fresh
base_qty = 100

# ---- SELL NOW
sell_now_value = (sell_now_price) * base_qty / 100

# ---- COLD STORAGE
cold_storage_cost_total = cold_storage_cost_per_day * storage_days * base_qty / 100
stored_price = sell_now_price * (1 + expected_price_recovery_pct / 100)
cold_storage_value = (stored_price * base_qty / 100) - cold_storage_cost_total

# ---- SOLAR DRYING (REAL ECONOMICS)
dry_yield_ratio = {
    "Tomato": 0.10,
    "Onion": 0.12,
    "Brinjal": 0.08,
    "Green Chilli": 0.15,
    "Potato": 0.20
}

dried_market_price = {
    "Tomato": 220,
    "Onion": 180,
    "Brinjal": 200,
    "Green Chilli": 320,
    "Potato": 150
}

drying_cost_per_kg_fresh = 2.0

dry_qty = base_qty * dry_yield_ratio[crop]
dry_revenue = dry_qty * dried_market_price[crop]
drying_cost = base_qty * drying_cost_per_kg_fresh
solar_drying_value = dry_revenue - drying_cost

# ---- DISPLAY TABLE
comparison_df = pd.DataFrame({
    "Option": ["Sell Now", "Cold Storage", "Solar Drying"],
    "Net Value (₹ per 100 kg fresh)": [
        round(sell_now_value, 0),
        round(cold_storage_value, 0),
        round(solar_drying_value, 0)
    ]
})

st.table(comparison_df)

best_option = comparison_df.loc[
    comparison_df["Net Value (₹ per 100 kg fresh)"].idxmax(), "Option"
]

# =========================
# DOWNLOAD
# =========================
st.subheader("⬇ Download Data")

st.download_button(
    "Download Commodity Data",
    commodity_data.to_csv(index=False),
    "decision_data.csv",
    "text/csv"
)

# =========================
# FOOTER
# =========================
st.caption(
    "This prototype uses historical intelligence. "
    "Live price, weather, and buyer APIs are part of the roadmap."
)
