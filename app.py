import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Farm-to-Market", layout="wide")

st.title("🍅 AI-Powered Farm-to-Market Decision Dashboard")

# -------------------------
# Load Data
# -------------------------
data = pd.read_csv("price_data.csv")

# Convert month number to name
month_map = {
    1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun",
    7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"
}
data["month_name"] = data["month"].map(month_map)

# -------------------------
# User Controls
# -------------------------
st.subheader("👨‍🌾 Context Selection")
selected_year = st.selectbox("Select Year", sorted(data["year"].unique(), reverse=True))

year_data = data[data["year"] == selected_year]

# -------------------------
# Price Trend Plot
# -------------------------
st.subheader("📈 Monthly Price Trend")

fig, ax = plt.subplots()
ax.plot(year_data["month_name"], year_data["price"], marker="o")
ax.set_xlabel("Month")
ax.set_ylabel("Price (₹)")
ax.set_title(f"Tomato Prices – {selected_year}")
st.pyplot(fig)

# -------------------------
# Seasonal Baseline
# -------------------------
seasonal_avg = data.groupby("month")["price"].mean().reset_index()

merged = pd.merge(
    year_data,
    seasonal_avg,
    on="month",
    suffixes=("_current", "_seasonal")
)

# -------------------------
# Crash Detection Logic
# -------------------------
merged["deviation_pct"] = (
    (merged["price_current"] - merged["price_seasonal"]) 
    / merged["price_seasonal"]
) * 100

def classify_risk(dev):
    if dev < -30:
        return "🔴 High Crash Risk"
    elif dev < -15:
        return "🟠 Medium Risk"
    else:
        return "🟢 Normal"

merged["risk"] = merged["deviation_pct"].apply(classify_risk)

# -------------------------
# Decision Logic
# -------------------------
def suggest_action(risk):
    if "High" in risk:
        return "Process / Store"
    elif "Medium" in risk:
        return "Hold if possible"
    else:
        return "Sell"

merged["suggested_action"] = merged["risk"].apply(suggest_action)

# -------------------------
# Results Table
# -------------------------
st.subheader("⚖️ AI Decision Output")

st.dataframe(
    merged[[
        "month_name",
        "price_current",
        "price_seasonal",
        "risk",
        "suggested_action"
    ]].rename(columns={
        "month_name":"Month",
        "price_current":"Current Price (₹)",
        "price_seasonal":"Seasonal Avg Price (₹)",
        "risk":"Risk Level",
        "suggested_action":"AI Suggestion"
    }),
    use_container_width=True
)

# -------------------------
# Explanation Section
# -------------------------
st.subheader("🧠 AI Explanation")

st.write(
    "The system compares current month prices with long-term seasonal averages. "
    "If prices fall significantly below normal seasonal levels, it flags a crash risk "
    "and recommends processing or storage instead of immediate sale."
)
