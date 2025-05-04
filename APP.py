import streamlit as st
import requests
import socket
import time
from threading import Timer

# ---------------- 网络连通性检测 ----------------
def check_network():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except OSError:
        return False

# ---------------- 汇率获取函数 ----------------
def get_binance_rate():
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=10)
        data = response.json()
        return float(data["price"])
    except Exception as e:
        return f"币安获取失败：{e}"

def get_huobi_rate():
    try:
        response = requests.get("https://api.huobi.pro/market/detail/merged?symbol=btcusdt", timeout=10)
        data = response.json()
        return float(data["tick"]["close"])
    except Exception as e:
        return f"火币获取失败：{e}"

def get_usd_to_cny():
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        data = response.json()
        if "rates" in data and "CNY" in data["rates"]:
            return float(data["rates"]["CNY"])
        else:
            return "USD/CNY 获取失败：接口响应不包含 'CNY' 汇率"
    except Exception as e:
        return f"USD/CNY 获取失败：{e}"

# ---------------- 汇率刷新 ----------------
def get_rates():
    binance = get_binance_rate()
    huobi = get_huobi_rate()
    usd_to_cny = get_usd_to_cny()
    btc_usdt = binance if isinstance(binance, float) else (huobi if isinstance(huobi, float) else None)
    return binance, huobi, usd_to_cny, btc_usdt

# ---------------- Streamlit 页面 ----------------
st.set_page_config(page_title="BTC 汇率转换工具（第9.0版）", layout="centered")
st.title("📈 BTC 汇率转换工具（第9.0版）")

# 检测网络
st.subheader("🌐 网络连接测试")
if check_network():
    st.success("网络连接正常（可以访问 Google）")
else:
    st.error("无法访问 Google，当前网络可能无法连接外网")

# 自动刷新设置
refresh_interval = st.sidebar.number_input("自动刷新间隔（秒）", min_value=10, max_value=300, value=60, step=10, help="每隔指定秒数自动刷新汇率")
st.sidebar.write("（手动刷新请点击页面右上角的刷新按钮）")

# 汇率信息
st.subheader("💱 汇率信息")
binance, huobi, usd_to_cny, btc_usdt = get_rates()

col1, col2 = st.columns(2)
with col1:
    st.write("### Binance BTC/USDT")
    st.success(binance if isinstance(binance, float) else str(binance))

with col2:
    st.write("### Huobi BTC/USDT")
    st.success(huobi if isinstance(huobi, float) else str(huobi))

st.write("### USD → CNY 汇率")
if isinstance(usd_to_cny, float):
    st.success(f"1 USD ≈ {usd_to_cny:.4f} CNY")
else:
    st.error(usd_to_cny)

# 汇率换算
st.subheader("🔄 汇率换算工具")

custom1_name = st.text_input("自定义币1名称", "自定义币1")
custom2_name = st.text_input("自定义币2名称", "自定义币2")

custom1_price = st.number_input(f"{custom1_name} 单价（SATS）", min_value=0.0, value=1000.0, step=10.0)
custom2_price = st.number_input(f"{custom2_name} 单价（SATS）", min_value=0.0, value=5000.0, step=10.0)

st.markdown("---")

col_cny, col_usdt, col_btc, col_sats, col_custom1, col_custom2 = st.columns(6)

with col_cny:
    cny = st.number_input("CNY（人民币）", value=0.0, key="cny")
with col_usdt:
    usdt = st.number_input("USD/T", value=0.0, key="usdt")
with col_btc:
    btc = st.number_input("BTC", value=0.0, key="btc")
with col_sats:
    sats = st.number_input("SATS（聪）", value=0.0, key="sats")
with col_custom1:
    c1 = st.number_input(f"{custom1_name}", value=0.0, key="c1")
with col_custom2:
    c2 = st.number_input(f"{custom2_name}", value=0.0, key="c2")

# 自动换算逻辑
if btc_usdt and isinstance(usd_to_cny, float):
    # 优先判断哪个输入不为0
    total_inputs = [cny, usdt, btc, sats, c1, c2]
    if any(x > 0 for x in total_inputs):
        if btc > 0:
            sats = btc * 1e8
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
            c1 = sats / custom1_price if custom1_price else 0
            c2 = sats / custom2_price if custom2_price else 0
        elif sats > 0:
            btc = sats / 1e8
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
            c1 = sats / custom1_price if custom1_price else 0
            c2 = sats / custom2_price if custom2_price else 0
        elif cny > 0:
            usdt = cny / usd_to_cny
            btc = usdt / btc_usdt
            sats = btc * 1e8
            c1 = sats / custom1_price if custom1_price else 0
            c2 = sats / custom2_price if custom2_price else 0
        elif usdt > 0:
            btc = usdt / btc_usdt
            sats = btc * 1e8
            cny = usdt * usd_to_cny
            c1 = sats / custom1_price if custom1_price else 0
            c2 = sats / custom2_price if custom2_price else 0
        elif c1 > 0:
            sats = c1 * custom1_price
            btc = sats / 1e8
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
            c2 = sats / custom2_price if custom2_price else 0
        elif c2 > 0:
            sats = c2 * custom2_price
            btc = sats / 1e8
            usdt = btc * btc_usdt
            cny = usdt * usd_to_cny
            c1 = sats / custom1_price if custom1_price else 0

        # 显示结果
        st.markdown("---")
        st.write(f"🔄 汇率换算结果：")
        st.write(f"- CNY：{cny:.2f}")
        st.write(f"- USDT：{usdt:.2f}")
        st.write(f"- BTC：{btc:.8f}")
        st.write(f"- SATS：{sats:,.0f}")
        st.write(f"- {custom1_name}：{c1:.4f}")
        st.write(f"- {custom2_name}：{c2:.4f}")
    else:
        st.info("请在任意一个币种中输入数值以进行换算。")
else:
    st.warning("由于 BTC 或 USD/CNY 汇率缺失，无法进行换算。")
