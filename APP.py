import streamlit as st
import requests
from decimal import Decimal, getcontext

getcontext().prec = 20

st.set_page_config(page_title="加密货币费率转换器", page_icon="💱")

st.title("加密货币费率转换器")

# 获取汇率按钮
if st.button("获取汇率"):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }

        # 获取 BTC/USDT 价格
        btc_url = "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT"
        btc_res = requests.get(btc_url, headers=headers, timeout=10)
        
        # 打印返回内容进行调试
        st.write(f"BTC Response: {btc_res.text}")
        
        btc_data = btc_res.json()
        btc_to_usdt = Decimal(btc_data["data"][0]["last"])

        # 获取 USDT/CNY 汇率
        usdt_url = "https://www.okx.com/api/v5/market/ticker?instId=USDT-CNY"
        usdt_res = requests.get(usdt_url, headers=headers, timeout=10)
        
        # 打印返回内容进行调试
        st.write(f"USDT Response: {usdt_res.text}")
        
        usdt_data = usdt_res.json()
        usdt_to_cny = Decimal(usdt_data["data"][0]["last"])

        st.success(f"1BTC ≈ {btc_to_usdt:.2f} USDT | 1USDT ≈ {usdt_to_cny:.2f} CNY")

    except Exception as e:
        st.error(f"获取汇率失败：{e}")
