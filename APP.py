# 第8.5版：修复汇率获取，固定 DeFAI 名称，删除自定义币种2，优化移动端输入体验

import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="币种换算工具", layout="centered")

# ========== 网络连接检测 ==========
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
            price = float(r.json()["price"])
        elif source == "huobi":
            r = requests.get("https://api.huobi.pro/market/trade?symbol=btcusdt", timeout=5)
            price = float(r.json()["tick"]["data"][0]["price"])
        else:
            price = None
        return price
    except Exception as e:
        return None

def get_usd_cny():
    try:
        r = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=CNY", timeout=5)
        return float(r.json()["rates"]["CNY"])
    except:
        return None

# ========== 初始化 ==========
if "defai_price" not in st.session_state:
    st.session_state["defai_price"] = 100  # 单位：聪

# ========== 页面顶部 ==========
st.title("💱 币种换算工具（第8.5版）")

# 网络检测
if test_internet_connection():
    st.success("✅ 网络连接正常（已连接 Google）")
else:
    st.error("❌ 网络连接异常，请检查您的网络。")

# 选择数据来源
source = st.selectbox("选择汇率数据来源", ["binance", "huobi"], format_func=lambda x: "币安" if x == "binance" else "火币")

# 获取汇率
btc_usdt = get_btc_usdt(source)
usd_cny = get_usd_cny()
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if not btc_usdt or not usd_cny:
    st.error("❌ 无法获取实时汇率，请稍后再试。")
    st.stop()

# 计算实际汇率
btc_cny = btc_usdt * usd_cny
sats_per_btc = 100_000_000
sats_usd = btc_usdt / sats_per_btc
sats_cny = btc_cny / sats_per_btc

# ========== 输入币种 ==========
st.markdown("### 请输入任意一个币种的数值，其他币种将自动换算：")

input_option = st.selectbox("选择输入币种", [
    "CNY（人民币）", "USD/T(美元/泰达)", "BTC(比特币)", "SATS（聪）", "DeFAI"
])

# 用户输入
input_value = st.number_input(f"输入 {input_option} 数量", min_value=0.0, value=0.0, step=1.0)

# DeFAI 价格设置
with st.expander("⚙️ DeFAI 设置", expanded=False):
    st.session_state["defai_price"] = st.number_input("DeFAI 单价（聪）", value=st.session_state["defai_price"])

# ========== 计算结果 ==========
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
    sats = input_value * st.session_state["defai_price"]
    btc = sats / sats_per_btc
    usd = btc * btc_usdt
else:
    usd = btc = 0

cny = usd * usd_cny
sats = btc * sats_per_btc
defai = sats / st.session_state["defai_price"]

# ========== 显示结果 ==========
st.markdown("### 💹 换算结果（实时更新）")

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
st_autorefresh = st.checkbox("自动每60秒刷新", value=True)
if st_autorefresh:
    st.experimental_rerun()
