import requests
import json
import time
import pandas as pd
from urllib.parse import urlparse, parse_qs


def read_config(file_name="config.json"):
    with open(file_name, "r", encoding="utf-8") as f:
        config = json.load(f)
    headers = config.get("headers", {})
    data = config.get("data", {})
    return headers, data


def get_params(headers, data):
    url = "https://www.iwencai.com/unifiedwap/unified-wap/v2/result/get-robot-data"
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        raise Exception(f"获取数据失败，状态码：{response.status_code}")

    result_url = response.json()["data"]["answer"][0]["txt"][0]["content"][
        "components"
    ][0]["config"]["other_info"]["footer_info"]["url"]
    parsed = urlparse(result_url)
    return parse_qs(parsed.query)


def get_df(headers, data):
    url = "https://www.iwencai.com/gateway/urp/v7/landing/getDataList"
    page_num = int(data["perpage"])
    all_data = []
    for i in range(1, page_num + 1):
        time.sleep(2)
        print(f"获取第{i}/{page_num}页")
        data["page"] = str(i)
        response = requests.post(url, headers=headers, data=data)
        data_list = response.json()["answer"]["components"][0]["data"]["datas"]
        all_data.extend(data_list)
    return pd.DataFrame(all_data)


def df_to_txt(df, output_file="./wencai_stock_poll.txt"):
    df[["股票代码", "股票名称"]].to_csv(
        output_file, sep="\t", index=False, header=False
    )


if __name__ == "__main__":
    headers, data = read_config()
    params_data = get_params(headers, data)
    df = get_df(headers, params_data)
    df_to_txt(df)
    print(f"数据已保存，共{len(df)}条")
