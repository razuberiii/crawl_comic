# -*- coding: utf-8 -*-
"""
爬取comic_walker
"""
import base64
import os
import re
import sys
import time

from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

import driver as dr

driver = dr.driver

find = input("漫画名字:")
# 设置一个等待时间
wait = WebDriverWait(driver, 20)
regex_for_comic = re.compile(f"href.*?(?={find})")

JS1 = "return document.querySelector(\"div[data-index='1'] canvas\").toDataURL('image/png');"
JS0 = "return document.querySelector(\"div[data-index='0'] canvas\").toDataURL('image/png');"
JS2 = "return document.querySelector(\"div[data-index='2'] canvas\").toDataURL('image/png');"

offset_is_set = False

driver.set_window_size(626, 1000)


def load_source(episode):
    url = 'https://comic-walker.com/'
    driver.get(url)
    search_box = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                                            '#searchFormHeader .keywordBox')))
    search_box.clear()
    search_box.send_keys(f"{find}")
    search_box.send_keys(Keys.ENTER)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".tileList")))
    tile_list = driver.find_elements(By.CSS_SELECTOR, '.tileList h2')
    link_list = driver.find_elements(By.CSS_SELECTOR, '.tileList a')
    link = ''
    for i in range(0, len(tile_list)):
        if re.search(f"{find}", tile_list[i].text):
            link = link_list[i].get_attribute("href")
            break
    driver.get(link)
    try:
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '.ac-trigger-btn-more'))).click()
    except:
        raise
    book_list = wait.until(
        ec.presence_of_all_elements_located((By.CSS_SELECTOR,
                                             '#backnumberComics .ac-content .container a')))

    click_enabled(0, book_list[int(episode) - 1])


def get_source(episode):
    count = 1
    print(driver.current_url)
    wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, r"canvas")))
    time.sleep(5)
    total_page = get_total_page()
    actions = setup_offset()
    print(total_page)
    for i in range(1, total_page - 1):
        if count == 0:
            js = JS0
            count = 2
        elif count == 1:
            js = JS1
            count = 0
        elif count == 2:
            js = JS2
            count = 1

        print(js, count)

        img_bytes = decode_base64(js, 0)

        next_page(actions)
        download(episode, i, img_bytes)
        print(f"第{episode}话: 图片{i}抓取完成")
    print("抓完了")


def decode_base64(js, retry_times):
    try:
        mg_base64 = driver.execute_script(js).split(',')[1]
        return base64.b64decode(mg_base64)
    except:
        if retry_times > 20:
            print("失败了")
            sys.exit()
        time.sleep(1)
        retry_times += 1
        decode_base64(js, retry_times)


def download(episode, i, img_bytes):
    if not os.path.exists(str(episode)):
        os.makedirs(str(episode))
    with open(fr"{episode}\{i}.png", 'wb') as f:
        f.write(img_bytes)


def next_page(actions):
    # 没什么好办法判断完成，睡1秒把
    time.sleep(1)
    actions.click().perform()


def setup_offset():
    global offset_is_set
    if not offset_is_set:
        actions = ActionChains(driver)
        actions.move_by_offset(626 * 0.15, 500)
        offset_is_set = True
        return actions


def get_total_page():
    return int(re.findall(r"\d / \d.*(?=<)", driver.page_source)[0].split(r"/")[-1])


def click_enabled(retry_count, element):
    if retry_count > 20:
        print("点不了")
        sys.exit()

    if element.is_enabled():
        element.click()
    else:
        time.sleep(0.5)
        retry_count = retry_count + 1
        click_enabled(retry_count, element)


def crawl(episode):
    print("等会")
    load_source(episode)

    get_source(episode)
