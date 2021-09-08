#coding=gbk
import pandas as pd
import datetime
from icecream import ic

today_time = datetime.datetime.now().strftime('%Y%m%d')
delta_day = datetime.timedelta(days=1)
yesterday_time = (datetime.datetime.today()-delta_day).strftime('%Y%m%d')

PATH1 = f'�ֲ�_{today_time}.csv'
PATH2 = '��ѡ��.csv'
PATH3 = f'����_{today_time}.csv'
PATH4 = f'�ֲ�_{yesterday_time}.csv'

def read_resposity(path=PATH4):
    print('------�˶�PATH:',path)
    try:
        resposity = pd.read_csv(open(path, 'rb'), encoding='gbk')
    except:
        resposity = pd.read_csv(open(path, 'rb'), encoding='utf8')
    resposity = resposity[['��Ʊ����', '��Ʊ����', '����','��������','�˻�����']]
    return resposity

def get_forbidden(path=PATH2):
    forbidden = pd.read_csv(open(path,'r',encoding='gbk'))
    return forbidden['��Ʊ����'].tolist()

def process_check(forbidden,resposity):
    out_put = pd.DataFrame()
    print('----------------���ѡ���йؼ�¼-------------')
    out_put =  resposity[resposity['��Ʊ����'].isin(forbidden)]
    ic(out_put)

def get_trade_data(path=PATH3):
    print('--------�˶��ļ�',path)
    try:
        trade_data = pd.read_csv(open(path,'rb'))
    except:
        trade_data = pd.read_csv(open(path, 'r',encoding='gbk'))
    return trade_data

if __name__ == '__main__':
    process_check(get_forbidden(),get_trade_data())

