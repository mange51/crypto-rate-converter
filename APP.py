import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="多币种换算器 8.8版", layout="centered")

# ---------------------- 函数：格式化数字 ----------------------
def format_number(value):
    if isinstance(value, (int, float)):
        if value >= 1:
            return f"{value:,.2f}".rstrip('0').rstrip('.')
        elif value >= 0.01:
            return f"{value:,.6f}".rstrip('0').rstrip('.')
        else:
            return f"{value:,.8f}".rstrip('0').rstrip('.')
    return value

# ---------------------- 函数：获取汇率 ----------------------
def fetch_binance_btc_usdt():
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
        price = float(response.json()["price"])
        return price, datetime.now()
    except:
        return None, None

def fetch_usd_cny():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url, timeout=5)
        data = response.json()
        rate = data["rates"]["CNY"]
        update_time = datetime.fromtimestamp(data["time_last_update_unix"])
        return rate, update_time
    except:
        return None, None

# ---------------------- 汇率初始化 ----------------------
st.markdown("### 🌐 网络连接检测中...")
try:
    requests.get("https://www.google.com", timeout=5)
    st.success("网络连接正常 ✅")
except:
    st.error("❌ 无法连接互联网，请检查网络")
    st.stop()

# ---------------------- 获取汇率数据 ----------------------
btc_usdt, btc_time = fetch_binance_btc_usdt()
usd_cny, cny_time = fetch_usd_cny()

if btc_usdt is None or usd_cny is None:
    st.error("❌ 获取汇率失败，请稍后再试。")
    st.stop()

# ---------------------- 汇率换算 ----------------------
usdt = 1.0
btc = 1 / btc_usdt
cny = usd_cny
sats_per_btc = 100_000_000
sats = btc * sats_per_btc

# ---------------------- 汇率更新时间显示 ----------------------
st.markdown(f"🕒 汇率更新时间：BTC/USDT：{btc_time.strftime('%Y-%m-%d %H:%M:%S')}，USD/CNY：{cny_time.strftime('%Y-%m-%d %H:%M:%S')}")

# ---------------------- 用户输入区 ----------------------
st.markdown("## 💱 输入任意币种进行换算")

# 币种输入
col1, col2 = st.columns(2)
with col1:
    input_currency = st.selectbox("选择输入币种", ["CNY(人民币)", "USDT(美元)", "BTC(比特币)", "SATS(聪)", "DeFAI"])
with col2:
    input_value = st.number_input("输入金额", min_value=0.0, step=1.0, format="%.8f", key="input_value")

# DeFAI 单价
defai_price = st.number_input("DeFAI 单价：SATS(聪)", min_value=0.0, value=100.0, step=1.0, format="%.8f")

# ---------------------- 币种计算逻辑 ----------------------
defai_sats = defai_price
btc_value = 0

if input_currency == "CNY(人民币)":
    usdt_value = input_value / usd_cny
    btc_value = usdt_value / btc_usdt
elif input_currency == "USDT(美元)":
    usdt_value = input_value
    btc_value = usdt_value / btc_usdt
elif input_currency == "BTC(比特币)":
    btc_value = input_value
    usdt_value = btc_value * btc_usdt
elif input_currency == "SATS(聪)":
    btc_value = input_value / sats_per_btc
    usdt_value = btc_value * btc_usdt
elif input_currency == "DeFAI":
    sats_total = input_value * defai_sats
    btc_value = sats_total / sats_per_btc
    usdt_value = btc_value * btc_usdt

cny_value = usdt_value * usd_cny
sats_value = btc_value * sats_per_btc
defai_value = sats_value / defai_sats if defai_sats > 0 else 0

# ---------------------- 结果显示 ----------------------
st.markdown("## 📊 换算结果")

def display(label, value):
    st.write(f"**{label}**：{format_number(value)}")

col1, col2 = st.columns(2)
with col1:
    display("CNY(人民币)", cny_value)
    display("BTC(比特币)", btc_value)
    display("DeFAI", defai_value)
with col2:
    display("USDT(美元)", usdt_value)
    display("SATS(聪)", sats_value)

# ---------------------- 自动刷新功能 ----------------------
st_autorefresh = st.empty()
st_autorefresh.info("页面将每 60 秒自动刷新汇率数据。")
st.experimental_rerun() if st_autorefresh.button("立即刷新") else time.sleep(60)
