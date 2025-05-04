import streamlit as st
import requests
import time

st.set_page_config(page_title="BTC/USDT 汇率", layout="centered")
st.title("📈 BTC 与 USDT 汇率查询（第4版解决方案）")
st.markdown("数据来源：Binance 公共 API（无需 API Key）")

# 测试网络连通性
try:
    test = requests.get("https://api.binance.com", timeout=5)
    st.success("🌐 网络连接正常（Binance 可访问）")
except:
    st.error("❌ 无法访问 Binance 接口，可能是网络或平台限制")
    st.stop()

# 自动刷新开关
auto_refresh = st.checkbox("每 60 秒自动刷新", value=False)
status = st.empty()

# 获取汇率（来自 Binance）
@st.cache_data(ttl=60)
def get_rates():
    try:
        btc_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        usdt_cny_url = "https://api.binance.com/api/v3/ticker/price?symbol=USDTBUSD"  # 近似 1:1

        btc_res = requests.get(btc_url, timeout=10)
        usdt_res = requests.get(usdt_cny_url, timeout=10)

        btc_data = btc_res.json()
        usdt_data = usdt_res.json()

        btc_usdt = float(btc_data["price"])
        usdt_cny = 7.1  # Binance 无人民币对，手动设置汇率（或使用国内汇率源）
        btc_cny = btc_usdt * usdt_cny

        return btc_usdt, usdt_cny, btc_cny

    except Exception as e:
        st.error(f"❌ 异常：{e}")
        return None, None, None

# 展示函数
def display_rates():
    btc_usdt, usdt_cny, btc_cny = get_rates()
    if btc_usdt is None:
        status.error("❌ 获取汇率失败，请稍后再试。")
    else:
        status.success("✅ 汇率获取成功")
        st.metric("BTC / USDT", f"{btc_usdt:.2f} USDT")
        st.metric("USDT / CNY", f"{usdt_cny:.2f} 元")
        st.metric("BTC / CNY", f"{btc_cny:.2f} 元")

# 自动刷新
if auto_refresh:
    while True:
        display_rates()
        time.sleep(60)
        st.rerun()
else:
    display_rates()
