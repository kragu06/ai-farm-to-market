import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Farm-to-Market Cockpit", layout="wide")
st.caption("Built to reduce distress sales by combining market memory, AI reasoning, and execution support.")

# =========================
# LOAD DATA
# =========================
data = pd.read_csv("price_data.csv")

month_map = {
    1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun",
    7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"
}
data["month_name"] = data["month"].map(month_map)

# =========================
# HEADER
# =========================
st.title("🍅 AI-Powered Farm-to-Market Decision Cockpit")
st.caption("Decision + Execution + Handholding | Outcome-based model")

# =========================
# CONTEXT PANEL
# =========================
st.subheader("👨‍🌾 Context")

col1, col2, col3 = st.columns(3)

with col1:
    crop = st.selectbox("Crop", ["Tomato"])

with col2:
    quantity = st.number_input("Quantity (kg)", min_value=100, step=100)

with col3:
    urgency = st.selectbox("Farmer Urgency", ["Low", "Medium", "High"])

st.divider()

st.subheader("📍 Farmer Location")

farmer_location = st.text_input(
    "Enter Village / Town / District / Pin Code",
    placeholder="Example: Kolar, Karnataka or 563101"
)

st.subheader("🏗️ Required Infrastructure")

infra_type = st.selectbox(
    "Select Infrastructure Type",
    [
        "Solar Dryer",
        "Cold Storage",
        "Market / Mandi",
        "Government Warehouse"
    ]
)

if farmer_location:
    search_query = infra_type.replace(" ", "+")
    maps_url = f"https://www.google.com/maps/search/{search_query}+near+{farmer_location}"

    st.markdown(
        f"### 🗺️ Nearby {infra_type}\n"
        f"[👉 Open in Google Maps]({maps_url})"
    )
)
if farmer_location:
    search_query = infra_type.replace(" ", "+")
    maps_url = f"https://www.google.com/maps/search/{search_query}+near+{farmer_location}"

    st.markdown(
        f"### 🗺️ Nearby {infra_type}\n"
        f"[👉 Open in Google Maps]({maps_url})",
        unsafe_allow_html=True
    )

# =========================
# YEAR SELECTION
# =========================
st.subheader("📅 Market Context")
selected_year = st.selectbox("Select Year", sorted(data["year"].unique(), reverse=True))
year_data = data[data["year"] == selected_year]

# =========================
# PRICE TREND
# =========================
st.subheader("📈 Monthly Price Trend")
fig, ax = plt.subplots()
ax.plot(year_data["month_name"], year_data["price"], marker="o")
ax.set_xlabel("Month")
ax.set_ylabel("Price (₹)")
ax.set_title(f"{crop} Prices – {selected_year}")
st.pyplot(fig)

# =========================
# SEASONAL BASELINE
# =========================
seasonal_avg = data.groupby("month")["price"].mean().reset_index()
merged = pd.merge(
    year_data, seasonal_avg, on="month", suffixes=("_current", "_seasonal")
)

# =========================
# CRASH & RISK LOGIC
# =========================
merged["deviation_pct"] = (
    (merged["price_current"] - merged["price_seasonal"]) /
    merged["price_seasonal"]
) * 100

def risk_label(dev):
    if dev < -30:
        return "🔴 High Crash Risk"
    elif dev < -15:
        return "🟠 Medium Risk"
    else:
        return "🟢 Normal"

merged["risk"] = merged["deviation_pct"].apply(risk_label)

# =========================
# MARKET HEALTH SCORE
# =========================
avg_dev = merged["deviation_pct"].mean()
health_score = int(max(0, min(100, 60 + avg_dev)))

if health_score < 35:
    health_text = "🔴 Dangerous"
elif health_score < 60:
    health_text = "🟠 Uncertain"
else:
    health_text = "🟢 Favorable"

st.metric("🧠 Market Health Score", f"{health_score} / 100", health_text)

# =========================
# DECISION ENGINE
# =========================
def decision(risk, urgency):
    if "High" in risk:
        return "Process / Store", "Hold 3–4 weeks"
    if "Medium" in risk:
        return "Hold", "Review after 2 weeks"
    return "Sell", "Sell within 7 days"

