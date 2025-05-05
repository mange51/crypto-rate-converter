import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="币种换算器 第8.6版", layout="centered")
st.title("💱 币种换算器（第8.6版）")

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
            return float(r['price'])
        elif source == "Huobi":
            r = requests.get("https://api.huobi.pro/market/detail/merged?symbol=btcusdt").json()
            return float(r['tick']['close'])
    except:
        return None

# 获取 USD/CNY 汇率
@st.cache_data(ttl=600)
def get_usd_to_cny():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD").json()
        return r['rates']['CNY']
    except:
        return None

# 汇率源选择
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
        st.success(f"USD/CNY 汇率: {usd_to_cny:.4f}（更新时间：{timestamp}）")
    else:
        st.error("❌ 获取 USD/CNY 汇率失败")

    refresh_interval = st.number_input("设置自动刷新时间（秒）", min_value=10, max_value=3600, value=60, step=5)
    st.markdown("---")

    # DeFAI价格
    defai_price = st.number_input("DeFAI 单价（聪）", min_value=1.0, value=100.0, step=1.0)

    # 用户输入方式
    st.subheader("输入一个币种数值，其它币种将自动换算")

    input_option = st.radio("选择输入币种", ["CNY", "USDT", "BTC", "SATS", "DeFAI"], horizontal=True)

    # 改进输入体验：使用 text_input + 转换，避免默认值 + 回车问题
    raw_input = st.text_input(f"请输入 {input_option} 数值", value="", placeholder="请输入数值…")
    try:
        user_input = float(raw_input.replace(",", ""))
    except:
        user_input = 0.0

    # 初始化换算结果
    cny = usdt = btc = sats = defai = 0.0

    if btc_usdt and usd_to_cny and user_input > 0:
        if input_option == "CNY":
            cny = user_input
            usdt = cny / usd_to_cny
            btc = usdt / btc_usdt
        elif input_option == "USDT":
            usdt = user_input
            btc = usdt / btc_usdt
            cny = usdt * usd_to_cny
        elif input_option == "BTC":
            btc = user_input
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
        elif input_option == "SATS":
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

        # 显示换算结果（只读 + 千位符格式）
        st.markdown("### 💹 换算结果")
        cols = st.columns(5)
        cols[0].text_input("CNY（人民币）", value=f"{cny:,.6f}", disabled=True)
        cols[1].text_input("USDT（美元）", value=f"{usdt:,.6f}", disabled=True)
        cols[2].text_input("BTC（比特币）", value=f"{btc:,.8f}", disabled=True)
        cols[3].text_input("SATS（聪）", value=f"{sats:,.2f}", disabled=True)
        cols[4].text_input("DeFAI", value=f"{defai:,.4f}", disabled=True)

    # 自动刷新
    time.sleep(refresh_interval)
    st.rerun()
