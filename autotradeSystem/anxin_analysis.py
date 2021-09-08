import pandas as pd
import numpy as np
from jqdatasdk import *
import datetime
from icecream import ic

today_time = datetime.datetime.now().strftime('%Y%m%d')
# path = '持仓_{}.csv'.format(today_time)

delta_day = datetime.timedelta(days=1)
yesterday_time = (datetime.datetime.today()-delta_day).strftime('%Y%m%d')
path = f'持仓_{yesterday_time}.csv'
OUT_PATH = r'C:\Users\fxz.HT-9-DB-SV1\PycharmProjects\guoren\anxin'
RESULT = pd.DataFrame(columns=['股票名称','股票代码','买入时间','买入价格','成本','卖出时间','卖出价格','交易数量','卖出所得','盈亏','输赢'])

def trade_init():
    data = pd.read_csv(open('成交结果明细.csv', 'rb'), encoding='gbk')
    data = data[['证券代码', '成交日期', '成交时间', '方向', '成交数量', '成交价格', '证券名称']]
    data.loc[:, '金额'] = data.agg(lambda x: x['成交价格'] * x['成交数量'], axis=1)
    data.set_index('成交日期', inplace=True)
    data.sort_values(['成交日期','成交时间'],inplace=True)
    print(data)
    return data

def trade_group(data):
    for index, group in data.groupby(['证券代码']):
        print(group)
    groups = data.groupby(['证券代码'])
    print(groups.agg({'金额': 'sum'}))
    return groups

def modify_code(code):
    code = str(code)
    if len(code) < 6:
        code = (6 - len(code)) * '0' + code
    if code.startswith('6'):
        code = code + '.XSHG'
    else:
        code = code + '.XSHE'
    return code


def read_desposity(path=path):
    try:
        desposity = pd.read_csv(open(path, 'rb'), encoding='gbk').query('账户名称=="自营"')
    except:
        desposity = pd.read_csv(open(path, 'rb'), encoding='utf8').query('账户名称=="自营"')
    desposity = desposity[['股票代码', '股票名称', '数量']]
    print(desposity)
    return desposity


def responsity_get_price(desposity):
    auth('18274054038', '054038')
    codes = desposity['股票代码'].tolist()
    codes = [modify_code(code) for code in codes]
    nums = desposity['数量'].tolist()
    prices = list()
    moneys = list()
    tmp_moneys = list()
    dicts = dict(zip(codes, nums))
    data_frame = pd.DataFrame()

    for code in codes:
        tmp_table = pd.DataFrame()
        df = get_price(code, start_date='2021-8-4', end_date=datetime.datetime.now(), frequency='daily')
        tmp_table.loc[:, '日期'] = df.index
        tmp_table.loc[:, '股票代码'] = code
        tmp_table.loc[:, 'close'] = df['close'].tolist()
        tmp_table.loc[:, '数量'] = dicts[code]
        tmp_table.loc[:, '金额'] = tmp_table.loc[:, 'close'] * tmp_table.loc[:, '数量']
        data_frame = pd.concat([data_frame, tmp_table])

    result = pd.DataFrame()
    for name, group in data_frame.groupby(['日期']):
        result = pd.concat([result, group])
    result.to_csv(f'{OUT_PATH}\\价格金额表.csv', index=False)
    return result


def get_every_capital(path=OUT_PATH):
    desposity = pd.read_csv(open(path + r'\价格金额表.csv', 'rb'))
    net_value = desposity.groupby(['日期'])['金额'].sum()
    net_value = pd.DataFrame(net_value, columns=['金额'])
    net_value.loc[:, '金额'] = net_value['金额'] + 136
    net_value.loc[:, '净值'] = net_value['金额'] / 616371.0
    net_value.to_csv(path + r'\模拟净值表.csv')
    print(net_value)

