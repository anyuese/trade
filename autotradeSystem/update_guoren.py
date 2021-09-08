import os
import time
import json
from icecream import ic
from urllib import request
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
import os
import re

NOT_DONE_QUE = dict()


def write_cookie():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')
    url = "https://guorn.com"
    driver.get(url)
    time.sleep(20)
    # 此时浏览器已经打开，在浏览器中打开网页并登陆
    filename = r"F:\quantitative_trade\cookie.json"
    # 开始写入cookie
    cookies = driver.get_cookies()
    jsonCookies = json.dumps(cookies)
    with open(filename, 'w') as f:
        f.write(jsonCookies)
    driver.close()


def init():
    driver = webdriver.Chrome(r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
    dirname = r"C:\Users\fxz.HT-9-DB-SV1\PycharmProjects\guoren"
    driver.implicitly_wait(30)
    # 记得写完整的url 包括http和https
    driver.get('https://guorn.com')
    # 首先清除由于浏览器打开已有的cookies
    driver.delete_all_cookies()

    # 读取cookie
    with open(os.path.join(dirname, 'cookies.json'), 'r') as cookief:
        # 使用json读取cookies 注意读取的是文件 所以用load而不是loads
        cookieslist = json.load(cookief)

    # 方法1 将expiry类型变为int
    for cookie in cookieslist:
        # 并不是所有cookie都含有expiry 所以要用dict的get方法来获取
        if isinstance(cookie.get('expiry'), float):
            cookie['expiry'] = int(cookie['expiry'])
        driver.add_cookie(cookie)

    return driver


def parser_href(driver, path=2):
    driver.get('https://guorn.com/user/home?page=created')
    driver.implicitly_wait(40)
    try:
        xpath = f'//*[@id="content-cnt"]/div[2]/div[5]/div[3]/div/button[{path}]'
        text = driver.find_element_by_xpath(xpath).text.split('(')
        print(text)
        num, text_ = int(text[1][:-1]), text[0]
        ic(num, text_)
        time.sleep(10)
        driver.find_element_by_xpath(xpath).click()
        ic('已点击')
    except IndexError or Exception as e:
        ic(e)
        return None


    hrefs = dict()
    for i in range(1, num + 1):
        href_xpath = f'//*[@id="content-cnt"]/div[2]/div[5]/div[3]/table[1]/tbody/tr[{i}]/td[1]/a'
        info = driver.find_element_by_xpath(href_xpath)
        href = info.get_attribute('href')
        name = driver.find_element_by_xpath(href_xpath).text.strip()
        hrefs[name] = href
    print(len(hrefs))
    pd.DataFrame({'name': list(hrefs.keys()), 'href': list(hrefs.values())}).to_csv(f'{text_}_hrefs.csv', index=None)
    return driver, hrefs


def modify_2_years(driver, hrefs, year='两', isMut=None):
    driver.implicitly_wait(40)
    num_month = '7'
    num_day = '13'
    if year == '两':
        num_year = '2019'
    elif year == '三':
        num_year = '2018'
    elif year == '半':
        num_year = '2021'
        num_month = '1'
    elif year == '一':
        num_year = '2020'
        num_day = '7'
    # 查看定义 xpath
    ckdy_path = '//*[@id="strategy-cnt"]/div[1]/span[2]'
    # 日期控件
    start_time_path = '//*[@id="time-box"]/div[1]/input'
    # 另存为 xpath
    lcw_path = '//*[@id="stockScreen-top-bar"]/span[2]'
    # 策略名
    give_name_path = '//*[@id="save-as-dialog"]/div/div/div[2]/input'
    # 保存
    store_path = '//*[@id="save-as-dialog"]/div/div/div[3]/button[2]'

    for k, v in hrefs.items():
        try:
            ic(k, v)
            wait = WebDriverWait(driver, 30, 0.5)
            driver.get(v)
            wait.until(lambda diver: driver.find_element_by_xpath(ckdy_path))
            time.sleep(30)

            driver.find_element_by_xpath(ckdy_path).click()
            wait.until(lambda diver: driver.find_element_by_xpath(start_time_path))
            time.sleep(5)

            start_time = driver.find_element_by_xpath(start_time_path)
            start_time.click()

            wait.until(lambda diver: driver.find_element_by_xpath(lcw_path))
            js_value = f'document.querySelector("#time-box > div.input-group.date.form_date_start > input").value="{num_year}/{num_month}/{num_day}"'  # js添加时间
            driver.execute_script(js_value)
            time.sleep(4)

            driver.find_element_by_xpath(lcw_path).click()
            name = k + f"_近{year}年{isMut}"
            time.sleep(2)
            wait.until(lambda diver: driver.find_element_by_xpath(give_name_path))
            give_name = driver.find_element_by_xpath(give_name_path)
            give_name.click()
            time.sleep(2)
            give_name.send_keys(name)
            time.sleep(2)
            wait.until(lambda diver: driver.find_element_by_xpath(store_path))
            store = driver.find_element_by_xpath(store_path)
            store.click()

            # //*[@id="common-warn-dialog"]/div/div/div/div[3]/button[1]  知道啦
            # //*[@id="strategy-saved-info"]/button
            ok_p, err_p = '//*[@id="strategy-saved-info"]/button', '//*[@id="common-warn-dialog"]/div/div/div/div[3]/button[1]'
            wait.until(lambda diver: driver.find_element_by_xpath(ok_p) or driver.find_element_by_xpath(err_p))
            time.sleep(30)
        except Exception as e:
            if not os.path.exists(f'error{year}.csv'):
                with open(f'error{year}.csv','w') as f:
                    f.write('name,href,\n')
            pd.Series({k: v}).to_csv(f'error{year}.csv', mode='a')
            NOT_DONE_QUE[k] = [v]
            ic(e)
            ic('error')
            continue

def compare():
    pass


def get_strategy_stock(name):
    try:
        config = pd.read_csv(open('果仁网址配置表.csv', 'rb'))
    except:
        config = pd.read_csv(open('果仁网址配置表.csv', 'r', encoding='gbk'))
    href = config.query('策略==@name')['网址']
    driver = init()
    driver.get(href)
    time.sleep(15)
    # 遍历获取
    stocks = list()
    for i in range(1, 31):
        try:
            x_path = f'//*[@id="stock-realCmd-grid"]/div/div[3]/div/div[{2 * i}]/div[2]/spanname'
            text = driver.find_element_by_xpath(x_path).text.strip()
            stocks.append(text)
        except:
            break
    return stocks

def process_modify_guoren_name():
    driver = init()
    dict_ = dict()
    dict_all = pd.read_csv('task.csv')
    for k, v in dict_all.iterrows():
        ic(v['name'].strip(), v['href'])
        dict_[v['name'].strip()] = v['href']
    modify_2_years(driver, dict_, year='三', isMut='_')
    modify_2_years(driver, dict_, year='半', isMut='_')
    modify_2_years(driver, dict_, year='两', isMut='_')
    modify_2_years(driver, dict_, year='一', isMut='_')


if __name__ == '__main__':
    # write_cookie()
    driver = init()
    parser_href(driver, path=8)
    # driver, href2 =parser_href(driver, path=2)
    # pd.set_option('display.max_columns', None)
    # href1.to_csv('chaosuan_hrefs.csv')
    # dict_ = dict()
    #
    # # dict1 = pd.read_csv('chaosuan_hrefs.csv')
    # # dict2 = pd.read_csv('HTclfl_hrefs.csv')
    # # dict_all = pd.concat([dict1, dict2])
    # dict_all = pd.read_csv(open('task.csv','rb'))
    # for k, v in dict_all.iterrows():
    #     ic(v['name'].strip(), v['href'])
    #     dict_[v['name'].strip()] = v['href']
    # # #
    # modify_2_years(driver, dict_, year='半',isMut='')
    # modify_2_years(driver, dict_, year='一', isMut='')
    # modify_2_years(driver, dict_, year='两', isMut='')
    # modify_2_years(driver, dict_, year='三', isMut='')


