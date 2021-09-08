
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from jqdatasdk import *
import datetime
from icecream import ic
import os
import matplotlib.pyplot as plt

auth('18274054038','054038')
today_time = datetime.datetime.now().strftime('%Y%m%d')
today_time1 = datetime.datetime.now().strftime('%Y-%m-%d')
delta_day = datetime.timedelta(days=1)
yesterday_time = (datetime.datetime.today()-delta_day).strftime('%Y%m%d')
yesterday_time2 = (datetime.datetime.today()-delta_day).strftime('%Y-%m-%d')
#--coding:utf-8-
PATH = f'持仓_{today_time}.csv'
PATH2 = f'持仓_{yesterday_time}.csv'
OUT_PATH = r'C:\Users\fxz.HT-9-DB-SV1\PycharmProjects\guoren\all'

def read_depository(path=PATH):
    try:
        depository = pd.read_csv(open(path, 'rb'), encoding='gbk',dtype={'股票代码':str})
    except:
        depository = pd.read_csv(open(path, 'rb'), encoding='utf8',dtype={'股票代码':str})
    depository = depository[['股票代码', '股票名称', '数量','策略名称','账户名称']]
    return depository

def modify_code_jq(code):
    code = str(code)
    if len(code) < 6:
        code = (6 - len(code)) * '0' + code
    if code.startswith('6'):
        code = code + '.XSHG'
    else:
        code = code + '.XSHE'
    return code

def get_pct(depository,flag=1):
    depository.dropna(subset=['股票代码'],inplace=True)
    if flag:
        if os.path.exists(f'收益率明细表{today_time}.csv'):
            depository['收益率'] = pd.read_csv(open(f'收益率明细表{today_time}.csv','rb'),dtype={'策略':str,'股票代码':str})['收益率']
            return depository
    codes = depository['股票代码'].tolist()
    pcts = list()
    for code in codes:
        yesterday_close = get_price(modify_code_jq(code),start_date=yesterday_time2,end_date=today_time1,frequency='daily')['close']
        pct = yesterday_close.pct_change().tolist()[-1]
        pcts.append(pct)
    depository['收益率'] = pcts
    depository.to_csv(f'收益率明细表{today_time}.csv')
    return depository

def cal_combo_return(depository,config):
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False
    result = depository.groupby(['策略名称']).agg({'收益率':np.mean}).reset_index()
    result = result.sort_values(by='收益率')
    ax = result.plot(kind='bar',x='策略名称',y='收益率',figsize=(15,12),rot='45')
    fig = ax.get_figure()
    fig.savefig('各策略收益率统计.png')
    plt.title(f'{today_time}各策略收益率统计')
    plt.show()

    result2 = depository.groupby(['策略名称','账户名称']).agg({'收益率':np.mean}).reset_index()
    result2.loc[:,'账户名称_策略名称'] = result2['账户名称'].str.cat(result2['策略名称'].str.strip())
    result2.drop(['账户名称','策略名称'],axis=1)
    result2 = result2.merge(config,on='账户名称_策略名称')
    print(result2)

    result2.loc[:,'权重收益率'] = result2['收益率']*result2['策略权重']
    result2 = result2.groupby(['账户名称']).agg({'权重收益率':np.sum}).reset_index()
    ax = result2.plot(kind='bar', x='账户名称', y='权重收益率', figsize=(15, 12),rot='45')
    fig = ax.get_figure()
    fig.savefig('各账户收益率统计.png')
    plt.title(f'{today_time}各账户收益率统计')
    plt.show()
    print(len(result))

def read_config(PATH='账户策略配置表.xlsx'):
    data = pd.read_excel(PATH)
    data = data.dropna(subset=['账户'])[['账户','策略','策略权重']]
    data.loc[:, '账户名称_策略名称'] = data['账户'].str.cat(data['策略'].tolist())
    print(data['策略'].tolist())
    return data


def update_price(data):
    pass


def read_price(path=os.path.join(OUT_PATH,'价格金额表.csv')):
    pass

def process_static_return(flag):
    print(yesterday_time)
    depository = read_depository(path=PATH2)
    depository = get_pct(depository,flag=flag)
    config = read_config()
    cal_combo_return(depository,config)


if __name__ == '__main__':
    # 0 表示从头开始获得，1表示不重新获得价格数据
    process_static_return(1)