def cal_winning_probability_detail(groups):
    flag = True
    count_trade_all = 0
    count_right = 0
    count_error = 0
    print(len(groups))
    for name, group in groups:
        exit_flag = 0
        tmp_trade_buy = group[group['方向'] == '买入']
        tmp_trade_sell = group[group['方向'] == '卖出']
        tmp_trade_buy_copy = tmp_trade_buy.copy()
        tmp_trade_sell_copy = tmp_trade_sell.copy()
        count_buy = len(tmp_trade_buy)
        count_sell = len(tmp_trade_sell)
        count_trade = min([count_buy, count_sell])
        count_trade_all += count_trade
        ic(count_buy, count_sell, count_trade)
        ic(tmp_trade_buy, tmp_trade_sell)
        start_sell_position = 0
        start_buy_position = 0
        next_start_buy_position = 0
        next_start_sell_position = 0
        buy_position = 0
        sell_position = 0
        tmp_k = 0
        # start_position 为当前窗口开始位置，next_start_positon为窗口下次开始位置,buy_position为当前位置
        for i in range(count_trade):
            try:
                flag = True
                while flag:
                    if tmp_k ==0:
                        count_buynum, count_sellnum = tmp_trade_buy['成交数量'].iloc[start_buy_position], \
                                                  tmp_trade_sell['成交数量'].iloc[start_sell_position]
                    else:
                        start_buy_position,start_sell_position = next_start_buy_position,next_start_sell_position
                        buy_position,sell_position = next_start_buy_position,next_start_sell_position
                        count_buynum, count_sellnum = tmp_trade_buy['成交数量'].iloc[start_buy_position], \
                                                      tmp_trade_sell['成交数量'].iloc[start_sell_position]
                    if (count_sellnum - count_buynum) > 400:
                        next_start_buy_position = buy_position + 1
                        count_buynum += tmp_trade_buy['成交数量'].iloc[buy_position]
                        next_start_buy_position = buy_position
                    elif (count_buynum - count_sellnum) > 400:
                        sell_position = sell_position + 1
                        count_sellnum += tmp_trade_sell['成交数量'].iloc[sell_position]
                        next_start_sell_position = sell_position
                    tmp_k += 1
                    if abs(count_sellnum - count_buynum) <= 400:
                        flag = False
                        count_tradenum = min(count_sellnum, count_buynum)
                        if (buy_position + 1) <= count_buy:
                            next_start_buy_position = buy_position+1
                        if (sell_position + 1 ) <= count_sell:
                            next_start_sell_position = sell_position+1
                        break
                    if tmp_k >= 10:
                        raise Exception
                # ic(start_buy_position,next_start_buy_position,start_sell_position,next_start_sell_position)
                tmp_trade_buy_copy = tmp_trade_buy.iloc[start_buy_position:next_start_buy_position].copy()
                tmp_trade_sell_copy = tmp_trade_sell.iloc[start_sell_position:next_start_sell_position].copy()
            except Exception:
                single_buy_num = tmp_trade_buy['成交数量'].sum()
                single_sell_num = tmp_trade_sell['成交数量'].sum()
                count_tradenum = min(single_buy_num,single_sell_num)
                exit_flag = 1
            finally:
                single_buy_costall = tmp_trade_buy_copy['金额'].sum()
                single_buy_num = tmp_trade_buy_copy['成交数量'].sum()
                single_sell_num = tmp_trade_sell_copy['成交数量'].sum()
                single_sell_costall = tmp_trade_sell_copy['金额'].sum()
                single_buy_cost = 5+ count_tradenum * single_buy_costall / single_buy_num
                single_sell_cost = (1-0.001)*count_tradenum * single_sell_costall / single_sell_num - 5
                time_buy1,time_buy2 = tmp_trade_buy_copy.index[-1],tmp_trade_buy_copy['成交时间'].iloc[-1]
                time_sell1, time_sell2 = tmp_trade_sell_copy.index[-1], tmp_trade_sell_copy['成交时间'].iloc[-1]
                time_buy,time_sell = f'{time_buy1} {time_buy2}',f'{time_sell1} {time_sell2}'
                stock_name = tmp_trade_buy_copy['证券名称'].iloc[0]
                ic(single_buy_costall, single_sell_costall, single_buy_cost,single_sell_cost, count_tradenum)
                ic(time_buy,time_sell)
                generate_result(code=name,name=stock_name,buy_time=time_buy,buy_price=tmp_trade_buy_copy['成交价格'].iloc[-1],buy_cost=single_buy_cost,
                            sell_time=time_sell,sell_price=tmp_trade_sell_copy['成交价格'].iloc[-1],sell_cost=single_sell_cost,tradenum=count_tradenum)
                if exit_flag == 1:
                    break

