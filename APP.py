# app.py - 第9.0版：结构优化 + UI调整 + 千位符 + 完整换算逻辑

import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="币种换算器", layout="centered")

# 初始化 session_state
for key in ["selected_currency", "input_amount", "defai_price_sats"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ---------------------- 获取汇率函数 ----------------------
@st.cache_data(ttl=60)
def get_rates():
    try:
        # 获取 BTC/USDT 汇率（使用币安）
        binance_resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
        binance_data = binance_resp.json()
        btc_usdt = float(binance_data["price"])
        btc_usdt_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 获取 USD/CNY 汇率（使用 exchangerate.host）
        fx_resp = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=CNY", timeout=5)
        fx_data = fx_resp.json()
        usd_cny = float(fx_data["rates"]["CNY"])
        usd_cny_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "btc_usdt": btc_usdt,
            "btc_usdt_time": btc_usdt_time,
            "usd_cny": usd_cny,
            "usd_cny_time": usd_cny_time
        }
    except Exception as e:
        st.error(f"❌ 汇率获取失败：{e}")
        return None

rates = get_rates()
if not rates:
    st.stop()

# ---------------------- 标题 ----------------------
st.markdown("## 💱 一币输入，多币立算")
st.caption(f"🕒 汇率更新时间 - BTC/USDT: {rates['btc_usdt_time']} | USD/CNY: {rates['usd_cny_time']}")

# ---------------------- 常量 ----------------------
BTC_USDT = rates["btc_usdt"]
USD_CNY = rates["usd_cny"]
SATOSHI_PER_BTC = 100_000_000

# 默认 DeFAI 单价（单位为聪）
if st.session_state["defai_price_sats"] == "":
    st.session_state["defai_price_sats"] = 100.0

# ---------------------- 币种输入 ----------------------
currency_names = {
    "cny": "CNY(人民币)",
    "usdt": "USDT(美元)",
    "btc": "BTC(比特币)",
    "sats": "SATS(聪)",
    "defai": "DeFAI"
}
selected = st.selectbox("选择要输入的币种", list(currency_names.keys()), format_func=lambda x: currency_names[x])

input_val = st.number_input(
    f"请输入 {currency_names[selected]} 数量",
    min_value=0.0,
    format="%.8f",
    key="input_amount"
)

# ---------------------- DeFAI 单价输入 ----------------------
defai_price_sats = st.number_input(
    "DeFAI 单价：SATS(聪)",
    min_value=0.0,
    format="%.4f",
    key="defai_price_sats"
)

# ---------------------- 换算逻辑 ----------------------
def convert_all(selected, input_val, defai_price):
    result = {}

    if selected == "cny":
        usdt = input_val / USD_CNY
        btc = usdt / BTC_USDT
    elif selected == "usdt":
        usdt = input_val
        btc = usdt / BTC_USDT
    elif selected == "btc":
        btc = input_val
    elif selected == "sats":
        btc = input_val / SATOSHI_PER_BTC
    elif selected == "defai":
        sats = input_val * defai_price
        btc = sats / SATOSHI_PER_BTC
    else:
        return {}

    sats = btc * SATOSHI_PER_BTC
    usdt = btc * BTC_USDT
    cny = usdt * USD_CNY
    defai = sats / defai_price if defai_price != 0 else 0

    result["cny"] = cny
    result["usdt"] = usdt
    result["btc"] = btc
    result["sats"] = sats
    result["defai"] = defai
    return result

results = convert_all(selected, input_val, defai_price_sats)

# ---------------------- 显示换算结果 ----------------------
st.markdown("### 📊 换算结果")
def fmt(val):
    if val >= 1000:
        return f"{val:,.4f}".rstrip("0").rstrip(".")
    else:
        return f"{val:.8f}".rstrip("0").rstrip(".")

for key in ["cny", "usdt", "btc", "sats", "defai"]:
    if key != selected:
        st.text_input(currency_names[key], value=fmt(results.get(key, 0)), disabled=True)

# ---------------------- 底部设置 ----------------------
with st.expander("⚙️ 设置"):
    st.selectbox("汇率平台（当前固定为币安+exchangerate.host）", ["Binance + exchangerate.host"], index=0, disabled=True)
    refresh = st.slider("自动刷新时间（秒）", 10, 300, 60)
    st.caption("数据每次页面刷新或间隔时间后自动更新")

# ---------------------- 自动刷新 ----------------------
time.sleep(0.1)
st.experimental_rerun()
