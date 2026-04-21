import requests
import json
from urllib.parse import urlparse, parse_qs, unquote
import urllib
import time
import pandas as pd

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "chat_bot_session_id=c5bf7063f0b53d74cd5dde3544c7659d; other_uid=Ths_iwencai_Xuangu_37arjesx9cdwuibtqpmqxcw0162ycyda; ta_random_userid=wht30lfjkg; cid=0ce420d77d4bb14c191c5a0cbbbf91c21734747987; THSSESSID=d179bab8591710a9d19f85798c; v=A1BH2xTDA-7O6d-xUScqB5YRIZWnGTVBVviIZ0shHN9-oP6L8ikE86YNWAuZ",
    "Host": "www.iwencai.com",
    "Origin": "https://www.iwencai.com",
    "Referer": "https://www.iwencai.com/unifiedmobile/?q=%E8%BF%9E%E6%9D%BF%E5%A4%A9%E6%95%B0%E6%8E%92%E5%BA%8F%EF%BC%9B%E5%B8%82%E5%80%BC&queryType=stock",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

data = {
    "question": "连续3天涨停以上且涨幅小于18%且剔除st股票流通市值小于40亿流通市值大于5000万",
    "source": "ths_mobile_iwencai",
    "user_id": "0",
    "user_name": "0",
    "version": "2.0",
    "secondary_intent": "stock",
    "add_info": '{"urp":{"scene":3,"company":1,"business":1,"is_lowcode":1},"contentType":"json"}',
    "log_info": '{"input_type":"typewrite"}',
    "rsh": "Ths_iwencai_Xuangu_37arjesx9cdwuibtqpmqxcw0162ycyda",
}


def read_config(file_name="config.json"):
    with open(file_name, "r", encoding="utf-8") as f:
        config = json.load(f)
    headers = config.get("headers", {})
    data = config.get("data", {})
    Cookie = headers.get("Cookie", "")
    UserAgent = headers.get("User-Agent", "")
    question = data.get("question", "")
    return Cookie, UserAgent, question


def get_url(headers, data):
    url = "https://www.iwencai.com/unifiedwap/unified-wap/v2/result/get-robot-data"
    session = requests.Session()
    response = session.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("获取数据成功")
        print(response.json())
    else:
        print("获取失败，状态码：", response.status_code)
    base_url = "https://www.iwencai.com"
    result_data = response.json()["data"]["answer"][0]["txt"][0]["content"][
        "components"
    ][0]["config"]["other_info"]["footer_info"]["url"]
    url = base_url + result_data
    return url


def get_url_params(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    decoded_params = {}
    for key, value in params.items():
        decoded_value = unquote(value[0])
        decoded_params[key] = decoded_value
    return decoded_params


def get_df(headers, data):
    url = "https://www.iwencai.com/gateway/urp/v7/landing/getDataList"
    page_num = int(data["perpage"])
    all_data = []
    for i in range(1, page_num + 1):
        time.sleep(2)
        print("开始获取第", i, "页，共", page_num, "页")
        data["page"] = str(i)
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print(response.json())
        data_list = response.json()["answer"]["components"][0]["data"]["datas"]
        all_data.extend(data_list)
    df = pd.DataFrame(all_data)
    return df


def df_to_txt(df):
    df_to_write = df[["股票代码", "股票名称"]]
    with open("./wencai_stock_poll.txt", "w", encoding="utf-8") as f:
        for index, row in df_to_write.iterrows():
            f.write(row["股票代码"] + "\t" + row["股票名称"] + "\n")


if __name__ == "__main__":
    Cookie, UserAgent, question = read_config()
    headers["Cookie"] = Cookie
    headers["User-Agent"] = UserAgent
    data["question"] = question

    url = get_url(headers, data)
    print("问财选股url获取成功:", url)

    params_data = get_url_params(url)
    df = get_df(headers, params_data)
    print("问财选股数据获取成功:", df)
    df_to_txt(df)
    print("问财选股数据已保存")
