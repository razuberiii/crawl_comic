# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

options = webdriver.ChromeOptions()
# 保持逻辑结束后不退出浏览器
options.add_experimental_option('detach', True)
# 启用浏览器log
options.add_argument('--enable-logging')
options.add_argument('--v=1')
# 隐藏浏览器
options.add_argument('--headless')

caps = DesiredCapabilities.CHROME
caps["goog:loggingPrefs"] = {"performance": "ALL"}



# 获取一个浏览器对象
driver = webdriver.Chrome(desired_capabilities=caps,
                          options=options)
# 隐式等待1s
driver.implicitly_wait(1)
