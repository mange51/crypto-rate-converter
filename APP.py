import streamlit as st
import requests

st.set_page_config(page_title="BTC 汇率查询 - 第7版", layout="centered")
st.title("💱 BTC 汇率查询 - 第7版")

# 平台选项
platforms = ["Binance", "火币 (Huobi)", "CoinMarketCap", "CoinGecko"]
platform = st.selectbox("选择数据平台：", platforms)

# 网络连接检测
def check_network():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

# 获取 Binance 汇率
def get_binance_rates():
    try:
        btc_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        btc_response = requests.get(btc_url, timeout=5)
        btc_response.raise_for_status()
        btc_usdt = float(btc_response.json()['price'])
        usdt_cny = 7.2  # 默认值
        return btc_usdt, usdt_cny, "✅ Binance 成功（CNY为默认）"
    except Exception as e:
        return None, None, f"❌ Binance 失败：{e}"

# 获取火币汇率
def get_huobi_rates():
    try:
        btc_url = "https://api.huobi.pro/market/detail/merged?symbol=btcusdt"
        btc_response = requests.get(btc_url, timeout=5)
        btc_response.raise_for_status()
        btc_usdt = float(btc_response.json()["tick"]["close"])
        usdt_cny = 7.2  # 默认值
        return btc_usdt, usdt_cny, "✅ 火币 成功（CNY为默认）"
    except Exception as e:
        return None, None, f"❌ 火币 失败：{e}"

# 获取 CoinMarketCap 汇率
def get_coinmarketcap_rate():
    try:
        url = "https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert=CNY"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()[0]
        btc_usdt = float(data["price_usd"])
        btc_cny = float(data["price_cny"])
        usdt_cny = btc_cny / btc_usdt
        return btc_usdt, usdt_cny, "✅ CoinMarketCap 成功"
    except Exception as e:
        return None, None, f"❌ CoinMarketCap 失败：{e}"

# 获取 CoinGecko 汇率
def get_coingecko_rate():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,cny"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()["bitcoin"]
        btc_usdt = float(data["usd"])
        btc_cny = float(data["cny"])
        usdt_cny = btc_cny / btc_usdt
        return btc_usdt, usdt_cny, "✅ CoinGecko 成功"
    except Exception as e:
        return None, None, f"❌ CoinGecko 失败：{e}"

# 获取汇率
def get_rates(platform):
    if platform == "Binance":
        return get_binance_rates()
    elif platform == "火币 (Huobi)":
        return get_huobi_rates()
    elif platform == "CoinMarketCap":
        return get_coinmarketcap_rate()
    elif platform == "CoinGecko":
        return get_coingecko_rate()
    else:
        return None, None, "❌ 未知平台"

# 主逻辑
if st.button("获取汇率"):
    if check_network():
        st.success("🌐 网络连接正常（已连接Google）")
        btc_usdt, usdt_cny, status = get_rates(platform)
        if btc_usdt and usdt_cny:
            st.write(status)
            st.write(f"🔶 当前 BTC/USDT 汇率：`{btc_usdt}`")
            st.write(f"💵 当前 USDT/CNY 汇率：`{usdt_cny}`")
            st.write(f"💰 当前 BTC/CNY 汇率：`{btc_usdt * usdt_cny:.2f}`")
        else:
            st.error("获取汇率失败，请稍后再试。")
            st.write(status)
    else:
        st.error("❌ 无法访问 Google，可能断网或被墙。")

st.caption("© 第7版 - 支持 Binance、火币、CoinMarketCap 和 CoinGecko")
