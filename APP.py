import requests

def get_rate_with_headers():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=cny"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://www.coingecko.com/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            cny_rate = data["bitcoin"]["cny"]
            print(f"当前比特币兑人民币汇率：¥{cny_rate}")
        else:
            print(f"获取汇率失败，状态码：{response.status_code}\n内容：{response.text}")
    except requests.RequestException as e:
        print(f"请求异常：{e}")

if __name__ == "__main__":
    get_rate_with_headers()
