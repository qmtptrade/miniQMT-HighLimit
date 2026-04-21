import requests
import json
import re
import os
import time
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


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
    if response.status_code != 200:
        raise Exception(f"获取失败, 状态码: {response.status_code}")
    return response


def get_all_community_data(
    pre_date=3,
    start_date=None,
    end_date=None,
    pages=15,
    remove_duplicates=True,
    name_list=None,
):
    start_date = start_date or (datetime.now() - timedelta(pre_date)).replace(
        hour=0, minute=0, second=0
    ).strftime("%Y-%m-%d %H:%M:%S")
    end_date = end_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    all_df = pd.DataFrame()
    for i in range(1, pages + 1):
        current_df = html_df(get_community_data(i))
        all_df = pd.concat([all_df, current_df], ignore_index=True)

    if remove_duplicates:
        all_df = all_df.drop_duplicates(subset=["title", "article_id"], keep="first")

    all_df = all_df[all_df["create_time"] >= start_date]

    if name_list:
        all_df = all_df[all_df["nickname"].isin(name_list)]

    all_df.to_csv("all_df.csv", encoding="utf-8")
    return all_df


def html_df(response):
    html_json = response.json()["data"]["result"]
    data_list = [
        {
            **item,
            "nickname": item["user"]["nickname"],
            "create_time": item["create_time"],
        }
        for item in html_json
    ]
    df = pd.DataFrame(data_list)
    df["create_time"] = pd.to_datetime(df["create_time"])
    return df


CLEAN_PATTERNS = [
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
    "关注",
    "已关注",
    "作业",
    "时间",
    "财经AI",
    "通知",
    "全部",
    "私",
    "记号",
    "我的",
    "退出",
    "微信视频",
    "一路",
    "转",
    "转为证投投研",
    "置",
    "确",
    "关注我的",
    "收",
    "财经",
    "只",
    "看",
    "回",
    "回本",
    "置为投顾",
    "转为投顾",
    "投资研",
    "经",
    "投资",
    "投研",
    "置为",
    "投研经",
    "投资经",
]


def clean_text(text):
    for pattern in CLEAN_PATTERNS:
        text = re.sub(pattern, "", text)
    return text


def html_to_txt(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def get_jygs_data_txt(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(True)
        page = browser.new_page()
        page.goto(url)
        time.sleep(5)
        page_source = page.content()
        soup = BeautifulSoup(page_source, "html.parser")
        text = soup.get_text(strip=True)
        return html_to_txt(text)


def get_text_list(
    pre_date=3,
    start_date=None,
    end_date=None,
    pages=15,
    remove_duplicates=True,
    save_to_txt=False,
    name_list=None,
):
    df = get_all_community_data(
        pre_date, start_date, end_date, pages, remove_duplicates, name_list
    )
    url_list = [
        "https://www.jiuyangongshe.com/a/" + article_id
        for article_id in df["article_id"]
    ]
    all_texts = []

    for url_num, url in enumerate(url_list, 1):
        try:
            text = get_jygs_data_txt(url)
            all_texts.append(text)
            time.sleep(2)
        except Exception as e:
            print(f"第{url_num}个链接出错: {url}, 错误: {e}")

    if save_to_txt:
        txt_filename = f"{datetime.now().strftime('%Y%m%d')}-九 syndicated.txt"

    return str(all_texts)
