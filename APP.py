import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="加密货币换算器 第8.5版", layout="centered")
st.title("💱 加密货币换算器 第8.5版")

# -------------------
# 网络连接测试
# -------------------
def check_network():
    try:
        requests.get("https://www.google.com", timeout=5)
        st.success("🌐 网络连接正常（可访问 Google）")
        return True
    except:
        st.error("❌ 无法连接外网，请检查网络设置或代理。")
        return False

# -------------------
# 获取 BTC/USDT
# -------------------
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

# -------------------
# 获取 USD/CNY
# -------------------
@st.cache_data(ttl=600)
def get_usd_to_cny():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD").json()
        return r['rates']['CNY']
    except:
        return None

# -------------------
# 界面设置
# -------------------
if check_network():
    source = st.selectbox("选择汇率平台", ["Binance", "Huobi"])
    btc_usdt = get_btc_usdt(source)
    usd_cny = get_usd_to_cny()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if btc_usdt:
        st.success(f"{source} BTC/USDT 汇率：{btc_usdt}")
    else:
        st.error("❌ 获取 BTC/USDT 失败")

    if usd_cny:
        st.success(f"USD/CNY 汇率：{usd_cny:.4f}（{timestamp}）")
    else:
        st.error("❌ 获取 USD/CNY 失败")

    refresh_interval = st.number_input("自动刷新时间（秒）", min_value=5, max_value=3600, value=60, step=5)
    st.markdown("---")

    # 固定 DeFAI 单价（单位：聪）
    defai_price_sats = st.number_input("DeFAI 单价（聪）", min_value=0.0, value=100.0, step=1.0)

    st.markdown("## 输入并转换")

    unit_options = ["CNY", "USDT", "BTC", "SATS", "DeFAI"]
    selected_unit = st.selectbox("选择要输入的币种", unit_options)
    input_amount = st.number_input(f"请输入 {selected_unit} 金额", min_value=0.0, value=0.0, step=1.0)

    # -------------------
    # 汇率换算逻辑
    # -------------------
    cny = usdt = btc = sats = defai = 0.0

    if btc_usdt and usd_cny:
        if selected_unit == "CNY":
            cny = input_amount
            usdt = cny / usd_cny
            btc = usdt / btc_usdt
        elif selected_unit == "USDT":
            usdt = input_amount
            btc = usdt / btc_usdt
            cny = usdt * usd_cny
        elif selected_unit == "BTC":
            btc = input_amount
            usdt = btc * btc_usdt
            cny = usdt * usd_cny
        elif selected_unit == "SATS":
            sats = input_amount
            btc = sats / 100_000_000
            usdt = btc * btc_usdt
            cny = usdt * usd_cny
        elif selected_unit == "DeFAI":
            defai = input_amount
            sats = defai * defai_price_sats
            btc = sats / 100_000_000
            usdt = btc * btc_usdt
            cny = usdt * usd_cny

        # 统一换算
        sats = btc * 100_000_000
        defai = sats / defai_price_sats if defai_price_sats > 0 else 0

        # -------------------
        # 显示换算结果
        # -------------------
        st.markdown("### 换算结果")
        col = st.columns(5)
        col[0].metric("CNY", f"{round(cny, 2)}")
        col[1].metric("USDT", f"{round(usdt, 6)}")
        col[2].metric("BTC", f"{round(btc, 8)}")
        col[3].metric("SATS", f"{int(sats)}")
        col[4].metric("DeFAI", f"{round(defai, 4)}")

        st.caption(f"汇率更新时间：{timestamp}")

    # 自动刷新
    time.sleep(refresh_interval)
    st.rerun()
