import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# PAGE CONFIG & STYLE
# =========================
st.set_page_config(page_title="AI Farm-to-Market Cockpit", layout="wide")

st.markdown(
    """
    <style>
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Built to reduce distress sales by combining market memory, AI reasoning, and execution support."
)

# =========================
# LOAD DATA
# =========================
data = pd.read_csv("price_data.csv")

required_cols = {"commodity", "year", "month", "price"}
if not required_cols.issubset(data.columns):
    st.error("CSV file format incorrect. Required columns: commodity, year, month, price")
    st.stop()

month_map = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
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
    crop = st.selectbox("Commodity", sorted(data["commodity"].unique()))

with col2:
    quantity = st.number_input("Quantity (kg)", min_value=100, step=100)

with col3:
    urgency = st.selectbox("Farmer Urgency", ["Low", "Medium", "High"])

st.divider()

# =========================
# LOCATION & MAP
# =========================
st.subheader("📍 Farmer Location")

farmer_location = st.text_input(
    "Enter Village / Town / District / Pin Code",
    placeholder="Example: Kolar, Karnataka or 563101"
)

st.subheader("🏗️ Required Infrastructure")

# =========================
# GOOGLE MAPS – NEARBY INFRASTRUCTURE
# =========================
infra_map_keywords = {
    "Solar Dryer": "food processing unit",
    "Cold Storage": "cold storage warehouse",
    "Fresh Market Sale": "APMC market",
    "Staggered Sale": "vegetable wholesale market"
}

if farmer_location:
    map_keyword = infra_map_keywords.get(infra_choice, "vegetable market")
    maps_url = (
        f"https://www.google.com/maps/search/"
        f"{map_keyword}+near+{farmer_location}"
    )

    st.markdown(
        f"📍 [View Nearby {infra_choice} Locations on Google Maps]({maps_url})"
    )
    maps_url = f"https://www.google.com/maps/search/{search_query}+near+{farmer_location}"
    st.markdown(f"[👉 Open {infra_type} in Google Maps]({maps_url})")

# =========================
# ALL-YEARS DATA (CORE DESIGN)
# =========================
commodity_data = data[data["commodity"] == crop]

if commodity_data.empty:
    st.warning("No historical data available for this commodity.")
    st.stop()

# =========================
# CURRENT PRICE LEVEL (YEAR-AGNOSTIC)
# =========================
recent_window = min(6, len(commodity_data))
current_price = commodity_data.tail(recent_window)["price"].mean()

# =========================
# SEASONAL PATTERN CHART
# =========================
st.subheader("📈 Long-Term Seasonal Price Pattern")

seasonal_plot = (
    commodity_data
    .groupby("month")["price"]
    .mean()
    .reset_index()
)

seasonal_plot["month_name"] = seasonal_plot["month"].map(month_map)

fig, ax = plt.subplots()
ax.plot(seasonal_plot["month_name"], seasonal_plot["price"], marker="o")
ax.set_xlabel("Month")
ax.set_ylabel("Average Price (₹)")
ax.set_title(f"{crop} – Historical Seasonal Pattern")
st.pyplot(fig)

# =========================
# SEASONAL COMPARISON
# =========================
current_month = pd.Timestamp.now().month

seasonal_price = seasonal_plot.loc[
    seasonal_plot["month"] == current_month, "price"
].values[0]

deviation_pct = ((current_price - seasonal_price) / seasonal_price) * 100

# =========================
# RISK LOGIC
# =========================
def risk_label(dev):
    if dev < -30:
        return "🔴 High Crash Risk"
    elif dev < -15:
        return "🟠 Medium Risk"
    else:
        return "🟢 Normal"

risk = risk_label(deviation_pct)
# =========================
# AI INFRASTRUCTURE DECISION ENGINE
# =========================

current_month = pd.Timestamp.now().month

# Simple perishability score (domain knowledge)
perishability = {
    "Tomato": "High",
    "Onion": "Medium",
    "Potato": "Low",
    "Brinjal": "High",
    "Green Chilli": "Medium"
}

# Monsoon & summer proxy (India-focused)
monsoon_months = [6, 7, 8, 9]
summer_months = [3, 4, 5]

if "High" in risk:
    if perishability.get(crop) == "High":
        infra_choice = "Solar Dryer"
        infra_reason = "High price crash risk + high perishability"
    else:
        infra_choice = "Cold Storage"
        infra_reason = "High price crash risk + lower perishability"

elif "Medium" in risk:
    if current_month in monsoon_months:
        infra_choice = "Cold Storage"
        infra_reason = "Monsoon season + moderate price risk"
    else:
        infra_choice = "Staggered Sale"
        infra_reason = "Moderate risk, monitor recovery"

else:
    infra_choice = "Fresh Market Sale"
    infra_reason = "Favourable prices, immediate sale advised"

# =========================
# MARKET HEALTH SCORE
# =========================
health_score = int(max(0, min(100, 60 + deviation_pct)))

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

action, timeframe = decision(risk, urgency)

if "High" in risk:
    bg_color = "#ffebee"
    emoji = "🚨"
elif "Medium" in risk:
    bg_color = "#fff8e1"
    emoji = "⚠️"
else:
    bg_color = "#e8f5e9"
    emoji = "✅"

st.markdown(
    f"""
    <div style="
        background:{bg_color};
        padding:35px;
        border-radius:18px;
        text-align:center;
        box-shadow:0 6px 18px rgba(0,0,0,0.15);
        margin-bottom:30px;
    ">
        <h1>{emoji} AI DECISION</h1>
        <h2>{action}</h2>
        <h4>{timeframe}</h4>
        <p><b>Risk Level:</b> {risk}</p>
    </div>
    """,
    unsafe_allow_html=True
)
# =========================
# AI ACTION RECOMMENDATION
# =========================
st.subheader("🤖 AI Action Recommendation")

if "High" in risk:
    st.error(
        "🔴 **Do NOT sell now.**\n\n"
        "• Use **Solar Drying** to reduce losses\n"
        "• OR store temporarily in **Cold Storage**\n\n"
        "AI predicts distress sale risk if sold immediately."
    )
elif "Medium" in risk:
    st.warning(
        "🟠 **Avoid bulk selling.**\n\n"
        "• Use **short-term Cold Storage**\n"
        "• OR stagger sales over time."
    )
else:
    st.success(
        "🟢 **Sell Fresh Produce Now.**\n\n"
        "Market conditions are favorable compared to historical trends."
    )
# =========================
# DOWNSIDE WARNING
# =========================
if deviation_pct < -30:
    st.error("⚠️ Historically severe downside risk. Storage or processing advised.")
elif deviation_pct < -15:
    st.warning("⚠️ Moderate downside risk. Short-term holding may help.")
else:
    st.success("✅ Price levels are within normal historical range.")

# =========================
# INFRASTRUCTURE RECOMMENDATION
# =========================
st.subheader("🏗️ AI-Decided Infrastructure Strategy")

st.success(f"✅ **Recommended Option:** {infra_choice}")
st.info(f"🧠 **Why:** {infra_reason}")

if "High" in risk:
    best_option = "Solar Dryer"
elif "Medium" in risk:
    best_option = "Cold Storage"
else:
    best_option = "Fresh Sale"

st.success(f"✅ Best Option Right Now: **{best_option}**")

st.subheader("🏗️ AI Infrastructure Strategy")

if "High" in risk:
    infra_choice = "Solar Dryer"
    infra_reason = (
        "High supply glut detected. Drying reduces volume, "
        "extends shelf life, and protects value during price crashes."
    )
elif "Medium" in risk:
    infra_choice = "Cold Storage"
    infra_reason = (
        "Moderate price weakness detected. Short-term storage "
        "allows selling during recovery windows."
    )
else:
    infra_choice = "Fresh Market Sale"
    infra_reason = (
        "Prices are within or above normal range. Immediate sale "
        "maximizes cash flow."
    )

st.success(f"✅ Suggested Infrastructure: **{infra_choice}**")
st.info(f"🧠 Why: {infra_reason}")

# =========================
# GOOGLE MAPS – NEARBY INFRASTRUCTURE
# =========================

infra_map_keywords = {
    "Solar Dryer": "food processing unit",
    "Cold Storage": "cold storage warehouse",
    "Fresh Market Sale": "APMC market",
    "Staggered Sale": "vegetable wholesale market"
}

if farmer_location:
    map_keyword = infra_map_keywords.get(infra_choice, "vegetable market")
    maps_url = (
        f"https://www.google.com/maps/search/"
        f"{map_keyword}+near+{farmer_location}"
    )

    st.markdown(
        f"📍 [View Nearby {infra_choice} Locations on Google Maps]({maps_url})"
    )

# =========================
# VALUE IMPACT
# =========================
st.subheader("💰 Value Impact")

fresh_value = commodity_data["price"].mean()
processed_value = fresh_value * 1.18

st.write(f"• Fresh sale estimate: ₹{int(fresh_value)}")
st.write(f"• After processing: ₹{int(processed_value)} (**+18%**)")

# =========================
# DEMAND SIGNAL
# =========================
st.subheader("🛒 Demand & Sales Intelligence")

# =========================
# DEMAND SIGNAL
# =========================
if "High" in risk:
    demand_level = "🔴 Low Immediate Demand"
elif "Medium" in risk:
    demand_level = "🟠 Selective Demand"
else:
    demand_level = "🟢 Strong Demand"

st.metric("📊 Current Demand Signal", demand_level)

# =========================
# SALES STRATEGY (AI-DRIVEN)
# =========================
st.subheader("📦 AI Sales Strategy")

if infra_choice == "Solar Dryer":
    st.write(
        "🧭 **Sales Path Identified:**\n"
        "• Dehydrated vegetable processors\n"
        "• Spice & soup powder manufacturers\n"
        "• Institutional buyers (hostels, ICDS, mid-day meal)\n"
        "• Export-oriented aggregators\n\n"
        "💡 **Platform Role:** Aggregate volume, ensure drying quality, "
        "negotiate bulk contracts."
    )

elif infra_choice == "Cold Storage":
    st.write(
        "🧭 **Sales Path Identified:**\n"
        "• Wholesale mandis (post price recovery)\n"
        "• Urban retailers & supermarkets\n"
        "• Bulk traders\n\n"
        "💡 **Platform Role:** Monitor prices daily, trigger sale at recovery peak."
    )

else:
    st.write(
        "🧭 **Sales Path Identified:**\n"
        "• Nearby APMC mandi\n"
        "• Local wholesalers\n"
        "• Retail vendors\n\n"
        "💡 **Platform Role:** Enable quick listing, connect to nearby buyers."
    )
    # =========================
# AI LEAD DISCOVERY (SIMULATED)
# =========================
st.subheader("🔎 AI Lead Discovery")

if infra_choice == "Solar Dryer":
    st.success(
        "🔗 Leads Found:\n"
        "• 2 regional dehydrated food processors\n"
        "• 1 institutional bulk buyer\n"
        "• 1 export aggregator\n\n"
        "⏳ Contact initiation recommended within 7 days."
    )

elif infra_choice == "Cold Storage":
    st.success(
        "🔗 Leads Found:\n"
        "• 3 wholesale traders monitoring prices\n"
        "• 2 urban retailers\n\n"
        "⏳ Expected selling window: 10–20 days."
    )

else:
    st.success(
        "🔗 Leads Found:\n"
        "• 2 nearby APMC traders\n"
        "• 3 local wholesalers\n\n"
        "⏳ Immediate sale possible."
    )

st.caption(
    "Note: Leads are generated using historical demand patterns. "
    "Live buyer discovery via e-commerce & wholesale APIs is part of future roadmap."
)
# =========================
# AVAIL AI LEADS
# =========================
st.subheader("🚀 Avail AI-Identified Leads")

if st.button("Request Buyer Connection"):
    st.success(
        "✅ Request registered successfully!\n\n"
        "Our platform team will:\n"
        "• Contact verified buyers\n"
        "• Match quality & quantity\n"
        "• Negotiate best possible price\n"
        "• Coordinate logistics\n\n"
        "⏳ Expected response time: 24–48 hours"
    )
    # =========================
# HANDHOLDING EXPLANATION (STEP 2)
# =========================
st.info(
    "🤝 **How the Handholding Works:**\n\n"
    "• Farmer does NOT chase buyers\n"
    "• Platform aggregates produce\n"
    "• Platform negotiates pricing\n"
    "• Farmer approves final deal\n"
    "• Payment after successful sale\n\n"
    "No upfront cost. Platform earns only if farmer earns."
)
# =========================
# DOWNLOAD
# =========================
st.subheader("⬇ Download Decision Data")

csv = commodity_data.to_csv(index=False)

st.download_button(
    "Download CSV",
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
# IMPACT & ROADMAP
# =========================
st.subheader("🎯 Expected Impact")

st.write(
    "📈 Income improvement: **+12–25%**\n\n"
    "🌾 Distress sale reduction\n\n"
    "♻️ Lower post-harvest waste\n\n"
    "🌞 Better utilization of rural infrastructure"
)

future_mode = st.toggle("Show Future Capabilities")

if future_mode:
    st.info(
        "Future versions will integrate live mandi prices, "
        "weather alerts, government policy notifications, "
        "and automated buyer matching."
    )

st.caption(
    "Note: This prototype demonstrates decision intelligence using historical data. "
    "Live integrations are part of the deployment roadmap."
)
