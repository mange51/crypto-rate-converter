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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0.0.0 Safari/537.36"
        }
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,tether&vs_currencies=cny"
        r = requests.get(url, proxies=proxies, headers=headers, timeout=10)

        # 安全解析 JSON
        if r.status_code != 200:
            raise Exception(f"接口返回错误状态码：{r.status_code}")
        try:
            data = r.json()
        except ValueError:
            raise Exception("返回内容不是 JSON 格式")

        btc_to_cny = Decimal(str(data["bitcoin"]["cny"]))
        usdt_to_cny = Decimal(str(data["tether"]["cny"]))
        btc_to_usdt = btc_to_cny / usdt_to_cny
        st.success(f"1BTC ≈ {btc_to_usdt:.2f} USDT | 1USDT ≈ {usdt_to_cny:.2f} CNY")
    except Exception as e:
        st.error(f"获取汇率失败：{e}")
