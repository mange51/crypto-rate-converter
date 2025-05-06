import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="币种换算器 第8.8版", layout="centered")
st.title("💱 币种换算器（第8.8版）")

# 检查网络连接
def check_network():
    try:
        requests.get("https://www.google.com", timeout=5)
        st.success("🌐 网络连接正常（已连接 Google）")
        return True
    except:
        st.error("❌ 无法连接外网")
        return False

# 获取 BTC/USDT
@st.cache_data(ttl=60)
def get_btc_usdt(source):
    try:
        if source == "Binance":
            r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()
            return float(r['price']), datetime.now()
        elif source == "Huobi":
            r = requests.get("https://api.huobi.pro/market/detail/merged?symbol=btcusdt").json()
            return float(r['tick']['close']), datetime.now()
    except:
        return None, None

# 获取 USD/CNY 汇率
@st.cache_data(ttl=600)
def get_usd_to_cny():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD").json()
        return r['rates']['CNY'], datetime.now()
    except:
        return None, None

# 格式化千位数 + 去除多余小数
def format_number(value, max_decimals=8):
    if value == int(value):
        return f"{int(value):,}"
    else:
        return f"{value:,.{max_decimals}f}".rstrip("0").rstrip(".")

# 汇率源选择
source = st.selectbox("选择汇率平台", ["Binance", "Huobi"])

if check_network():
    btc_usdt, btc_time = get_btc_usdt(source)
    usd_to_cny, usd_time = get_usd_to_cny()

    if btc_usdt:
        st.success(f"{source} BTC/USDT 汇率: {btc_usdt}（更新时间：{btc_time.strftime('%Y-%m-%d %H:%M:%S')}）")
    else:
        st.error("❌ 获取 BTC/USDT 汇率失败")

    if usd_to_cny:
        st.success(f"USD/CNY 汇率: {usd_to_cny:.4f}（更新时间：{usd_time.strftime('%Y-%m-%d %H:%M:%S')}）")
    else:
        st.error("❌ 获取 USD/CNY 汇率失败")

    refresh_interval = st.number_input("设置自动刷新时间（秒）", min_value=10, max_value=3600, value=60, step=5)
    st.markdown("---")

    # ✅ 修改为允许小于1的 DeFAI 单价，并格式化
    defai_price = st.number_input("DeFAI 单价：SATS(聪)", min_value=0.0, value=100.0, step=0.1, format="%.4f")

    st.subheader("输入一个币种数值，其它币种将自动换算")

    # ✅ 修改币种标签
    input_option = st.radio("选择输入币种", ["CNY(人民币)", "USDT(美元)", "BTC(比特币)", "SATS(聪)", "DeFAI"], horizontal=True)
    raw_input = st.text_input(f"请输入 {input_option} 数值", value="", placeholder="请输入数值…")

    try:
        user_input = float(raw_input.replace(",", ""))
    except:
        user_input = 0.0

    cny = usdt = btc = sats = defai = 0.0

    if btc_usdt and usd_to_cny and user_input > 0:
        if input_option.startswith("CNY"):
            cny = user_input
            usdt = cny / usd_to_cny
            btc = usdt / btc_usdt
        elif input_option.startswith("USDT"):
            usdt = user_input
            btc = usdt / btc_usdt
            cny = usdt * usd_to_cny
        elif input_option.startswith("BTC"):
            btc = user_input
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
        elif input_option.startswith("SATS"):
            sats = user_input
            btc = sats / 100_000_000
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
        elif input_option == "DeFAI":
            defai = user_input
            sats = defai * defai_price
            btc = sats / 100_000_000
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny

        sats = btc * 100_000_000
        defai = sats / defai_price if defai_price > 0 else 0

        st.markdown("### 💹 换算结果")
        cols = st.columns(5)
        cols[0].text_input("CNY(人民币)", value=format_number(cny, 6), disabled=True)
        cols[1].text_input("USDT(美元)", value=format_number(usdt, 6), disabled=True)
        cols[2].text_input("BTC(比特币)", value=format_number(btc, 8), disabled=True)
        cols[3].text_input("SATS(聪)", value=format_number(sats, 2), disabled=True)
        cols[4].text_input("DeFAI", value=format_number(defai, 4), disabled=True)

    time.sleep(refresh_interval)
    st.rerun()
