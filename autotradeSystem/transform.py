import pandas as pd
import datetime
from icecream import ic

today_time = datetime.datetime.now().strftime('%Y%m%d')

DEFAULT_PATH1 = f'交易_{today_time}_策略替换.csv'
DEFAULT_OUT1 = f'精选_{today_time}_策略替换.csv'

DEFAULT_PATH2 = f'交易_{today_time}.csv'
DEFAULT_OUT2 = f'交易_{today_time}_.csv'


def transform_strategy(path=DEFAULT_PATH1, path_out=DEFAULT_OUT1):
    new_table = pd.DataFrame()
    try:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}).dropna(how='all')
    except:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}, encoding='gbk').dropna(how='all')

    df_htjx = df_data_all.query("账户名称=='鸿通精选'")
    new_table.loc[:, '证券代码'] = df_htjx['股票代码'].agg(lambda x: (6 - len(x)) * '0' + x)
    new_table.loc[:, '市场'] = df_htjx['股票代码'].agg(lambda x: 2 if int(x) < 600000 else 1)
    new_table.loc[:, '委托方向'] = df_htjx['交易方向'].astype(str).agg(lambda x: 1 if x == '买入' else 2)
    new_table.loc[:, '交易股数'] = df_htjx['交易股数']
    new_table = new_table.set_index('证券代码')
    new_table.to_csv(path_out)


def transform_trade_data(path=DEFAULT_PATH2, path_out=DEFAULT_OUT2):
    try:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}).dropna(how='all')
    except:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}, encoding='gbk').dropna(how='all')

    df_data_all.loc[:, '金额'] = df_data_all.agg(lambda x: x['交易股数'] * x['实时价格'], axis=1)
    series_money = df_data_all.groupby(['账户名称','交易方向'])['金额'].sum()
    ic(series_money)
    # df_data_all.to_csv(path_out)

def check(df_fl):
    today_time = datetime.datetime.now().strftime('%Y%m%d')
    DEFAULT_PATH2 = f'交易_{today_time}.csv'
    data = pd.read_csv(DEFAULT_PATH2)
    list_fl = df_fl['策略名称']
    pass



if __name__ == '__main__':
    transform_trade_data()
