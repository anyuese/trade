import pandas as pd
import time
import datetime
import os
import warnings
warnings.filterwarnings("ignore")

import jqdatasdk as jq
jq.auth("17086394096","zhu1988520")

# jq.auth("18274054038","054038")


dirname = r"C:\Users\fxz.HT-9-DB-SV1\PycharmProjects\guoren"
days = jq.get_trade_days(end_date=datetime.datetime.now(),count=2)
today = days[-1].strftime('%Y%m%d')
pre_dt = days[0].strftime('%Y%m%d')

# ============获取本地信息==================
fp = os.path.join(dirname,'持仓_{}.csv'.format(pre_dt))

try:
    df_pos = pd.read_csv(open(fp,'rb'),dtype={'日期':str,'股票代码':str}).dropna(how='all')
except:
    df_pos = pd.read_csv(open(fp, 'rb'), encoding='gbk',dtype={'日期': str, '股票代码': str}).dropna(how='all')
df_pos = df_pos[~df_pos['股票代码'].isnull()]
df_pos['股票代码'] = ["{:0>6d}".format(int(x)) for x in df_pos['股票代码'].tolist()]

# ============行情数据===========================
holdings = df_pos['股票代码'].unique()
holdings = [jq.normalize_code(x) for x in holdings if x[0] in ['0','6','3']]
prices = jq.get_price(holdings,end_date=datetime.datetime.now(),count=100)
# series
close = prices['close'].iloc[-1]
hi = prices['high'].iloc[-1]
lo = prices['low'].iloc[-1]
open = prices['open'].iloc[-1]
# dataframe
vol = prices['volume']


# ===========计算放量上影线================================
#  上影线：(最高-收盘)/(最高-最低)
#  放量： 当日成交量/20日平均成交量
#  上影线*放量 > 3,  表明放量至少大于三倍，如果上影线为0.5，则需要放量6倍
syx = (hi-close)/(hi-lo)
fangda = vol.iloc[-1]/vol.iloc[-20:].mean()
res = syx*fangda
res2 = res[res>3]


final_stks = [x[:6] for x in res2.index.tolist()]

# 将放量上影线结果写入csv中
df_fl = df_pos[df_pos['股票代码'].isin(final_stks)]
df_fl.loc[:,'日期'] = datetime.datetime.now().strftime('%Y%m%d')
df_fl.to_csv('放量上影线.csv',mode='a',index=False,encoding='gbk',header=False)

print("=======今日放量上影线股票===============")
print(df_pos[df_pos['股票代码'].isin(final_stks)])


# ============计算换手率===========================================
q = jq.query(jq.valuation.turnover_ratio).filter(jq.valuation.code.in_(holdings))
turnover = jq.get_fundamentals_continuously(q,end_date=datetime.datetime.now(),count=20)['turnover_ratio']

# 五日换手总和
tn_sum = turnover.iloc[-5:].sum()/100
# 五日换手大于50%股票
tn_stks = tn_sum[tn_sum>0.5].index.tolist()

# 100天内高点出现在最近5天
max5 = prices['close'].iloc[-5:].max()
max100 = prices['close'].iloc[-100:].max()
match_items = (max5==max100)
match_stks = match_items[match_items].index.tolist()
final_match  = list(set(tn_stks) & set(match_stks))
final_match = [x[:6] for x in final_match]

# 将高换手写入csv
df_gh = df_pos[df_pos['股票代码'].isin(final_match)]
df_gh.loc[:,'日期'] = datetime.datetime.now().strftime('%Y%m%d')
df_gh.to_csv('高换手股票.csv',mode='a',index=False,header=False,encoding='gbk')

print("=======高换手股票===============")
print(df_pos[df_pos['股票代码'].isin(final_match)])
print("===================================")


# tn_sum = turnover.iloc[-10:].sum()/100
# tn_stks = tn_sum.sort_values().dropna().tail(5).index.tolist()
# tn_stks = [x[:6] for x in tn_stks]
# print("=======10天总换手前三===============")
# print(df_pos[df_pos['股票代码'].isin(tn_stks)])
# print("===================================")

# =======查重=======
# g = df_pos.groupby(['账户名称','策略名称','股票代码'])
# g['股票名称'].count().sort_values(ascending=False)

