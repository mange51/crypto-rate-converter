import streamlit as st
import requests

st.set_page_config(page_title="BTC 汇率查询 - 第8版", layout="centered")
st.title("💱 BTC 汇率查询 - 第8版")

# 网络连接检测（访问 Google）
def check_network():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

# 显示网络状态
if check_network():
    st.success("🌐 网络连接正常（已连接 Google）")
else:
    st.error("❌ 网络连接失败，无法访问 Google")

# 获取币安 BTC/USDT 汇率
def get_binance_btc_usdt():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        price = float(resp.json()['price'])
        return price, "✅ Binance 成功"
    except Exception as e:
        return None, f"❌ Binance 失败：{e}"

# 获取火币 BTC/USDT 汇率
def get_huobi_btc_usdt():
    try:
        url = "https://api.huobi.pro/market/detail/merged?symbol=btcusdt"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        price = float(resp.json()['tick']['close'])
        return price, "✅ 火币 成功"
    except Exception as e:
        return None, f"❌ 火币 失败：{e}"

# 获取 USD/CNY 汇率（使用 exchangerate.host）
def get_usd_cny_rate():
    try:
        url = "https://api.exchangerate.host/latest?base=USD&symbols=CNY"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return float(data['rates']['CNY']), "✅ USD/CNY 获取成功"
    except Exception as e:
        return None, f"❌ USD/CNY 获取失败：{e}"

st.subheader("📊 汇率查询")

platform = st.selectbox("选择平台：", ["Binance", "火币 (Huobi)"])

if st.button("获取 BTC 和 USD/CNY 汇率"):
    if platform == "Binance":
        btc_usdt, status = get_binance_btc_usdt()
    else:
        btc_usdt, status = get_huobi_btc_usdt()

    usd_cny, cny_status = get_usd_cny_rate()

    if btc_usdt:
        st.write(status)
        st.write(f"🔶 BTC/USDT 汇率：`{btc_usdt}`")
    else:
        st.error("无法获取 BTC 汇率")
        st.write(status)

    if usd_cny:
        st.write(cny_status)
        st.write(f"💵 USD/CNY 汇率：`{usd_cny}`")
        if btc_usdt:
            st.write(f"💰 BTC/CNY 汇率：`{btc_usdt * usd_cny:.2f}`")
    else:
        st.error("无法获取 USD/CNY 汇率")
        st.write(cny_status)

st.caption("© 第8版 - Binance / 火币 BTC 汇率 + 实时 USD/CNY 汇率")
