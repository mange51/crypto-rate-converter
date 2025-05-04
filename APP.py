import streamlit as st
import requests
import time

st.set_page_config(page_title="BTC/USDT 汇率", layout="centered")

st.title("📈 BTC 与 USDT 汇率查询")
st.markdown("使用 OKX 与火币接口，支持实时刷新。")

# 数据源选项
source = st.selectbox("选择汇率来源", ["OKX", "火币"])

# 自动刷新
auto_refresh = st.checkbox("每 60 秒自动刷新", value=False)

# 显示加载状态
status = st.empty()

@st.cache_data(ttl=60)
def get_okx_rates():
    try:
        btc_resp = requests.get("https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT").json()
        btc_price = float(btc_resp["data"][0]["last"])
        cny_resp = requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-CNY").json()
        usdt_to_cny = float(cny_resp["data"][0]["last"])
        return btc_price, usdt_to_cny
    except:
        return None, None

@st.cache_data(ttl=60)
def get_huobi_rates():
    try:
        btc_resp = requests.get("https://api.huobi.pro/market/detail/merged?symbol=btcusdt").json()
        btc_price = float(btc_resp["tick"]["close"])
        cny_resp = requests.get("https://api.huobi.pro/market/detail/merged?symbol=usdtcny").json()
        usdt_to_cny = float(cny_resp["tick"]["close"])
        return btc_price, usdt_to_cny
    except:
        return None, None

# 主循环
def display_rates():
    if source == "OKX":
        btc, usdt = get_okx_rates()
    else:
        btc, usdt = get_huobi_rates()

    if btc is None or usdt is None:
        st.error("❌ 获取汇率失败，请稍后再试。")
    else:
        st.success("✅ 汇率获取成功")
        st.metric("BTC/USDT", f"{btc:.2f} USDT")
        st.metric("USDT/CNY", f"{usdt:.2f} 元")
        st.metric("BTC/CNY", f"{btc * usdt:.2f} 元")

# 自动刷新逻辑
if auto_refresh:
    while True:
        display_rates()
        time.sleep(60)
        st.rerun()
else:
    display_rates()