def cal_winning_simple(groups):
    result = pd.DataFrame()
    for name,group in groups:
        trade_buy_count = group[group['方向'] == '买入'].shape[0]
        ic(trade_buy_count)
        trade_sell_count = group[group['方向']=='卖出'].shape[0]
        ic(trade_sell_count)
        sell_all = group[group['方向']=='卖出']['金额'].sum()
        sell_num = group[group['方向']=='卖出']['成交数量'].sum()

        buy_all = group[group['方向'] == '买入']['金额'].sum()
        buy_num = group[group['方向'] == '买入']['成交数量'].sum()

        diff_money1 = sell_all-buy_all
        diff_count = sell_num - buy_num
        count_trade = min(sell_num,buy_num)
        code_name = group['证券名称'].tolist()[0]
        diff_money = ((1-0.001)*(sell_all/sell_num*count_trade)-(5*trade_sell_count)) - ((5*trade_buy_count)+(buy_all/buy_num*count_trade))
        tmp_df = pd.DataFrame([{'股票代码':name,'股票名称':code_name,'买入数量':buy_num,'买入成交':buy_all,'卖出数量':sell_num,'卖出成交':sell_all,'交易数量':count_trade,'盈亏额':diff_money}],
                              columns=['股票代码','股票名称','买入数量','买入成交','卖出数量','卖出成交','交易数量','盈亏额'])
        ic(group)
        ic(buy_num,sell_num,sell_all,count_trade,diff_money1,diff_money)
        result = pd.concat([result,tmp_df])
    all_diff = result['盈亏额'].sum()
    result = result.append(pd.DataFrame([[],['总盈亏额：',all_diff]],columns=['交易数量','盈亏额']))
    result.to_csv(OUT_PATH+ r'\交易累计表.csv',index=False)
    ic(result)
    ic(all_diff)

def generate_result(code,name,buy_time,buy_price,buy_cost,sell_time,sell_price,sell_cost,tradenum):
    diff = sell_cost - buy_cost
    right_error = '正' if diff>0 else '负'
    new_rows = pd.DataFrame([[name,code,buy_time,buy_price,buy_cost,sell_time,sell_price,tradenum,sell_cost,diff,right_error]],
                            columns=['股票名称','股票代码','买入时间','买入价格','成本','卖出时间','卖出价格','交易数量','卖出所得','盈亏','输赢'])
    global RESULT
    RESULT = RESULT.append(new_rows,ignore_index=True)

def write_result():
    global RESULT
    RESULT = RESULT.set_index('股票名称')
    RESULT.sort_values(['卖出时间'], inplace=True)
    all_dif = RESULT['盈亏'].sum()
    winning_ = RESULT['输赢'].value_counts().to_dict()
    winning_probability = winning_['正']/(winning_['正']+winning_['负'])
    wining_money = RESULT.query('输赢=="正"')['盈亏'].sum()
    loss_money = RESULT.query('输赢=="负"')['盈亏'].sum()
    every_win = wining_money/winning_['正']
    every_loss = loss_money/winning_['负']
    info = pd.DataFrame([[],['总盈亏',all_dif,' ','盈利次数:',winning_['正'],' ','亏损次数:',winning_['负'],' ','胜率:',winning_probability],
                         ['盈利总额:', wining_money, ' ', '每次均盈利:', every_win, ' ','亏损总额:',loss_money,' ','每次均亏损:', every_loss]],
                                        columns=['股票名称','股票代码','买入时间','买入价格','成本','卖出时间','卖出价格','交易数量','卖出所得','盈亏','输赢'])
    print(info)
    info.set_index('股票名称',inplace=True)
    RESULT = RESULT.append(info)
    RESULT.to_csv(OUT_PATH+ r'\交易胜负表.csv')

if __name__ == '__main__':
    data = trade_init()
    groups = trade_group(data)
    cal_winning_simple(groups)
    cal_winning_probability_detail(groups)
    write_result()
    desposity = read_desposity()
    responsity_get_price(desposity)
    get_every_capital()
