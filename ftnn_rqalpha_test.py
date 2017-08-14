from rqalpha.api import *
from openft.open_quant_context import *
# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
import talib

def _example_history_kline(quote_ctx):
    """
    获取历史K线，输出 股票代码，时间，开盘价，收盘价，最高价，最低价，成交量，成交额
    """
    # subscribe Kline
    stock_code_list = ["US.AAPL", "HK.00700"]
    sub_type_list = ["K_DAY"]

    for code in stock_code_list:
        for sub_type in sub_type_list:
            ret_status, ret_data = quote_ctx.subscribe(code, sub_type)
            if ret_status != RET_OK:
                print("%s %s: %s" % (code, sub_type, ret_data))
                exit()

    ret_status, ret_data = quote_ctx.query_subscription()

    if ret_status == RET_ERROR:
        print(ret_data)
        exit()

    print(ret_data)

    for code in stock_code_list:
        for ktype in ["K_DAY"]:
            ret_code, ret_data = quote_ctx.get_history_kline(code, start='2016-01-01', end='2017-01-01', ktype='K_DAY', autype='qfq')
            if ret_code == RET_ERROR:
                print(code, ktype, ret_data)
                exit()
            kline_table = ret_data
            print("%s KLINE %s" % (code, ktype))
            print(kline_table.dtypes)
            print(kline_table[['code', 'close']].head(10))
            #print(kline_table)
            print("\n\n")


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    # 在context中保存全局变量
    context.s1 = "000001.XSHE"
    context.dateoffset = 0
    # 设置这个策略当中会用到的参数，在策略中可以随时调用，这个策略使用长短均线，我们在这里设定长线和短线的区间，在调试寻找最佳区间的时候只需要在这里进行数值改动
    context.SHORTPERIOD = 20
    context.LONGPERIOD = 120
    #orderid = all_instruments('CS')
    #print(orderid.dtypes)
    #print(orderid[['order_book_id', 'symbol']].head(10))

    context.quote_context = OpenQuoteContext(host='119.29.141.202', port=11111)
    # 获取推送数据
    context.quote_context.subscribe('HK.00700', "QUOTE", push=True)
    #quote_context.set_handler(_example_history_kline(quote_context))
    ret_code, context.kline_table = context.quote_context.get_history_kline("HK.00700", start='2014-01-01', end='2017-01-01', ktype='K_DAY',
                                                     autype='qfq')
    context.quote_context.start()
    print(context.kline_table['close'].head(10))
    #print(context.kline_table[['code', 'close']].head(10))

# before_trading此函数会在每天策略交易开始前被调用，当天只会被调用一次
def before_trading(context):
    pass

# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):

    # 因为策略需要用到均线，所以需要分拆历史数据
    prices = context.kline_table.loc[context.dateoffset:context.dateoffset+context.LONGPERIOD+1, ['close']].T.values[0]
    ++context.dateoffset
    #pricesX = history_bars(context.s1, context.LONGPERIOD+1, '1d', 'close')
    #current_snapshot(context.s1)
    #orderid = all_instruments('FenjiA')
    #print(orderid)
    print(prices[0])
    #print(pricesX)
    # 使用talib计算长短两根均线，均线以array的格式表达
    short_avg = talib.SMA(prices, context.SHORTPERIOD)
    long_avg = talib.SMA(prices, context.LONGPERIOD)
    mid_avg = talib.SMA(prices, 55)

    plot("short avg", short_avg[-1])
    plot("long avg", long_avg[-1])
    plot("mid avg", mid_avg[-1])
    plot("prices", prices[-1])

    # 计算现在portfolio中股票的仓位
    cur_position = context.portfolio.positions[context.s1].quantity
    # 计算现在portfolio中的现金可以购买多少股票
    shares = context.portfolio.cash/bar_dict[context.s1].close

    # 如果短均线从上往下跌破长均线，也就是在目前的bar短线平均值低于长线平均值，而上一个bar的短线平均值高于长线平均值
    if short_avg[-1] - long_avg[-1] < 0 and short_avg[-2] - long_avg[-2] > 0 and cur_position > 0:
        # 进行清仓
        order_target_value(context.s1, 0)

    # 如果短均线从下往上突破长均线，为入场信号
    if short_avg[-1] - long_avg[-1] > 0 and short_avg[-2] - long_avg[-2] < 0:
        # 满仓入股
        order_shares(context.s1, shares)

# after_trading函数会在每天交易结束后被调用，当天只会被调用一次
def after_trading(context):
    pass