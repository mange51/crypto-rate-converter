import streamlit as st
import requests
import time

st.set_page_config(page_title="BTC/USDT 汇率", layout="centered")
st.title("📈 BTC 与 USDT 汇率查询")
st.markdown("数据来源：OKX 公共 API")

# ✅ 网络测试
try:
    test = requests.get("https://www.okx.com", timeout=5)
    st.success("🌐 网络连接正常")
except:
    st.error("❌ 无法访问外网（Render 限制）")
    st.stop()

# 自动刷新选项
auto_refresh = st.checkbox("每 60 秒自动刷新", value=False)
status = st.empty()

# ✅ 获取汇率
@st.cache_data(ttl=60)
def get_rates_from_okx():
    try:
        btc_url = "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT"
        usdt_url = "https://www.okx.com/api/v5/market/ticker?instId=USDT-CNY"

        btc_data = requests.get(btc_url, timeout=10).json()
        usdt_data = requests.get(usdt_url, timeout=10).json()

        # 打印调试信息
        st.subheader("📦 响应调试信息")
        st.code(f"BTC 数据:\n{btc_data}")
        st.code(f"USDT 数据:\n{usdt_data}")

        if "data" not in btc_data or "data" not in usdt_data:
            raise ValueError("API 返回数据缺失，可能是请求格式错误或API问题。")

        btc_usdt = float(btc_data["data"][0]["last"])
        usdt_cny = float(usdt_data["data"][0]["last"])
        btc_cny = btc_usdt * usdt_cny

        return btc_usdt, usdt_cny, btc_cny
    except Exception as e:
        st.error(f"❌ 异常：{e}")
        return None, None, None

# 显示汇率
def display_rates():
    btc_usdt, usdt_cny, btc_cny = get_rates_from_okx()
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