merged[["action", "timeframe"]] = merged.apply(
    lambda r: pd.Series(decision(r["risk"], urgency)), axis=1
)
st.subheader("🧾 Final AI Verdict")

latest = merged.iloc[-1]

st.success(
    f"""
    **Recommended Action:** {latest['action']}  
    **Timeframe:** {latest['timeframe']}  
    **Risk Level:** {latest['risk']}
    """
)

# =========================
# WORST-CASE WARNING
# =========================
worst_month = merged.sort_values("deviation_pct").iloc[0]
loss_est = abs(worst_month["deviation_pct"]) * worst_month["price_seasonal"] / 100

if "High" in worst_month["risk"]:
    st.error(
        f"⚠️ Worst-case warning: Selling in {worst_month['month_name']} "
        f"could mean ~₹{int(loss_est)} loss per unit vs seasonal average."
    )

# =========================
# INFRASTRUCTURE MATCHING (MOCK LOGIC)
# =========================
st.subheader("🏗️ Infrastructure Recommendation")

infra = pd.DataFrame({
    "Option": ["Solar Dryer", "Cold Storage", "Fresh Sale"],
    "Distance (km)": [12, 8, 3],
    "Cost": ["₹2/kg", "₹1.5/kg/day", "₹0"],
    "Time": ["3 days", "15 days", "Immediate"],
    "Suitability": ["High", "Medium", "Low"]
})

st.table(infra)

if "High" in worst_month["risk"]:
    best_option = "Solar Dryer"
elif "Medium" in worst_month["risk"]:
    best_option = "Cold Storage"
else:
    best_option = "Fresh Sale"

st.success(f"✅ Best Option Right Now: **{best_option}**")

# =========================
# VALUE ADD MARGIN
# =========================
st.subheader("💰 Value Impact")
fresh_value = year_data["price"].mean()
processed_value = fresh_value * 1.18

st.write(f"• Fresh sale estimate: ₹{int(fresh_value)}")
st.write(f"• After processing: ₹{int(processed_value)} (**+18%**)")

# =========================
# DEMAND & SALES INTELLIGENCE
# =========================
st.subheader("🛒 Demand & Sales Intelligence")

if health_score < 50:
    demand = "🟡 Medium"
    buyer = "Processing Unit / Bulk Buyer"
else:
    demand = "🟢 High"
    buyer = "Wholesale Mandi / Urban Buyer"

st.write(f"**Demand Signal:** {demand}")
st.write(f"**Suggested Buyer Type:** {buyer}")

# =========================
# AI EXPLANATION (BEDROCK STYLE)
# =========================
st.subheader("🧠 Why AI Suggests This")

st.info(
    "The system compares current monthly prices with long-term seasonal averages. "
    "Prices falling significantly below normal seasonal levels are flagged as crash risks. "
    "During such windows, storage or processing reduces downside risk and improves net income. "
    "When prices align with or exceed seasonal norms, immediate selling is recommended."
)
st.subheader("⬇ Download Decision Report")

csv = merged.to_csv(index=False)

st.download_button(
    "Download Decision CSV",
    csv,
    "decision_report.csv",
    "text/csv"
)

# =========================
# HANDHOLDING MODEL
# =========================
st.subheader("🤝 Platform Handholding Model")
st.write(
    "• Farmers retain decision control\n"
    "• Platform executes storage, processing, and sales\n"
    "• Revenue is shared only if farmer income improves"
)

# =========================
# IMPACT SUMMARY
# =========================
st.subheader("🎯 Expected Impact")
st.write(
    "📈 Income improvement: **+12–25%**\n\n"
    "🌾 Distress sale reduction\n\n"
    "♻️ Lower post-harvest waste\n\n"
    "🌞 Better utilization of rural infrastructure"
)
st.subheader("🔮 Future Roadmap")

future_mode = st.toggle("Show Future Capabilities")

if future_mode:
    st.info(
        "Future versions will integrate live mandi prices, "
        "weather alerts, government policy notifications, "
        "and automated buyer matching using cloud AI services."
    )
st.caption(
    "Note: This prototype demonstrates decision intelligence using historical data. "
    "Live integrations are part of the deployment roadmap."
)
