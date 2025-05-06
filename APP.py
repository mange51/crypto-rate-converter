# 第8.9.2版：调整布局，优先展示换算工具，辅助信息置底

import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="币种换算器", layout="centered")
st.title("💱 币种换算")

# 汇率数据获取函数
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

@st.cache_data(ttl=600)
def get_usd_to_cny():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD").json()
        return r['rates']['CNY'], datetime.now()
    except:
        return None, None

# 千位格式化函数
def format_number(value, max_decimals=8):
    if value == int(value):
        return f"{int(value):,}"
    else:
        return f"{value:,.{max_decimals}f}".rstrip("0").rstrip(".")

# 页面顶部：一币输入多币立算
st.subheader("💡 一币输入，多币立算")
input_option = st.radio("选择输入币种", ["CNY(人民币)", "USDT(美元)", "BTC(比特币)", "SATS(聪)", "DeFAI"], horizontal=True)
raw_input = st.text_input(f"请输入 {input_option} 数值", value="", placeholder="请输入数值…")
try:
    user_input = float(raw_input.replace(",", ""))
except:
    user_input = 0.0

# 默认平台和汇率获取
source = st.session_state.get("source_selector", "Binance")
btc_usdt, btc_time = get_btc_usdt(source)
usd_to_cny, usd_time = get_usd_to_cny()

# DeFAI 单价设置
defai_input = st.text_input("DeFAI 单价：SATS(聪)", value="", placeholder="例如：100")
try:
    defai_price = float(defai_input.replace(",", ""))
    if defai_price < 0:
        defai_price = 0.0
except:
    defai_price = 100.0

# 换算逻辑
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

    # 换算结果
    st.markdown("### 💹 换算结果")
    cols = st.columns(5)
    cols[0].text_input("CNY(人民币)", value=format_number(cny, 6), disabled=True)
    cols[1].text_input("USDT(美元)", value=format_number(usdt, 6), disabled=True)
    cols[2].text_input("BTC(比特币)", value=format_number(btc, 8), disabled=True)
    cols[3].text_input("SATS(聪)", value=format_number(sats, 2), disabled=True)
    cols[4].text_input("DeFAI", value=format_number(defai, 4), disabled=True)

# 底部辅助信息
st.markdown("---")
# 网络测试
try:
    requests.get("https://www.google.com", timeout=5)
    st.success("🌐 网络连接正常（已连接 Google）")
except:
    st.error("❌ 无法连接外网")

# 汇率信息显示
if btc_usdt:
    st.success(f"{source} BTC/USDT 汇率: {btc_usdt}（更新时间：{btc_time.strftime('%Y-%m-%d %H:%M:%S')}）")
else:
    st.error("❌ 获取 BTC/USDT 汇率失败")
if usd_to_cny:
    st.success(f"USD/CNY 汇率: {usd_to_cny:.4f}（更新时间：{usd_time.strftime('%Y-%m-%d %H:%M:%S')}）")
else:
    st.error("❌ 获取 USD/CNY 汇率失败")

# 汇率源选择器与刷新设置
source = st.selectbox("选择汇率平台", ["Binance", "Huobi"], index=0, key="source_selector")
refresh_interval = st.number_input("设置自动刷新时间（秒）", min_value=10, max_value=3600, value=60, step=5)
time.sleep(refresh_interval)
st.rerun()
