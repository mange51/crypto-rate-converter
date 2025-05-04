# AYY_v5.py
import streamlit as st
import requests

st.set_page_config(page_title="第5版 汇率查询", layout="centered")
st.title("💱 第5版：多平台汇率查询工具")
st.markdown("支持平台：**OKX、火币、币安、币世界、Bitget**，单位：人民币 CNY")

# 数据源选项
data_sources = ["OKX", "火币", "币安", "币世界", "Bitget"]
source = st.selectbox("选择汇率数据源：", data_sources)

# 网络连接测试
def test_connection():
    try:
        response = requests.get("https://api.okx.com", timeout=5)
        return response.status_code == 200
    except:
        return False

st.markdown("📡 网络状态：" + ("✅ 正常" if test_connection() else "❌ 异常"))

# 汇率获取函数
def get_rates(source):
    try:
        if source == "OKX":
            btc_url = "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT"
            cny_url = "https://www.okx.com/api/v5/market/ticker?instId=USDT-CNY"
            btc_usdt = float(requests.get(btc_url).json()["data"][0]["last"])
            usdt_cny = float(requests.get(cny_url).json()["data"][0]["last"])
            return btc_usdt, usdt_cny, btc_usdt * usdt_cny

        elif source == "火币":
            btc_url = "https://api.huobi.pro/market/detail/merged?symbol=btcusdt"
            btc_usdt = float(requests.get(btc_url).json()["tick"]["close"])
            usdt_cny = 7.2  # 估值
            return btc_usdt, usdt_cny, btc_usdt * usdt_cny

        elif source == "币安":
            btc_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            btc_usdt = float(requests.get(btc_url).json()["price"])
            usdt_cny = 7.2
            return btc_usdt, usdt_cny, btc_usdt * usdt_cny

        elif source == "币世界":
            url = "https://api.bishijie.com/api/convert/coinprice?coin=btc"
            data = requests.get(url).json()
            btc_cny = float(data["data"]["cny"])
            btc_usdt = float(data["data"]["usd"])
            usdt_cny = btc_cny / btc_usdt
            return btc_usdt, usdt_cny, btc_cny

        elif source == "Bitget":
            btc_url = "https://api.bitget.com/api/spot/v1/market/ticker?symbol=BTCUSDT"
            btc_usdt = float(requests.get(btc_url).json()["data"]["last"])
            usdt_cny = 7.2
            return btc_usdt, usdt_cny, btc_usdt * usdt_cny

    except Exception as e:
        st.error(f"❌ 获取汇率失败：{e}")
        return None, None, None

# 获取汇率
btc_usdt, usdt_cny, btc_cny = get_rates(source)

# 显示结果
if btc_usdt and usdt_cny and btc_cny:
    st.success("✅ 汇率获取成功")
    st.metric("BTC/USDT", f"{btc_usdt:.2f} USDT")
    st.metric("USDT/CNY", f"{usdt_cny:.4f} CNY")
    st.metric("BTC/CNY", f"{btc_cny:.2f} 元人民币")
else:
    st.warning("⚠️ 无法获取完整汇率数据")

st.caption("由 OpenAI + Streamlit 提供 | 当前版本：第5版 | 数据来源：" + source)
