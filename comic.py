# -*- coding: utf-8 -*-
"""
爬取comic_walker
"""
import json
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
        self.driver = dr.driver
        # 设置一个等待时间
        self.wait = WebDriverWait(driver, 20)
        self.regex_for_comic = re.compile(f"href.*?(?={self.find})")
        self.width = 1412
        self.height = 2000
        self.driver.set_window_size(self.width, self.height)

        self.offset_is_set = False

        self.actions = self.setup_offset()
        self.retry_count = 0

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
        self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "footer")))
        total_page = self.get_total_page()
        self.wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, r"canvas")))
        self.get_xhr()
        print(total_page)
        for i in range(1, total_page - 1):
            if not i == total_page - 2:
                self.wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, r"canvas")))
                if not os.path.exists(str(self.episode)):
                    os.makedirs(str(self.episode))
                self.is_done()
                self.driver.get_screenshot_as_file(f"{self.episode}/{i}.png")
                self.next_page()
            else:
                self.driver.get_screenshot_as_file(f"{self.episode}/{i}.png")
            print(f"第{i}张完成")
        print("ok")

    def is_done(self):
        self.wait.until(ec.presence_of_element_located((By.TAG_NAME, "body")))
        self.wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        self.get_xhr()
        time.sleep(0.1)

    def next_page(self):
        self.actions.click().perform()
        time.sleep(0.5)

    def setup_offset(self):
        if not self.offset_is_set:
            actions = ActionChains(self.driver)
            actions.move_by_offset(self.width * 0.15, self.height * 0.5)
            self.offset_is_set = True
            return actions

    def get_xhr(self):
        # 获取所有的网络请求
        while True:
            logs = self.driver.get_log('performance')
            events = [json.loads(log['message'])['message'] for log in logs]
            network_events = [event['params'] for event in events if event['method'] == 'Network.requestWillBeSent']
            if all('response' in event for event in network_events):
                break

            if self.retry_count < 20:
                self.retry_count = self.retry_count + 1
                time.sleep(0.5)
                self.get_xhr()
            break

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
