import streamlit as st
import requests
from decimal import Decimal, getcontext

getcontext().prec = 20

st.set_page_config(page_title="加密货币费率转换器", page_icon="💱")

st.title("加密货币费率转换器")

# 输入代理地址
proxy = st.text_input("代理地址 (可选)", "")

# 获取汇率按钮
if st.button("获取汇率"):
    try:
        proxies = {"http": proxy, "https": proxy} if proxy else None
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,tether&vs_currencies=cny"
        r = requests.get(url, proxies=proxies, timeout=10)
        data = r.json()
        btc_to_cny = Decimal(str(data["bitcoin"]["cny"]))
        usdt_to_cny = Decimal(str(data["tether"]["cny"]))
        btc_to_usdt = btc_to_cny / usdt_to_cny
        st.success(f"1BTC ≈ {btc_to_usdt:.2f} USDT | 1USDT ≈ {usdt_to_cny:.2f} CNY")
    except Exception as e:
        st.error(f"获取汇率失败：{e}")
