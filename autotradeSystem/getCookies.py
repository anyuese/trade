from selenium import webdriver
import time
import json
import os

dirname = r"C:\Users\fxz.HT-9-DB-SV1\PycharmProjects\guoren"
#填写webdriver的保存目录
driver = webdriver.Chrome(r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')

#记得写完整的url 包括http和https
driver.get('https://guorn.com')

#程序打开网页后20秒内手动登陆账户527
time.sleep(30)

with open(os.path.join(dirname,'cookies.json'),'w') as cookief:
    #将cookies保存为json格式
    cookief.write(json.dumps(driver.get_cookies()))

print(driver.get_cookies())
driver.close()