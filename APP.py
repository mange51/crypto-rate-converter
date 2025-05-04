import streamlit as st
import requests
import time

st.set_page_config(page_title="BTC/USDT 汇率", layout="centered")

st.title("📈 BTC 与 USDT 汇率查询")
st.markdown("数据来源：CoinGecko API（全球可访问）")

# 自动刷新
auto_refresh = st.checkbox("每 60 秒自动刷新", value=False)

# 状态显示容器
status = st.empty()

@st.cache_data(ttl=60)
def get_rates_from_coingecko():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,tether",
            "vs_currencies": "cny"
        }
        response = requests.get(url, params=params, timeout=10).json()
        btc_cny = response["bitcoin"]["cny"]
        usdt_cny = response["tether"]["cny"]
        btc_usdt = btc_cny / usdt_cny
        return btc_usdt, usdt_cny, btc_cny
    except:
        return None, None, None

def display_rates():
    btc_usdt, usdt_cny, btc_cny = get_rates_from_coingecko()

    if btc_usdt is None:
        status.error("❌ 获取汇率失败，请稍后再试。")
    else:
        status.success("✅ 汇率获取成功")
        st.metric("BTC / USDT", f"{btc_usdt:.2f} USDT")
        st.metric("USDT / CNY", f"{usdt_cny:.2f} 元")
        st.metric("BTC / CNY", f"{btc_cny:.2f} 元")

if auto_refresh:
    while True:
        display_rates()
        time.sleep(60)
        st.rerun()
else:
    display_rates()
