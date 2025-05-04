import streamlit as st
import requests
import time
from datetime import datetime
import math

st.set_page_config(page_title="加密货币转换器 第8.2版", layout="centered")
st.title("💱 加密货币转换器 第8.2版")

# 显示网络连接状态
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

    # 自动刷新时间（秒）
    refresh_interval = st.number_input("设置自动刷新时间（秒）", min_value=5, max_value=3600, value=60, step=5)
    st.markdown("---")

    # 自定义币种名称与单价（SATS）
    custom_name1 = st.text_input("自定义币种 1 名称", value="自定义币1")
    custom_price1 = st.number_input(f"{custom_name1} 单价（聪）", min_value=0.0, value=100.0)

    custom_name2 = st.text_input("自定义币种 2 名称", value="自定义币2")
    custom_price2 = st.number_input(f"{custom_name2} 单价（聪）", min_value=0.0, value=200.0)

    st.markdown("---")
    st.subheader("输入任意一个币种，自动换算其余")

    cny = st.number_input("CNY（人民币）", min_value=0.0, value=0.0, key="cny")
    usdt = st.number_input("USD/T（美元/泰达）", min_value=0.0, value=0.0, key="usdt")
    btc = st.number_input("BTC（比特币）", min_value=0.0, value=0.0, key="btc")
    sats = st.number_input("SATS（聪）", min_value=0.0, value=0.0, key="sats")
    c1 = st.number_input(f"{custom_name1}", min_value=0.0, value=0.0, key="c1")
    c2 = st.number_input(f"{custom_name2}", min_value=0.0, value=0.0, key="c2")

    # 自动换算逻辑
    if btc_usdt and isinstance(usd_to_cny, float):
        total_inputs = [cny, usdt, btc, sats, c1, c2]
        valid_inputs = [x for x in total_inputs if isinstance(x, (int, float)) and not math.isnan(x)]

        if any(x > 0 for x in valid_inputs):
            if cny > 0:
                usdt = cny / usd_to_cny
                btc = usdt / btc_usdt
            elif usdt > 0:
                cny = usdt * usd_to_cny
                btc = usdt / btc_usdt
            elif btc > 0:
                usdt = btc * btc_usdt
                cny = usdt * usd_to_cny
            elif sats > 0:
                btc = sats / 100_000_000
                usdt = btc * btc_usdt
                cny = usdt * usd_to_cny
            elif c1 > 0:
                sats = c1 * custom_price1
                btc = sats / 100_000_000
                usdt = btc * btc_usdt
                cny = usdt * usd_to_cny
            elif c2 > 0:
                sats = c2 * custom_price2
                btc = sats / 100_000_000
                usdt = btc * btc_usdt
                cny = usdt * usd_to_cny

            sats = btc * 100_000_000
            c1 = sats / custom_price1 if custom_price1 > 0 else 0
            c2 = sats / custom_price2 if custom_price2 > 0 else 0

            # 更新输入框显示结果
            st.session_state["cny"] = round(cny, 6)
            st.session_state["usdt"] = round(usdt, 6)
            st.session_state["btc"] = round(btc, 8)
            st.session_state["sats"] = round(sats, 2)
            st.session_state["c1"] = round(c1, 4)
            st.session_state["c2"] = round(c2, 4)

    # 自动刷新
    time.sleep(refresh_interval)
    st.rerun()
