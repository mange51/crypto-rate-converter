import streamlit as st
import requests
import socket

# ---------------- 网络连通性检测 ----------------
def check_network():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except OSError:
        return False

# ---------------- 汇率获取函数 ----------------
def get_binance_rate():
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=10)
        data = response.json()
        return float(data["price"])
    except Exception as e:
        return f"币安获取失败：{e}"

def get_huobi_rate():
    try:
        response = requests.get("https://api.huobi.pro/market/detail/merged?symbol=btcusdt", timeout=10)
        data = response.json()
        return float(data["tick"]["close"])
    except Exception as e:
        return f"火币获取失败：{e}"

def get_usd_to_cny():
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        data = response.json()
        return float(data["rates"]["CNY"])
    except Exception as e:
        return f"USD/CNY 获取失败：{e}"

# ---------------- Streamlit 页面 ----------------
st.set_page_config(page_title="BTC 汇率转换工具（第8版）", layout="centered")
st.title("📈 BTC 汇率转换工具（第8版）")

# 检测网络
st.subheader("🌐 网络连接测试")
if check_network():
    st.success("网络连接正常（可以访问 Google）")
else:
    st.error("无法访问 Google，当前网络可能无法连接外网")

# 汇率查询
st.subheader("💱 汇率信息")
binance = get_binance_rate()
huobi = get_huobi_rate()
usd_to_cny = get_usd_to_cny()

col1, col2 = st.columns(2)
with col1:
    st.write("### Binance BTC/USDT")
    st.success(binance if isinstance(binance, float) else str(binance))

with col2:
    st.write("### Huobi BTC/USDT")
    st.success(huobi if isinstance(huobi, float) else str(huobi))

st.write("### USD → CNY 汇率")
if isinstance(usd_to_cny, float):
    st.success(f"1 USD ≈ {usd_to_cny:.4f} CNY")
else:
    st.error(usd_to_cny)

# BTC/CNY 计算显示
st.subheader("💰 BTC 兑人民币价格")
if isinstance(binance, float) and isinstance(usd_to_cny, float):
    btc_cny = binance * usd_to_cny
    st.info(f"当前 BTC ≈ {btc_cny:,.2f} 元人民币（基于币安价格）")
elif isinstance(huobi, float) and isinstance(usd_to_cny, float):
    btc_cny = huobi * usd_to_cny
    st.info(f"当前 BTC ≈ {btc_cny:,.2f} 元人民币（基于火币价格）")
else:
    st.warning("由于部分汇率获取失败，无法计算 BTC 对人民币价格。")
