import streamlit as st
import requests

st.set_page_config(page_title="BTC 汇率查询 - 第8版", layout="centered")
st.title("💱 BTC 汇率查询 - 第8版")

# 平台选项
platforms = ["Binance", "火币 (Huobi)"]
platform = st.selectbox("选择数据平台：", platforms)

# 网络连接检测
def check_network():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

# 获取人民币兑美元汇率（即 USD/CNY）
def get_usd_cny_rate():
    try:
        url = "https://api.exchangerate.host/latest?base=USD&symbols=CNY"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        usd_cny = float(response.json()["rates"]["CNY"])
        return usd_cny, "✅ 获取 USD/CNY 成功"
    except Exception as e:
        return None, f"❌ 获取 USD/CNY 失败：{e}"

# 获取 Binance BTC/USDT 汇率
def get_binance_rate():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        btc_usdt = float(response.json()["price"])
        return btc_usdt, "✅ Binance 获取成功"
    except Exception as e:
        return None, f"❌ Binance 获取失败：{e}"

# 获取火币 BTC/USDT 汇率
def get_huobi_rate():
    try:
        url = "https://api.huobi.pro/market/detail/merged?symbol=btcusdt"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        btc_usdt = float(response.json()["tick"]["close"])
        return btc_usdt, "✅ 火币 获取成功"
    except Exception as e:
        return None, f"❌ 火币 获取失败：{e}"

# 汇率获取逻辑
def get_rates(platform):
    if platform == "Binance":
        return get_binance_rate()
    elif platform == "火币 (Huobi)":
        return get_huobi_rate()
    else:
        return None, "❌ 未知平台"

# 主按钮逻辑
if st.button("获取汇率"):
    if check_network():
        st.success("🌐 网络连接正常（已连接Google）")

        btc_usdt, status1 = get_rates(platform)
        usd_cny, status2 = get_usd_cny_rate()

        if btc_usdt and usd_cny:
            btc_cny = btc_usdt * usd_cny
            st.write(status1)
            st.write(status2)
            st.write(f"🔶 当前 BTC/USDT 汇率：`{btc_usdt}`")
            st.write(f"💵 当前 USD/CNY 汇率：`{usd_cny}`")
            st.write(f"💰 当前 BTC/CNY 汇率：`{btc_cny:.2f}`")
        else:
            st.error("获取汇率失败，请稍后再试。")
            st.write(status1)
            st.write(status2)
    else:
        st.error("❌ 无法访问 Google，可能断网或被墙。")

st.caption("© 第8版 - 支持 Binance 和火币，自动获取 USD/CNY 汇率")
