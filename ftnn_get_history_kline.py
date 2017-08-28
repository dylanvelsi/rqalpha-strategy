from rqalpha.api import *
from openft.open_quant_context import *
# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
import talib
import pandas as pd
import numpy


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    # 在context中保存全局变量
    context.s1 = "HK.00700"

    context.quote_context = OpenQuoteContext(host='127.0.0.1', port=11111)#119.29.141.202
    # 获取推送数据
    #context.quote_context.subscribe(context.s1, "QUOTE", push=True)
    #quote_context.set_handler(_example_history_kline(quote_context))
    #ret_code, context.kline_table = context.quote_context.get_stock_basicinfo("US", stock_type='STOCK')
    ret_code, context.kline_table = context.quote_context.get_history_kline(context.s1, start='2000-01-01', end='2017-06-01', ktype='K_DAY',
                                                     autype='qfq')
    #context.quote_context.start()
    print(context.kline_table)
    #context.kline_table.to_csv('US.AAPL_d.csv')
    #print(context.kline_table[['code', 'close']].head(10))

# before_trading此函数会在每天策略交易开始前被调用，当天只会被调用一次
def before_trading(context):
    pass

# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    pass

# after_trading函数会在每天交易结束后被调用，当天只会被调用一次
def after_trading(context):
    pass