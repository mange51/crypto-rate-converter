# 第8.3版：优化移动端输入体验，解决交互不便问题

import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="币种转换器", layout="centered")

# ========== 获取网络连通性 ==========
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
if "custom1_name" not in st.session_state:
    st.session_state["custom1_name"] = "自定义币1"
    st.session_state["custom2_name"] = "自定义币2"
    st.session_state["custom1_price"] = 100  # 单位：聪
    st.session_state["custom2_price"] = 200  # 单位：聪

# ========== 页面顶部 ==========
st.title("💱 币种换算工具（第8.3版）")

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
    "CNY（人民币）", "USD/T(美元/泰达)", "BTC(比特币)", "SATS（聪）",
    st.session_state["custom1_name"], st.session_state["custom2_name"]
])

# 用户输入
input_value = st.number_input(f"输入 {input_option} 数量", min_value=0.0, value=0.0, step=1.0)

# 自定义币种设置
with st.expander("⚙️ 自定义币设置", expanded=False):
    st.session_state["custom1_name"] = st.text_input("自定义币1名称", st.session_state["custom1_name"])
    st.session_state["custom2_name"] = st.text_input("自定义币2名称", st.session_state["custom2_name"])
    st.session_state["custom1_price"] = st.number_input(f"{st.session_state['custom1_name']} 单价（聪）", value=st.session_state["custom1_price"])
    st.session_state["custom2_price"] = st.number_input(f"{st.session_state['custom2_name']} 单价（聪）", value=st.session_state["custom2_price"])

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
elif input_option == st.session_state["custom1_name"]:
    sats = input_value * st.session_state["custom1_price"]
    btc = sats / sats_per_btc
    usd = btc * btc_usdt
elif input_option == st.session_state["custom2_name"]:
    sats = input_value * st.session_state["custom2_price"]
    btc = sats / sats_per_btc
    usd = btc * btc_usdt
else:
    usd = btc = 0

cny = usd * usd_cny
sats = btc * sats_per_btc
custom1 = sats / st.session_state["custom1_price"]
custom2 = sats / st.session_state["custom2_price"]

# ========== 显示结果 ==========
st.markdown("### 💹 换算结果（实时更新）")

col1, col2 = st.columns(2)
with col1:
    st.number_input("CNY（人民币）", value=round(cny, 6), disabled=True)
    st.number_input("BTC（比特币）", value=round(btc, 8), disabled=True)
    st.number_input(st.session_state["custom1_name"], value=round(custom1, 6), disabled=True)
with col2:
    st.number_input("USD/T（美元/泰达）", value=round(usd, 6), disabled=True)
    st.number_input("SATS（聪）", value=round(sats, 2), disabled=True)
    st.number_input(st.session_state["custom2_name"], value=round(custom2, 6), disabled=True)

st.caption(f"📅 汇率更新时间：{timestamp}")
st.caption(f"📈 BTC/USDT: {btc_usdt}, USD/CNY: {usd_cny}")

# ========== 自动刷新 ==========
st_autorefresh = st.checkbox("自动每60秒刷新", value=True)
if st_autorefresh:
    st.experimental_rerun()
