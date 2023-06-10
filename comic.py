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


class Comic:
    def __init__(self, name, episode):
        self.episode = episode
        self.find = name
        # 设置一个等待时间
        self.wait = WebDriverWait(driver, 20)
        self.regex_for_comic = re.compile(f"href.*?(?={self.find})")

        self.JS1 = "return document.querySelector(\"div[data-index='1'] canvas\").toDataURL('image/png');"
        self.JS0 = "return document.querySelector(\"div[data-index='0'] canvas\").toDataURL('image/png');"
        self.JS2 = "return document.querySelector(\"div[data-index='2'] canvas\").toDataURL('image/png');"

        self.offset_is_set = False

        driver.set_window_size(626, 1000)

    def load_source(self, episode):
        url = 'https://comic-walker.com/'
        driver.get(url)
        search_box = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                                                     '#searchFormHeader .keywordBox')))
        search_box.clear()
        search_box.send_keys(f"{self.find}")
        search_box.send_keys(Keys.ENTER)
        self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".tileList")))
        tile_list = driver.find_elements(By.CSS_SELECTOR, '.tileList h2')
        link_list = driver.find_elements(By.CSS_SELECTOR, '.tileList a')
        link = ''
        for i in range(0, len(tile_list)):
            if re.search(f"{self.find}", tile_list[i].text):
                link = link_list[i].get_attribute("href")
                break
        driver.get(link)
        try:
            self.wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '.ac-trigger-btn-more'))).click()
        except:
            raise
        book_list = self.wait.until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                 '#backnumberComics .ac-content .container a')))

        self.click_enabled(0, book_list[int(episode) - 1])

    def get_source(self, episode):
        count = 1
        print(driver.current_url)
        self.wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, r"canvas")))
        time.sleep(5)
        total_page = self.get_total_page()
        actions = self.setup_offset()
        print(total_page)
        for i in range(1, total_page - 1):
            if count == 0:
                js = self.JS0
                count = 2
            elif count == 1:
                js = self.JS1
                count = 0
            elif count == 2:
                js = self.JS2
                count = 1

            print(js, count)

            img_bytes = self.decode_base64(js, 0)
            self.wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, r"body")))
            self.next_page(actions)

            self.download(episode, i, img_bytes)
            print(f"第{episode}话: 图片{i}抓取完成")
        print("抓完了")

    def decode_base64(self, js, retry_times):
        try:
            mg_base64 = driver.execute_script(js).split(',')[1]
            return base64.b64decode(mg_base64)
        except:
            if retry_times > 20:
                print("失败了")
                sys.exit()
            time.sleep(1)
            retry_times += 1
            self.decode_base64(js, retry_times)

    def download(self, episode, i, img_bytes):
        if not os.path.exists(str(episode)):
            os.makedirs(str(episode))
        with open(fr"{episode}\{i}.png", 'wb') as f:
            f.write(img_bytes)

    def next_page(self, actions):
        # 没什么好办法判断完成，睡1秒把
        # 必须等图片加载完，但是我不知道有什么办法判断图片是否加载完……，网络卡就多抓几次，或者时间调大点
        time.sleep(1)
        actions.click().perform()

    def setup_offset(self):
        if not self.offset_is_set:
            actions = ActionChains(driver)
            actions.move_by_offset(626 * 0.15, 500)
            self.offset_is_set = True
            return actions

    def get_total_page(self):
        return int(re.findall(r"\d / \d.*?(?=<)", driver.page_source)[0].split(r"/")[-1])

    def click_enabled(self, retry_count, element):
        if retry_count > 20:
            print("点不了")
            sys.exit()

        if element.is_enabled():
            element.click()
        else:
            time.sleep(0.5)
            retry_count = retry_count + 1
            self.click_enabled(retry_count, element)

    def crawl(self):
        print("等会")
        self.load_source(self.episode)

        self.get_source(self.episode)
