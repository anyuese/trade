import pandas as pd
import datetime
from icecream import ic
from update_guoren import *
import numpy as np

today_time = datetime.datetime.now().strftime('%Y%m%d')

def get_responsity(path):
    data = pd.read_csv(path,encoding='gbk')
    print(data)

if __name__ == '__main__':
    get_responsity(path ='³Ö²Ö_20210820.csv')

