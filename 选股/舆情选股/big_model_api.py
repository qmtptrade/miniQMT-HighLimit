import sys
from openai import OpenAI
from gygs_all_community_data import get_text_list
import configparser
import os


def load_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "..", "配置文件", "config.ini")
    print("配置文件路径: ", config_path)

    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")

    api_key = config.get("BigModel", "api_key")
    model_name = config.get("BigModel", "model_name")
    gygs_data_hours = config.get("BigModel", "gygs_data_hours")

    return api_key, model_name, float(gygs_data_hours)


def big_model_select_stock(api_key: str, model_name: str, text_body: str) -> list:
    re = None

    text = """
        1【股票的题材要新鲜】
            题材最好是与当前热点风口相结合的强基本面，强势题材出强势股。不要去看那些已经过时的题材，那些已经涨高的题材不要去追，短线强势股回调之后还能继续走强。
            选股要求：市值小、股价低、筹码相对集中、股性活跃、换手率高。基本面要好，要有题材支撑。
            需要认真学习
        2【股票的跌幅】
            跌幅最好不同波段有不同幅度的调整，不要一次性跌幅太大。例如，跌幅超过40%不要去看，涨幅超过一倍以上不要去看跌幅超过50%更不要去看涨幅超过两倍以上更不要去。
            同时，还要关注跌幅排行，跌幅排行越靠前，后期上涨的概率越大。跌幅排行越靠后，后期越有可能成为牛股，涨幅翻倍甚至更多。买入时机选择在跌幅排行靠前的股票里。
            跌幅排行靠后的股票里也有例外，比如一些医药板块的细分龙头跌幅超过70%，这类股票可能在未来成为超级牛股。买入时机选择跌幅在30%到50%区间的。
            跌幅排行前几名的股票不要去看，涨幅已经翻倍的不要去看跌幅超过60%的不要去看跌幅超过80%更不要去看涨幅超过三倍以上的更不要去。
            跌幅排行越靠后，涨幅可能会更大跌幅排行越靠后跌幅空间越小跌幅排行靠后的股票里也有例外。
        3【股票的市值】
            股票的流通市值，最好为20亿到100亿之间的市值。
            不要选市值太小的股票比如5000万以下市值太小容易导致流动性不足。不要选市值太大的股票比如超过1000亿以上，流动性不足。不要选市值太小的股票，比如5000万以下市值太小，容易导致流动性不足。
            不要选市值太小的股票，比如5000万以下市值太小，容易导致流动性不足。不要选市值太大的股票，比如超过1000亿以上，流动性不足。不要选市值太小的股票，比如5000万以下，容易导致流动性不足。
            买入时间选择跌幅超过30%的股票跌幅超过50%的股票涨幅超过100%的股票跌幅超过60%的股票买入时机很重要。
            当大盘下跌时跌幅超过20%，当行业下跌时跌幅超过30%，当个股下跌时跌幅超过40%，当板块下跌时跌幅超过50%。
            当市场整体下跌跌幅超过20%时跌幅超过30%时跌幅超过50%时跌幅超过60%时跌幅超过80%时买入时机很重要。
            涨幅超过三倍以上的股票涨幅超过五倍以上的股票涨幅超过十倍以上的股票涨幅超过二十倍以上的股票。
            重要提示：次新股市值小、题材好赛道好、筹码集中、股性活跃、换手率高。
        4【公司质量】公司质量越好，涨幅越大，���幅越大，涨幅越大涨幅越大。
    """

    print("模型开始工作")
    question = "给出的第一个数据集是全部的股票名称，请判断哪些是好的股票并给出股票代码和名称，一行一个股票"

    all_text = text + text_body
    text_size = sys.getsizeof(all_text) / 1024

    if text_size > 128:
        print("文本太大，超过128k，无法处理。文本大小: ", text_size, " KB")
        return ""

    if model_name == "kimi":
        client = OpenAI(api_key=api_key, base_url="https://api.moonshot.cn/v1")
        model = "moonshot-v1-128k"
    elif model_name == "step":
        client = OpenAI(api_key=api_key, base_url="https://api.stepfun.com/v1")
        model = "step-1-128k"
    else:
        print("模型名称错误")
        return ""

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": text},
            {"role": "system", "content": text_body},
            {"role": "user", "content": question},
        ],
        temperature=0.3,
    )

    result = completion.choices[0].message.content

    print("模型返回结果")
    print("开始提取可选出股")

    with open("./all_stock_names.txt", "r", encoding="gbk") as f:
        stock_names = [line.strip() for line in f.readlines() if line.strip()]

    pattern = "|".join([re.escape(stock) for stock in stock_names])
    big_model_stock_pool = re.findall(pattern, result)

    return big_model_stock_pool


def save_to_txt(big_model_stock_list):
    with open("./big_model_stock_poll.txt", "w", encoding="utf-8") as f:
        for item in big_model_stock_list:
            f.write(item + "\n")


if __name__ == "__main__":
    api_key, model_name, gygs_data_hours = load_config()
    text_body = get_text_list(gygs_data_hours, False)
    big_model_stock_list = big_model_select_stock(api_key, model_name, text_body)
    save_to_txt(big_model_stock_list)
