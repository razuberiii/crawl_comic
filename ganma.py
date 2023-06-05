# -*- coding: utf-8 -*-
import json
import os
import re
import sys
import time

import requests
# 解析
from pyquery import PyQuery
from selenium.webdriver.common.by import By
# 一些条件判断的常见，如是否alert等
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

import driver as dr

find = "ウルフちゃんは澄ましたい".encode('utf-8').decode('utf-8')
regex_for_ganma = re.compile(f"href.*?(?={find})")
regex_first_comma = re.compile(r"(?<=\")/.*?(?=\")")
pattern_search_url = r'/\d.jpg\?'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
}
driver = dr.driver
# 设置一个等待时间
wait = WebDriverWait(driver, 10)


def download(episode, i, source_url):
    img = requests.get(source_url, headers=headers)
    with open(fr"{episode}\{i}.jpg", 'wb') as f:
        f.write(img.content)


def load_source_total():
    url = 'https://ganma.jp'
    driver.get(url + '/list/release')

    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                               '.view-list.ng-scope')))

    html = driver.page_source.replace("\n", "").replace("\r", "")

    href = regex_for_ganma.findall(html)[0].split("href")

    href = regex_first_comma.findall(href[- 1])[0]

    driver.get(url + href)

    wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".detail-action-all.ng-scope"))).click()


def get_xhr(retry_count):
    # 获取所有的网络请求
    logs = driver.get_log('performance')
    for log in logs:
        message = json.loads(log['message'])['message']

        if message['method'] == 'Network.requestWillBeSent':
            if "/1.jpg" in message['params']['request']['url']:
                return message['params']['request']['url']

    if retry_count < 20:
        retry_count = retry_count + 1
        time.sleep(0.5)
        get_xhr(retry_count)


def get_source(episode):
    if not os.path.exists(str(episode)):
        os.makedirs(str(episode))
    current_url = driver.current_url
    # 等待
    time.sleep(0.5)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                               ".manga-section-btm.manga-section.ng-scope.inactive .ng-binding")))
    html = driver.page_source
    doc = PyQuery(html)
    if "このマンガはアプリ限定公開です" in html:
        print("このマンガはアプリ限定公開です")
        sys.exit()

    item = list(doc(".manga-section-btm.manga-section.ng-scope.inactive .ng-binding").items())[0]
    totalpage = int(item.text().split('/ ')[-1])
    url = get_xhr(0)
    for i in range(1, totalpage - 2):
        source_url = re.split(pattern_search_url, url)[0] + f'/{i}' + '.jpg?' + \
                     re.split(pattern_search_url, url)[-1].split('&')[0] + "&" + \
                     re.split(pattern_search_url, url)[-1].split('&')[1] + "&" + \
                     re.split(pattern_search_url, url)[-1].split('&')[2]
        download(episode, i, source_url)
        print(f"第{episode}话:图片{i}完成")
    print(re.split(r'[^/]+(?!.*/)', current_url)[0] + str(totalpage - 2))
    print(f"第{episode}话完成！")
    driver.get(re.split(r'[^/]+(?!.*/)', current_url)[0] + str(totalpage - 2))

    next_page = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '.exchange-next-story-btn button')))
    next_page.click()
    episode = episode + 1

    if episode == 6:
        print("五话抓完了")
        return
    get_source(episode)


def crwal_total():
    try:
        load_source_total()
    except Exception as ex:
        print(ex)
        print("没找着")
        sys.exit()

    get_source(1)
