import sys
import re
import os
import configparser
from openai import OpenAI
from gygs_all_community_data import get_text_list


SYSTEM_PROMPT = """
1【股票的题材要新鲜】题材最好与当前热点风口结合，强基本面出强势股。不要追已过时的题材，短线强势股回调后仍可走强。选股要求：市值小、股价低、筹码集中、股性活跃、换手率高。
2【股票的跌幅】跌幅最好不同波段有不同幅度调整。跌幅超过40%、涨幅超过一倍的不看；跌幅超过50%、涨幅超过两倍的不看；跌幅超过60%、涨幅超过三倍的更不要看。跌幅排行越靠前，后期上涨概率越大。跌幅30%-50%区间是较好买入时机。医药细分龙头跌幅超70%可能成为超级牛股。
3【股票的市值】流通市值最好20亿到100亿之间。市值5000万以下流动性不足，1000亿以上也不选。次新股：小市值、题材好、筹码集中、股性活跃、换手率高。
4【公司质量】公司质量越好，涨幅越大。
"""


def load_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "..", "配置文件", "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    return (
        config.get("BigModel", "api_key"),
        config.get("BigModel", "model_name"),
        float(config.get("BigModel", "gygs_data_hours")),
    )


def big_model_select_stock(api_key: str, model_name: str, text_body: str) -> list:
    all_text = SYSTEM_PROMPT + text_body
    text_size = sys.getsizeof(all_text) / 1024

    if text_size > 128:
        print(f"文本太大，超过128k，无法处理。文本大小: {text_size} KB")
        return []

    base_urls = {
        "kimi": ("https://api.moonshot.cn/v1", "moonshot-v1-128k"),
        "step": ("https://api.stepfun.com/v1", "step-1-128k"),
    }
    if model_name not in base_urls:
        print("模型名称错误")
        return []

    base_url, model = base_urls[model_name]
    client = OpenAI(api_key=api_key, base_url=base_url)

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": text_body},
            {
                "role": "user",
                "content": "给出的第一个数据集是全部的股票名称，请判断哪些是好的股票并给出股票代码和名称，一行一个股票",
            },
        ],
        temperature=0.3,
    )

    result = completion.choices[0].message.content

    with open("./all_stock_names.txt", "r", encoding="gbk") as f:
        stock_names = [line.strip() for line in f if line.strip()]

    pattern = "|".join([re.escape(stock) for stock in stock_names])
    return re.findall(pattern, result)


def save_to_txt(big_model_stock_list, output_file="./big_model_stock_poll.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(big_model_stock_list))


if __name__ == "__main__":
    api_key, model_name, gygs_data_hours = load_config()
    text_body = get_text_list(gygs_data_hours, False)
    big_model_stock_list = big_model_select_stock(api_key, model_name, text_body)
    save_to_txt(big_model_stock_list)
