# 第8.5版：优化移动端输入体验，DeFAI替换自定义币1，删除币2，恢复成功的汇率获取方案

import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="币种换算器（第8.5版）", layout="centered")

# ========== 网络检测 ==========
def test_internet_connection():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

# ========== 获取汇率 ==========
def get_btc_usdt(source="binance"):
    try:
        if source == "binance":
            r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
            return float(r.json()["price"])
        elif source == "huobi":
            r = requests.get("https://api.huobi.pro/market/trade?symbol=btcusdt", timeout=5)
            return float(r.json()["tick"]["data"][0]["price"])
    except:
        return None

def get_usd_cny():
    try:
        r = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=CNY", timeout=5)
        return float(r.json()["rates"]["CNY"])
    except:
        return None

# ========== 页面开始 ==========
st.title("💱 币种换算器（第8.5版）")

# 网络状态
if test_internet_connection():
    st.success("✅ 网络连接正常（已连接 Google）")
else:
    st.error("❌ 网络连接异常，请检查您的网络。")
    st.stop()

# 汇率源选择
source = st.selectbox("选择汇率数据来源", ["binance", "huobi"], format_func=lambda x: "币安" if x == "binance" else "火币")

# 获取实时汇率
btc_usdt = get_btc_usdt(source)
usd_cny = get_usd_cny()
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if not btc_usdt or not usd_cny:
    st.error("❌ 无法获取实时汇率，请稍后再试。")
    st.stop()

# 汇率换算
btc_cny = btc_usdt * usd_cny
sats_per_btc = 100_000_000
sats_usd = btc_usdt / sats_per_btc
sats_cny = btc_cny / sats_per_btc
defai_price_sats = 150  # 1 DeFAI = 150 sats

# ========== 输入币种 ==========
st.markdown("### 输入任意币种的数值，其它自动换算")

input_option = st.selectbox("选择输入币种", ["CNY（人民币）", "USD/T(美元/泰达)", "BTC(比特币)", "SATS（聪）", "DeFAI"])
input_str = st.text_input(f"输入 {input_option} 数量", value="", key="main_input")

try:
    input_value = float(input_str) if input_str else 0.0
except:
    st.warning("⚠️ 请输入有效数字")
    st.stop()

# ========== 核心换算 ==========
if input_option == "CNY（人民币）":
    usd = input_value / usd_cny
    btc = usd / btc_usdt
elif input_option == "USD/T(美元/泰达)":
    usd = input_value
    btc = usd / btc_usdt
elif input_option == "BTC(比特币)":
    btc = input_value
    usd = btc * btc_usdt
elif input_option == "SATS（聪）":
    btc = input_value / sats_per_btc
    usd = btc * btc_usdt
elif input_option == "DeFAI":
    sats = input_value * defai_price_sats
    btc = sats / sats_per_btc
    usd = btc * btc_usdt
else:
    usd = btc = 0

# 结果换算
cny = usd * usd_cny
sats = btc * sats_per_btc
defai = sats / defai_price_sats

# ========== 显示换算结果 ==========
st.markdown("### 💹 实时换算结果")

col1, col2 = st.columns(2)
with col1:
    st.number_input("CNY（人民币）", value=round(cny, 6), disabled=True)
    st.number_input("BTC（比特币）", value=round(btc, 8), disabled=True)
    st.number_input("DeFAI", value=round(defai, 6), disabled=True)
with col2:
    st.number_input("USD/T（美元/泰达）", value=round(usd, 6), disabled=True)
    st.number_input("SATS（聪）", value=round(sats, 2), disabled=True)

st.caption(f"📅 汇率更新时间：{timestamp}")
st.caption(f"📈 BTC/USDT: {btc_usdt}, USD/CNY: {usd_cny}")

# ========== 自动刷新 ==========
st.checkbox("每60秒自动刷新", value=False, key="autorefresh")
if st.session_state["autorefresh"]:
    st.experimental_rerun()
