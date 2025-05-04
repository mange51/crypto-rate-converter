import streamlit as st
import requests
import time

st.set_page_config(page_title="BTC/USDT 汇率", layout="centered")

st.title("📈 BTC 与 USDT 汇率查询")
st.markdown("数据来源：CoinGecko API")

# ✅ 网络连接测试
try:
    test = requests.get("https://www.google.com", timeout=5)
    st.success("🌐 网络连接正常（可以访问外网）")
except:
    st.error("❌ 无法访问外网，可能是当前平台（如 Render）限制了外部请求")
    st.stop()

# 自动刷新选项
auto_refresh = st.checkbox("每 60 秒自动刷新", value=False)

# 状态容器
status = st.empty()

# ✅ 获取 CoinGecko 汇率并输出调试信息
@st.cache_data(ttl=60)
def get_rates_from_coingecko():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,tether",
            "vs_currencies": "cny"
        }
        response = requests.get(url, params=params, timeout=10)

        # 🔍 调试输出状态码和原始返回内容
        st.subheader("📦 接口调试信息")
        st.code(f"状态码: {response.status_code}\n返回内容:\n{response.text}")

        if response.status_code != 200:
            return None, None, None

        data = response.json()
        btc_cny = data["bitcoin"]["cny"]
        usdt_cny = data["tether"]["cny"]
        btc_usdt = btc_cny / usdt_cny
        return btc_usdt, usdt_cny, btc_cny
    except Exception as e:
        st.error(f"❌ 异常：{e}")
        return None, None, None

# 显示汇率
def display_rates():
    btc_usdt, usdt_cny, btc_cny = get_rates_from_coingecko()

    if btc_usdt is None:
        status.error("❌ 获取汇率失败，请稍后再试。")
    else:
        status.success("✅ 汇率获取成功")
        st.metric("BTC / USDT", f"{btc_usdt:.2f} USDT")
        st.metric("USDT / CNY", f"{usdt_cny:.2f} 元")
        st.metric("BTC / CNY", f"{btc_cny:.2f} 元")

# 页面控制逻辑
if auto_refresh:
    while True:
        display_rates()
        time.sleep(60)
        st.rerun()
else:
    display_rates()
