import streamlit as st
import requests

# ========== 第6版 ==========
st.set_page_config(page_title="比特币/USDT 汇率查询", layout="centered")
st.title("💱 比特币 / USDT 汇率查询 - 第6版")

# ========== 网络连接检测 ==========
def check_network():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

# ========== 获取币安汇率 ==========
def get_binance_rates():
    try:
        r1 = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
        r1.raise_for_status()
        btc_usdt = float(r1.json()['price'])

        # 币安无CNY，手动设置
        usdt_cny = 7.2
        return btc_usdt, usdt_cny, "✅ Binance 成功（CNY为默认）"
    except Exception as e:
        return None, None, f"❌ Binance 失败：{e}"

# ========== 获取火币汇率 ==========
def get_huobi_rates():
    try:
        btc_url = "https://api.huobi.pro/market/detail/merged?symbol=btcusdt"
        cny_url = "https://api.huobi.pro/market/detail/merged?symbol=usdtht"  # 有时无效，备用手动
        r1 = requests.get(btc_url, timeout=5)
        btc_usdt = float(r1.json()["tick"]["close"])

        # 火币不一定提供 CNY 汇率，尝试获取，如果失败则设默认
        try:
            r2 = requests.get(cny_url, timeout=5)
            usdt_cny = float(r2.json()["tick"]["close"])
        except:
            usdt_cny = 7.2  # 默认值

        return btc_usdt, usdt_cny, "✅ 火币 成功（CNY可能为默认）"
    except Exception as e:
        return None, None, f"❌ 火币 失败：{e}"

# ========== 用户界面 ==========
platform = st.selectbox("选择数据平台：", ["Binance", "火币 (Huobi)"])
check = st.button("获取汇率")

# ========== 主逻辑 ==========
if check:
    if check_network():
        st.success("🌐 网络连接正常（已连接Google）")

        if platform == "Binance":
            btc_usdt, usdt_cny, status = get_binance_rates()
        else:
            btc_usdt, usdt_cny, status = get_huobi_rates()

        if btc_usdt and usdt_cny:
            st.write(status)
            st.write(f"🔶 当前 BTC/USDT 汇率：`{btc_usdt}`")
            st.write(f"💵 当前 USDT/CNY 汇率：`{usdt_cny}`")
            st.write(f"💰 当前 BTC/CNY 汇率：`{btc_usdt * usdt_cny:.2f}`")
        else:
            st.error("获取汇率失败，请稍后再试。")
            st.write(status)
    else:
        st.error("❌ 无法访问 Google，可能断网或被墙。")

st.caption("© 第6版 - 支持币安和火币，CNY默认值为 7.2")
