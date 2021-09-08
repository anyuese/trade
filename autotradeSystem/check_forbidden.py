#coding=gbk
import pandas as pd
import datetime
from icecream import ic

today_time = datetime.datetime.now().strftime('%Y%m%d')
delta_day = datetime.timedelta(days=1)
yesterday_time = (datetime.datetime.today()-delta_day).strftime('%Y%m%d')

PATH1 = f'持仓_{today_time}.csv'
PATH2 = '禁选池.csv'
PATH3 = f'交易_{today_time}.csv'
PATH4 = f'持仓_{yesterday_time}.csv'

def read_resposity(path=PATH4):
    print('------核对PATH:',path)
    try:
        resposity = pd.read_csv(open(path, 'rb'), encoding='gbk')
    except:
        resposity = pd.read_csv(open(path, 'rb'), encoding='utf8')
    resposity = resposity[['股票代码', '股票名称', '数量','策略名称','账户名称']]
    return resposity

def get_forbidden(path=PATH2):
    forbidden = pd.read_csv(open(path,'r',encoding='gbk'))
    return forbidden['股票代码'].tolist()

def process_check(forbidden,resposity):
    out_put = pd.DataFrame()
    print('----------------与禁选池有关记录-------------')
    out_put =  resposity[resposity['股票代码'].isin(forbidden)]
    ic(out_put)

def get_trade_data(path=PATH3):
    print('--------核对文件',path)
    try:
        trade_data = pd.read_csv(open(path,'rb'))
    except:
        trade_data = pd.read_csv(open(path, 'r',encoding='gbk'))
    return trade_data

if __name__ == '__main__':
    process_check(get_forbidden(),get_trade_data())

