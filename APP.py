import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="加密货币转换器 第8.6版", layout="centered")
st.title("💱 加密货币转换器 第8.6版")

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

    # 输入栏并记录来源
    input_col = st.columns(6)
    input_sources = {}
    cny_input = input_col[0].text_input("CNY（人民币）", value="", key="cny_input")
    usdt_input = input_col[1].text_input("USD/T（美元/泰达）", value="", key="usdt_input")
    btc_input = input_col[2].text_input("BTC（比特币）", value="", key="btc_input")
    sats_input = input_col[3].text_input("SATS（聪）", value="", key="sats_input")
    c1_input = input_col[4].text_input(custom_name1, value="", key="c1_input")
    c2_input = input_col[5].text_input(custom_name2, value="", key="c2_input")

    results = {"cny": "", "usdt": "", "btc": "", "sats": "", "c1": "", "c2": ""}

    try:
        if cny_input:
            cny = float(cny_input)
            usdt = cny / usd_to_cny
            btc = usdt / btc_usdt
            sats = btc * 100_000_000
            c1 = sats / custom_price1 if custom_price1 > 0 else 0
            c2 = sats / custom_price2 if custom_price2 > 0 else 0
            results.update({"cny": cny_input, "usdt": f"{usdt:.6f}", "btc": f"{btc:.8f}", "sats": f"{sats:.2f}", "c1": f"{c1:.4f}", "c2": f"{c2:.4f}"})

        elif usdt_input:
            usdt = float(usdt_input)
            btc = usdt / btc_usdt
            cny = usdt * usd_to_cny
            sats = btc * 100_000_000
            c1 = sats / custom_price1 if custom_price1 > 0 else 0
            c2 = sats / custom_price2 if custom_price2 > 0 else 0
            results.update({"cny": f"{cny:.6f}", "usdt": usdt_input, "btc": f"{btc:.8f}", "sats": f"{sats:.2f}", "c1": f"{c1:.4f}", "c2": f"{c2:.4f}"})

        elif btc_input:
            btc = float(btc_input)
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
            sats = btc * 100_000_000
            c1 = sats / custom_price1 if custom_price1 > 0 else 0
            c2 = sats / custom_price2 if custom_price2 > 0 else 0
            results.update({"cny": f"{cny:.6f}", "usdt": f"{usdt:.6f}", "btc": btc_input, "sats": f"{sats:.2f}", "c1": f"{c1:.4f}", "c2": f"{c2:.4f}"})

        elif sats_input:
            sats = float(sats_input)
            btc = sats / 100_000_000
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
            c1 = sats / custom_price1 if custom_price1 > 0 else 0
            c2 = sats / custom_price2 if custom_price2 > 0 else 0
            results.update({"cny": f"{cny:.6f}", "usdt": f"{usdt:.6f}", "btc": f"{btc:.8f}", "sats": sats_input, "c1": f"{c1:.4f}", "c2": f"{c2:.4f}"})

        elif c1_input:
            c1 = float(c1_input)
            sats = c1 * custom_price1
            btc = sats / 100_000_000
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
            c2 = sats / custom_price2 if custom_price2 > 0 else 0
            results.update({"cny": f"{cny:.6f}", "usdt": f"{usdt:.6f}", "btc": f"{btc:.8f}", "sats": f"{sats:.2f}", "c1": c1_input, "c2": f"{c2:.4f}"})

        elif c2_input:
            c2 = float(c2_input)
            sats = c2 * custom_price2
            btc = sats / 100_000_000
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
            c1 = sats / custom_price1 if custom_price1 > 0 else 0
            results.update({"cny": f"{cny:.6f}", "usdt": f"{usdt:.6f}", "btc": f"{btc:.8f}", "sats": f"{sats:.2f}", "c1": f"{c1:.4f}", "c2": c2_input})

    except:
        pass

    # 结果展示栏
    result_col = st.columns(6)
    result_col[0].text_input("CNY（人民币）", value=results["cny"], key="cny_result")
    result_col[1].text_input("USD/T（美元/泰达）", value=results["usdt"], key="usdt_result")
    result_col[2].text_input("BTC（比特币）", value=results["btc"], key="btc_result")
    result_col[3].text_input("SATS（聪）", value=results["sats"], key="sats_result")
    result_col[4].text_input(custom_name1, value=results["c1"], key="c1_result")
    result_col[5].text_input(custom_name2, value=results["c2"], key="c2_result")

    time.sleep(refresh_interval)
    st.rerun()
