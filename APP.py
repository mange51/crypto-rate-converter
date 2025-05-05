import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="加密货币转换器 第8.6版", layout="centered")
st.title("💱 加密货币转换器 第8.6版")

# 网络检测
def check_network():
    try:
        requests.get("https://www.google.com", timeout=5)
        st.success("🌐 网络连接正常")
        return True
    except:
        st.error("❌ 无法连接外网")
        return False

# 汇率获取
@st.cache_data(ttl=60)
def get_btc_usdt(source):
    try:
        if source == "Binance":
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            return float(requests.get(url).json()['price'])
        elif source == "Huobi":
            url = "https://api.huobi.pro/market/detail/merged?symbol=btcusdt"
            return float(requests.get(url).json()['tick']['close'])
    except:
        return None

@st.cache_data(ttl=600)
def get_usd_to_cny():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        return requests.get(url).json()['rates']['CNY']
    except:
        return None

source = st.selectbox("选择汇率平台", ["Binance", "Huobi"])

if check_network():
    btc_usdt = get_btc_usdt(source)
    usd_to_cny = get_usd_to_cny()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if btc_usdt: st.success(f"{source} BTC/USDT: {btc_usdt}")
    else: st.error("❌ 获取 BTC/USDT 失败")

    if usd_to_cny: st.success(f"USD/CNY: {usd_to_cny:.4f}（{now}）")
    else: st.error("❌ 获取 USD/CNY 失败")

    refresh_interval = st.number_input("自动刷新时间（秒）", 5, 3600, 60, 5)
    st.markdown("---")

    # 自定义币
    cname1 = st.text_input("自定义币种1 名称", value="自定义币1")
    price1 = st.number_input(f"{cname1} 单价（聪）", value=100.0, min_value=0.0)
    cname2 = st.text_input("自定义币种2 名称", value="自定义币2")
    price2 = st.number_input(f"{cname2} 单价（聪）", value=200.0, min_value=0.0)

    st.markdown("---")
    st.subheader("输入一个币种，其余自动换算")

    input_col = st.columns(6)
    fields = ["cny", "usdt", "btc", "sats", "c1", "c2"]
    labels = ["CNY", "USDT", "BTC", "SATS", cname1, cname2]

    inputs = {}
    for i, field in enumerate(fields):
        with input_col[i]:
            inputs[field] = st.text_input(labels[i], value="", key=f"input_{field}")

    # 识别第一个有效输入
    active_key, active_value = None, None
    for k in fields:
        v = inputs[k]
        if v.strip() != "":
            try:
                active_value = float(v)
                active_key = k
                break
            except:
                continue

    results = dict.fromkeys(fields, 0.0)
    if active_key and btc_usdt and usd_to_cny:
        if active_key == "cny":
            results["cny"] = active_value
            results["usdt"] = active_value / usd_to_cny
            results["btc"] = results["usdt"] / btc_usdt
        elif active_key == "usdt":
            results["usdt"] = active_value
            results["btc"] = active_value / btc_usdt
            results["cny"] = active_value * usd_to_cny
        elif active_key == "btc":
            results["btc"] = active_value
            results["usdt"] = active_value * btc_usdt
            results["cny"] = results["usdt"] * usd_to_cny
        elif active_key == "sats":
            results["btc"] = active_value / 100_000_000
            results["usdt"] = results["btc"] * btc_usdt
            results["cny"] = results["usdt"] * usd_to_cny
        elif active_key == "c1":
            sats = active_value * price1
            results["btc"] = sats / 100_000_000
            results["usdt"] = results["btc"] * btc_usdt
            results["cny"] = results["usdt"] * usd_to_cny
        elif active_key == "c2":
            sats = active_value * price2
            results["btc"] = sats / 100_000_000
            results["usdt"] = results["btc"] * btc_usdt
            results["cny"] = results["usdt"] * usd_to_cny

        results["sats"] = results["btc"] * 100_000_000
        results["c1"] = results["sats"] / price1 if price1 else 0
        results["c2"] = results["sats"] / price2 if price2 else 0

        output_col = st.columns(6)
        for i, field in enumerate(fields):
            with output_col[i]:
                if field != active_key:
                    st.text_input(labels[i], value=str(round(results[field], 6)), key=f"output_{field}", disabled=True)

    st.caption(f"最后更新：{now}（每 {refresh_interval} 秒刷新一次）")

    time.sleep(refresh_interval)
    st.rerun()
