import pandas as pd
import datetime
from icecream import ic
from update_guoren import *
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

today_time = datetime.datetime.now().strftime('%Y%m%d')

DEFAULT_PATH1 = f'交易_{today_time}_策略替换.csv'
DEFAULT_OUT1 = f'精选_{today_time}_策略替换.csv'

DEFAULT_PATH2 = f'交易_{today_time}.csv'
DEFAULT_OUT2 = f'交易_{today_time}_.csv'

FL_PATH = '放量上影线.csv'
GW_path = '高位放量上影线.csv'
GUO_REN = '果仁网址配置表.csv'

DIR_NAME = r'C:\Users\fxz.HT-9-DB-SV1\PycharmProjects\guoren'


def transform_moudle_HT(path=DEFAULT_PATH2, path_out=f'交易_{today_time}_鸿通精选.csv'):
    new_table = pd.DataFrame()
    try:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}).dropna(how='all')
    except:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}, encoding='gbk').dropna(how='all')

    df_htjx = df_data_all.query("账户名称=='鸿通精选'")
    new_table.loc[:, '证券代码'] = df_htjx['股票代码'].agg(lambda x: (6 - len(x)) * '0' + x)
    new_table.loc[:, '市场'] = df_htjx['股票代码'].agg(lambda x: 2 if int(x) < 600000 else 1)
    new_table.loc[:, '委托方向'] = df_htjx['交易方向'].astype(str).agg(lambda x: 1 if x == '买入' else 2)
    new_table.loc[:, '数量'] = df_htjx['交易股数']
    new_table = new_table.set_index('证券代码')
    new_table.to_csv(path_out)

def transform_moudle_GJ(path=DEFAULT_PATH2, path_out=f'交易_{today_time}_鸿通2号.csv'):
    new_table = pd.DataFrame()
    try:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}).dropna(how='all')
    except:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}, encoding='gbk').dropna(how='all')
    df_htjx = df_data_all.query("账户名称=='鸿通精选'")
    new_table.loc[:, '股票代码'] = df_htjx['股票代码'].agg(lambda x: int(x))
    new_table.loc[:, '股票名称'] = df_htjx['股票名称']
    new_table.loc[:, '委托数量'] = df_htjx['交易股数'].agg(lambda x: int(x))
    new_table.loc[:, '证券市场'] = df_htjx['股票代码'].agg(lambda x: 2 if int(x) < 600000 else 1)
    new_table.loc[:, '相对权重'] = 1
    new_table.loc[:, '绝对权重(导入后自动计算，可不填)'] = 0
    new_table.loc[:, '委托方式'] = df_htjx['交易方向'].astype(str).agg(lambda x: 10 if x == '买入' else 20)
    new_table = new_table.set_index('股票代码')
    new_table.to_csv(path_out,encoding='gbk')

def transform_trade_data(path=DEFAULT_PATH2, path_out=DEFAULT_OUT2):
    try:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}).dropna(how='all')
    except:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}, encoding='gbk').dropna(how='all')

    df_data_all.loc[:,'交易股数'] = df_data_all['交易股数'].astype(str)
    df = df_data_all[df_data_all['交易股数'].str.match('[0-9]')]
    df.loc[:,'交易股数'], df.loc[:,'实时价格']= df['交易股数'].astype(float),df['实时价格'].astype(float)
    df.loc[:, '金额'] = df['交易股数'] * df['实时价格']
    series_money = df.groupby(['账户名称', '交易方向'])['金额'].sum()
    ic(series_money)
    # df_data_all.to_csv(path_out)

