import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="币种换算器 v8.9", layout="centered")

st.title("💱 币种换算器（v8.9）")

# 显示网络连接状态
def check_network():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

if check_network():
    st.success("🌐 网络连接正常")
else:
    st.error("❌ 无法连接外网")

# 获取 BTC/USDT 汇率
def get_btc_usdt_price():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
        data = r.json()
        return float(data["price"]), datetime.now()
    except:
        return None, None

# 获取 USD/CNY 汇率
def get_usd_cny_rate():
    try:
        r = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=CNY", timeout=5)
        data = r.json()
        return float(data["rates"]["CNY"]), datetime.fromisoformat(data["date"] + "T00:00:00")
    except Exception as e:
        print("USD/CNY 获取失败：", e)
        return None, None

# 自动刷新
st_autorefresh = st.experimental_rerun
st_autorefresh_interval = 60  # 每 60 秒刷新
st_autorefresh_interval

# 汇率获取
btc_usdt, btc_time = get_btc_usdt_price()
usd_cny, usd_cny_time = get_usd_cny_rate()

if btc_usdt and usd_cny:
    cny_usdt = usd_cny
    btc_cny = btc_usdt * usd_cny
    sats_per_btc = 100_000_000
    st.success(f"✅ 汇率获取成功")
    st.markdown(f"📈 BTC/USDT 汇率：**{btc_usdt:,.2f}** （更新时间：{btc_time.strftime('%H:%M:%S')}）")
    st.markdown(f"💵 USD/CNY 汇率：**{usd_cny:,.4f}** （更新时间：{usd_cny_time.strftime('%Y-%m-%d')}）")
else:
    st.error("❌ 获取汇率失败，请稍后再试。")
    st.stop()

st.divider()

# 显示币种输入界面
st.subheader("🔢 输入任意币种数值，自动换算其它币种")

col1, col2 = st.columns([1, 1])
with col1:
    input_currency = st.selectbox("选择输入币种", ["CNY(人民币)", "USDT(美元)", "BTC(比特币)", "SATS(聪)", "DeFAI"])
    defai_price_sats = st.number_input("DeFAI 单价：SATS(聪)", min_value=0.0, value=100.0, step=1.0, format="%.2f")
with col2:
    input_amount = st.number_input(f"输入 {input_currency} 数量", min_value=0.0, step=1.0, format="%.8f")

# 统一单位换算逻辑
defai_sats = defai_price_sats
sats = 0

if input_currency == "CNY(人民币)":
    usdt = input_amount / usd_cny
    btc = usdt / btc_usdt
    sats = btc * sats_per_btc
elif input_currency == "USDT(美元)":
    usdt = input_amount
    btc = usdt / btc_usdt
    sats = btc * sats_per_btc
elif input_currency == "BTC(比特币)":
    btc = input_amount
    sats = btc * sats_per_btc
elif input_currency == "SATS(聪)":
    sats = input_amount
elif input_currency == "DeFAI":
    sats = input_amount * defai_sats

btc = sats / sats_per_btc
usdt = btc * btc_usdt
cny = usdt * usd_cny
defai = sats / defai_sats if defai_sats else 0

# 输出换算结果
st.markdown("### 💡 自动换算结果")
st.write(f"CNY(人民币)：**{cny:,.6f}**")
st.write(f"USDT(美元)：**{usdt:,.6f}**")
st.write(f"BTC(比特币)：**{btc:,.8f}**")
st.write(f"SATS(聪)：**{int(sats):,}**")
st.write(f"DeFAI：**{defai:,.4f}**")

st.caption("数据每分钟自动刷新")
