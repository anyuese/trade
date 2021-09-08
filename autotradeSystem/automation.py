import datetime
import threading
import pickle
import time
#import tushare as ts
import pywinauto
import pywinauto.clipboard
from pywinauto.keyboard import send_keys
import pywinauto.application

import sys
from pywinauto.controls.win32_controls import ComboBoxWrapper
from pywinauto.findwindows import find_element,find_elements
import pandas as pd
import sys


def find_THX_handle(name='THX'):
    if name == 'THX':
        title = '网上股票交易系统5.0'
        class_name = 'Afx:400000:b:10003:6:108b3'
    if name == 'ZS':
        title = '招商证券V7.08'
        class_name = 'TdxW_MainFrame_Class'
    print('--------------开始寻找客户端窗口------------------')
    handle = find_element(title_re=title,class_name=class_name)
    print('客户端窗口句柄为：',handle.handle)
    process = handle.process_id
    return handle.handle,process

def connect_mult(handle=None,name=None):
    print('---------------开始客户端----------------------')
    app = pywinauto.application.Application(backend='uia')
    app.connect(handle=handle)
    print('连接成功')
    # app.top_window()
    print(app)

    if name == 'ZS':
        top_window = app['招商证券V7.08 - [分析图表-中国联通]']
    if name == 'THX':
        top_window = app['网上股票交易系统5.0']
    # top_window.print_control_identifiers()
    top_window.wait("exists enabled  ready")
    return app,top_window

def init(name):
    handle,process = find_THX_handle(name=name)
    app,top_window = connect_mult(handle=handle,name=name)
    return app,top_window,handle,process

def THX_change_user(top_window,handle=0x10B72,user_name='中天国富-鸿**号'):
    user_l = ['中天国富-鸿**号', '国金证券-鸿**号', '中信证券-牛*华']
    cb_button = ComboBoxWrapper(handle)
    cb_button.select(user_name)
    # print(cb_button.item_texts())

def THX_buy_sell(app,top_window,process,status='卖出',stock='600519',num=None):
    if status == '买入':
        app.top_window().type_keys('{F1}')
    if status == '卖出':
        app.top_window().type_keys('{F2}')
    if status == '撤单':
        app.top_window().type_keys('{F3}')
    stock_c = top_window.child_window(auto_id="1032", control_type="Edit")
    # stock_c.top_window()
    print(stock)
    stock_c.type_keys(stock)
    # stock_can_buy_num = top_window.child_window(auto_id='1018',control_type='Image')
    # print(stock_can_buy_num.window_text())
    # 输入数量
    stock_status_num = top_window.child_window(auto_id="1034", control_type="Edit")
    stock_status_num.type_keys(num)
    # 买入提交
    stock_button1 = top_window.child_window(title=status,auto_id="1006", control_type="Button")
    stock_button1.click()
    # 确认提交
    stock_button2 = top_window.child_window(title="是(Y)", auto_id="6", control_type="Button")
    stock_button2.click()
    # 检查弹出的窗口
    # popup_window = pywinauto.findwindows.find_window(auto_id="1004", control_type="Image")
    # print(popup_window._ctrl_identifiers())
    # popup_window.print_control_identifiers()
    # 提交成功/失败
    stock_button3 = top_window.child_window(title='确定',auto_id='2',control_type="Button")
    stock_button3.click()
    # 检查失败or成功

def ZS_change_user(handle=0xA161A,name='量化优选'):
    print('------------------开始切换账户--------------',name)
    user_l = ['钻石卡 0380327515 普通 湖南鸿通投资  长沙芙蓉中路证券营业部', '钻石卡 0380328755 普通 鸿通量化稳健  长沙芙蓉中路证券营业部']
    if name== '量化优选':
        name = user_l[0]
    if name == '量化稳健':
        name = user_l[1]
    cb_button = ComboBoxWrapper(handle)
    cb_button.select(name)

def read_data(path=u'交易_20210811.csv'):
    try:
        data = pd.read_csv(open(path, 'rb'),encoding='gbk')
    except:
        data = pd.read_csv(open(path, 'rb'), encoding='utf8')
    data_group = data.groupby(['账户名称'])
    table_result = pd.DataFrame()
    for k,table in data_group:
        if k in ['鸿通2号','中信专户','多因子']:
            table = table[['账户名称','股票代码','交易方向','交易股数']]
            table_result = pd.concat([table_result,table])
    return table_result

def modify_code(code):
    code = str(code)
    if len(code)<6:
        code = (6-len(code))*'0'+code
    return code

def THX_process_buy_sell():
    print('正在初始化-------------------')
    app,top_window,handle,process = init(name='THX')
    data = read_data()
    print(data)
    for index, rows in data.iterrows():
        if rows['账户名称'] == '中信专户':
            THX_change_user(top_window=top_window,user_name='中信证券-牛*华')
        elif rows['账户名称'] == '鸿通2号':
            THX_change_user(top_window=top_window,user_name='国金证券-鸿**号')
        elif rows['账户名称'] == '多因子':
            THX_change_user(top_window=top_window, user_name='中天国富-鸿**号')
        stock_code = modify_code(rows['股票代码'])
        signal = rows['交易方向']
        num = rows['交易股数']
        print('正在操作:',rows['账户名称'],stock_code,signal,num)
        print('开始操作-----------------------')
        THX_buy_sell(app,top_window,process,status=signal,stock=stock_code,num=num)

def test_THX_buy_sell():
    # class_name = '#32770'
    # windows = pywinauto.findwindows.find_elements(class_name=class_name)
    # print(windows)
    # 获取行情数据
    # panel_handle = pywinauto.findwindows.find_window(process=process,class_name='#32770')
    # print(panel_handle,hex(panel_handle))
    # panel = app.window_(handle=panel_handle)
    app, top_window, handle, process = init(name='THX')
    THX_buy_sell(app, top_window, process,num=1000)
    # test THX_buy_sell
def test_huatai():
    pass

def test_ZS():
    handle, process = find_THX_handle(name='ZS')
    connect_mult(handle=handle)
    # ZS_change_user()

if __name__ == '__main__':
    THX_process_buy_sell()











    # THX_change_user(top_window)