def check_buy(path1=FL_PATH, path2=GW_path, path3=GUO_REN):
    # 读取放量上影线的策略名以及股票代码
    f = open(path1)
    data_fl = pd.read_csv(f)
    dk_fl = {k: list(v['股票代码'].values) for k, v in data_fl.groupby(['策略名称'])}
    ic(dk_fl)

    # 读取网址
    f = open(GUO_REN)
    data_gr = pd.read_csv(f)
    d_href = {k: data_gr.query(f'策略=="{k}"')['网址'].values[0] for k in dk_fl.keys()}

    # 检查股票是否在果仁网里面
    data_buy = pd.DataFrame(columns=data_fl.columns)
    for k, v in d_href.items():
        ic(v)
        stocks = get_strategy_stock(v)
        ic(stocks)
        if dk_fl[k][0].strip() in stocks:
            data_buy.append(dk_fl.query(f'策略=="{k}"'))
    ic(data_buy)

    # // *[ @ id = "stock-realCmd-grid"] / div / div[3] / div / div[2] / div[2] / spanname
    # //*[@id="stock-realCmd-grid"]/div/div[3]/div/div[42]/div[2]/spanname
    # //*[@id="stock-realCmd-grid"]/div/div[3]/div/div[4]/div[2]
def write_unique_stock(path=DEFAULT_PATH2):
    try:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}).dropna(how='all')
    except:
        df_data_all = pd.read_csv(open(path, 'rb'), dtype={'日期': str, '股票代码': str}, encoding='gbk').dropna(how='all')

    df = df_data_all[~(df_data_all['备注'].isnull())]
    df.to_csv('异常股票备注.csv', header=False, encoding='gbk', index=False,mode='a')
    print(df)

def modify_code(code):
    return (6-len(code)) * '0' + str(code)

def get_stock_name(data,code):
    data = data[data['股票代码']==code]
    print('查询所得的股票名称:',data)
    if not data.shape[0]:
        return data['股票代码']
    return None

def modify_responsity(path1=os.path.join(DIR_NAME,'acctcheck\本地持仓与账户持仓不符股票列表.csv'),path2=os.path.join('./acctCheck','持仓_20210827.csv')):
    time =datetime.datetime.now().strftime('%Y%m%d')
    data,check = pd.read_csv(open(path2,'rb')),pd.read_csv(open(path1,'rb'))
    print(data.tail())
    check.loc[:, '股票代码'] = check['股票代码'].astype(str)
    # check.loc[:,'股票代码'] = check['股票代码'].apply(modify_code)
    print(check)
    for index,row in check.iterrows():
        if not row['股票代码'].startswith('00') and not row['股票代码'].startswith('6'):
            continue
        if pd.isnull(row['数量']) and ~pd.isnull(row['实际数量']):
            tmp = pd.Series({'日期':time,'账户名称':row['账户'],'股票代码':row['股票代码'],'股票名称':get_stock_name(data,int(row['股票代码'])),'数量':row['实际数量']})
            print('tmp',tmp)
            data = data.append(tmp,ignore_index=True)
            # print(data.tail())

def check():
    data = pd.read_csv(open(os.path.join(DIR_NAME,'2021_0824weituo.csv'),'r',encoding='gbk'),usecols=['证券代码','证券名称','操作','成交数量','备注'])
    data = data[(data['备注'] == '已成(买卖)') | (data['备注']=='部撤(买卖)') ]
    strategy_data = pd.read_csv(open(DEFAULT_PATH1,encoding='gbk'))
    strategy_data = strategy_data[strategy_data['账户名称'] == '鸿通精选']
    table = data.merge(strategy_data,how='right',right_on='股票代码',left_on='证券代码')
    table.loc[:,'diff'] = table['成交数量'] - table['交易股数']
    table.drop(['Unnamed: 11','Unnamed: 12'],axis=1,inplace=True)
    table = table.query('diff!=0')
    table.to_csv('diff.csv')
    print(table)

def transform_check_guoren(path):
    def transform_check_loss():
        pass

def transform_moudle():
    transform_moudle_HT()
    transform_moudle_GJ()

if __name__ == '__main__':
    # check_buy()
    # modify_responsity()
    transform_trade_data()

    # transform_moudle_HT(path=DEFAULT_PATH1, path_out=f'交易_{today_time}_鸿通精选.csv')
    # modify_responsity()
