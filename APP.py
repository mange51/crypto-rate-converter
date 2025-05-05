import streamlit as st
import requests
import time
from datetime import datetime
import math

st.set_page_config(page_title="加密货币转换器 第8.4版", layout="centered")
st.title("💱 加密货币转换器 第8.4版")

# 检查网络连接
def check_network():
    try:
        requests.get("https://www.google.com", timeout=5)
        st.success("🌐 网络连接正常（可以访问 Google）")
        return True
    except:
        st.error("❌ 无法连接外网，请检查代理或网络设置。")
        return False

# 获取 BTC/USDT 汇率
@st.cache_data(ttl=60)
def get_btc_usdt(source):
    try:
        if source == "Binance":
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            r = requests.get(url).json()
            return float(r['price'])
        elif source == "Huobi":
            url = "https://api.huobi.pro/market/detail/merged?symbol=btcusdt"
            r = requests.get(url).json()
            return float(r['tick']['close'])
    except:
        return None

# 获取 USD 对 CNY 汇率
@st.cache_data(ttl=600)
def get_usd_to_cny():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        r = requests.get(url).json()
        return r['rates']['CNY']
    except:
        return None

# 汇率来源选择
source = st.selectbox("选择汇率平台", ["Binance", "Huobi"])

if check_network():
    btc_usdt = get_btc_usdt(source)
    usd_to_cny = get_usd_to_cny()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if btc_usdt:
        st.success(f"{source} BTC/USDT 汇率: {btc_usdt}")
    else:
        st.error("❌ 获取 BTC/USDT 汇率失败")

    if usd_to_cny:
        st.success(f"USD/CNY 汇率: {usd_to_cny:.4f}（{timestamp}）")
    else:
        st.error("❌ 获取 USD/CNY 汇率失败")

    refresh_interval = st.number_input("设置自动刷新时间（秒）", min_value=5, max_value=3600, value=60, step=5)
    st.markdown("---")

    # 自定义币种
    custom_name1 = st.text_input("自定义币种 1 名称", value="自定义币1")
    custom_price1 = st.number_input(f"{custom_name1} 单价（聪）", min_value=0.0, value=100.0)
    custom_name2 = st.text_input("自定义币种 2 名称", value="自定义币2")
    custom_price2 = st.number_input(f"{custom_name2} 单价（聪）", min_value=0.0, value=200.0)

    st.markdown("---")
    st.subheader("输入任意一个币种，自动换算其余")

    # 初始化输入框
    input_col = st.columns(6)
    with input_col[0]:
        cny_input = st.number_input("CNY（人民币）", min_value=0.0, value=0.0, key="input_cny")
    with input_col[1]:
        usdt_input = st.number_input("USD/T（美元/泰达）", min_value=0.0, value=0.0, key="input_usdt")
    with input_col[2]:
        btc_input = st.number_input("BTC（比特币）", min_value=0.0, value=0.0, key="input_btc")
    with input_col[3]:
        sats_input = st.number_input("SATS（聪）", min_value=0.0, value=0.0, key="input_sats")
    with input_col[4]:
        c1_input = st.number_input(f"{custom_name1}", min_value=0.0, value=0.0, key="input_c1")
    with input_col[5]:
        c2_input = st.number_input(f"{custom_name2}", min_value=0.0, value=0.0, key="input_c2")

    # 换算逻辑
    cny = usdt = btc = sats = c1 = c2 = 0.0

    if btc_usdt and usd_to_cny:
        if cny_input > 0:
            cny = cny_input
            usdt = cny / usd_to_cny
            btc = usdt / btc_usdt
        elif usdt_input > 0:
            usdt = usdt_input
            btc = usdt / btc_usdt
            cny = usdt * usd_to_cny
        elif btc_input > 0:
            btc = btc_input
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
        elif sats_input > 0:
            sats = sats_input
            btc = sats / 100_000_000
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
        elif c1_input > 0 and custom_price1 > 0:
            c1 = c1_input
            sats = c1 * custom_price1
            btc = sats / 100_000_000
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
        elif c2_input > 0 and custom_price2 > 0:
            c2 = c2_input
            sats = c2 * custom_price2
            btc = sats / 100_000_000
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny

        sats = btc * 100_000_000
        c1 = sats / custom_price1 if custom_price1 > 0 else 0
        c2 = sats / custom_price2 if custom_price2 > 0 else 0

        # 输出计算后的结果
        result_col = st.columns(6)
        result_col[0].metric("CNY", round(cny, 6))
        result_col[1].metric("USDT", round(usdt, 6))
        result_col[2].metric("BTC", round(btc, 8))
        result_col[3].metric("SATS", round(sats, 2))
        result_col[4].metric(custom_name1, round(c1, 4))
        result_col[5].metric(custom_name2, round(c2, 4))

    # 自动刷新
    time.sleep(refresh_interval)
    st.rerun()
