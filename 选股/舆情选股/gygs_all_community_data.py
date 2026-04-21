import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
import os
import json
import requests
import json
from datetime import datetime
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import json


def get_community_data(page):
    url = "https://app.jiuyangongshe.com/jystock-app/api/v2/article/community"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-length": "74",
        "content-type": "application/json",
        "cookie": "Hm_lvt_58aa18061df7855800f2a1b32d6da7f4=1734826412; Hm_lpvt_58aa18061df7855800f2a1b32d6da7f4=1734826419",
        "origin": "https://www.jiuyangongshe.com",
        "platform": "3",
        "priority": "u=1, i",
        "referer": "https://www.jiuyangongshe.com/",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "timestamp": "1734826429268",
        "token": "bc572bf828613c03ce04dc00f444ec9f",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    data = {
        "category_id": "",
        "limit": 15,
        "order": 1,
        "start": 0,
        "type": 0,
        "back_garden": 0,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("获取成功", "{}".format(page))
    else:
        raise Exception("获取失败, 状态码: {}".format(response.status_code))

    return response


import pandas as pd


def html_df(response):
    data_list = []
    html_json = response.json()["data"]["result"]

    data_list = []

    for item in html_json:
        data_dict = {}

        for key in item.keys():
            data_dict[key] = item[key]

        data_dict["nickname"] = item["user"]["nickname"]
        data_dict["create_time"] = item["create_time"]

        data_list.append(data_dict)

    df = pd.DataFrame(data_list)
    df["create_time"] = pd.to_datetime(df["create_time"])

    return df


import pandas as pd
from datetime import datetime, timedelta


import pandas as pd
from datetime import datetime, timedelta


def _get_all_community_data(
    pre_date=3, start_date=None, end_date=None, pages=15, remove_duplicates=True
):
    if start_date is None:
        start_date = (
            (datetime.now() - timedelta(pre_date))
            .replace(hour=0, minute=0, second=0)
            .strftime("%Y-%m-%d %H:%M:%S")
        )

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    all_df = pd.DataFrame()

    for i in range(1, pages + 1):
        response_json = get_community_data(i)
        current_df = html_df(response_json)

        all_df = pd.concat([all_df, current_df], ignore_index=True)

        print("第", i, "页, 共获得数据：", len(all_df), "条")

    if remove_duplicates:
        all_df = all_df.drop_duplicates(subset=["title", "article_id"], keep="first")
        print("去重后剩余", len(all_df), "条")

    print(start_date, end_date)

    all_df = all_df[all_df["create_time"] >= start_date]

    if name_list is not None:
        if len(name_list) > 0:
            all_df = all_df[all_df["nickname"].isin(name_list)]
            print("筛选作者", name_list, "的所有数据，共", len(all_df), "条")

    print("筛选后剩余", len(all_df), "条")

    all_df.to_csv("all_df.csv", encoding="utf-8")

    return all_df


import re


def clean_text(text):
    patterns = [
        "回复",
        "投稿",
        "第一页",
        "1",
        "前一页",
        "前",
        "页",
        "确认订单",
        "取消",
        "确认",
        "0 0",
        "谢谢",
        "赞赏",
        "赞赏",
        "关注",
        "关注",
        "已关注",
        "作业",
        "时间",
        "财经AI",
        "通知",
        "全部",
        "通知",
        "私",
        "记号",
        "我的",
        "退出",
        "微信视频",
        "一路",
        "微信视频",
        "转",
        "转为证投投研",
        "置",
        "关注",
        "置",
        "确",
        "关注我的",
        "转",
        "收",
        "关注",
        "财经",
        "只",
        "看",
        "回",
        "回本",
        "关注",
        "置",
        "置为投顾",
        "回",
        "回",
        "转为投顾",
        "投资研",
        "经",
        "投资",
        "投研",
        "置",
        "置为",
        "投研经",
        "投研经",
        "投研",
        "投资",
        "投资",
        "投研",
        "经",
        "投研",
        "经",
        "投资",
        "投研",
        "经",
        "投研经",
        "投资经",
        "投研经",
        "投资经",
        "投研经",
        "投资经",
        "投研经",
        "投研经",
        "投资经",
        "投研经",
        "置",
        "置",
        "置",
        "置",
    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text)

    return text


def html_to_txt(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    return text


def get_jygs_data_txt(url):
    wendang_id = url.split("a/")[-1]

    with sync_playwright() as p:
        browser = p.chromium.launch(True)
        page = browser.new_page()

        page.goto(url)
        time.sleep(5)

        page_source = page.content()

        soup = BeautifulSoup(page_source, "html.parser")
        text = soup.get_text(strip=True)

        txt = html_to_txt(text)

        print(txt)

        return txt


from datetime import datetime, timedelta


def get_text_list(
    pre_date=3,
    start_date=None,
    end_date=None,
    pages=15,
    remove_duplicates=True,
    save_to_txt=False,
):
    df = _get_all_community_data(
        pre_date, start_date, end_date, pages, remove_duplicates
    )

    base_url = "https://www.jiuyangongshe.com/a/"

    url_list = [base_url + article_id for article_id in df["article_id"]]

    all_texts = []

    url_num = 1

    for url in url_list:
        print("正在获取第{}个链接，共{}个".format(url_num, url))

        try:
            text = get_jygs_data_txt(url)
            all_texts.append(text)

            time.sleep(2)

            url_num += 1
        except Exception as e:
            url_num += 1
            print("第", url_num, "个链接：", url, "错误：", str(e))
            continue

    print("数据保存完毕")

    if save_to_txt:
        datatime = datetime.now().strftime("%Y%m%d")
        txt_filename = "{}-九 syndicated.txt".format(datatime)
        print("文本已被保存为 ", txt_filename)

    return str(all_texts)
