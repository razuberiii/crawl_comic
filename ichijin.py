import json
import os
import re
import time

from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

import driver as dr


class Ichijin:
    def __init__(self, name, episode):
        self.name = name
        self.episode = episode
        self.driver = dr.driver
        # 设置一个等待时间
        self.wait = WebDriverWait(self.driver, 20)
        self.width = 638
        self.height = 907
        self.driver.set_window_size(self.width, self.height)
        self.url = "https://ichijin-plus.com/"
        self.offset_is_set = False
        self.actions = self.setup_offset()
        self.retry_count = 0

    def load_source(self):
        self.driver.get(self.url)
        self.wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR,
                                                    'img[alt="作品を探す"]'))).click()

        search_box = self.wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "input[type='search']")))
        search_box.clear()
        search_box.send_keys(f"{self.name}")

        search_box.send_keys(Keys.ENTER)
        self.wait.until(
            ec.presence_of_element_located((By.XPATH, fr"//title[contains(text(), '{self.name}')]")))
        self.driver.execute_script("document.querySelector('ul li a').click()")

        manga_list = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "section ul")))

        manga_list.find_elements(By.CSS_SELECTOR, "li")[int(self.episode) - 1].click()

    def get_source(self):
        self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "footer")))
        total_page = self.get_total_page()
        self.wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, r"canvas")))
        self.get_xhr()
        time.sleep(2)
        for i in range(1, total_page - 1):
            if not i == total_page - 2:
                self.wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, r"canvas")))
                if not os.path.exists(str(self.episode)):
                    os.makedirs(str(self.episode))
                self.is_done()

                self.driver.get_screenshot_as_file(f"{self.episode}/{i}.png")
                time.sleep(0.3)
                self.next_page()
            else:
                self.driver.get_screenshot_as_file(f"{self.episode}/{i}.png")
            print(f"第{i}张完成")
        print("ok")

    def setup_offset(self):
        if not self.offset_is_set:
            actions = ActionChains(self.driver)
            actions.move_by_offset(self.width * 0.15, self.height * 0.5)
            self.offset_is_set = True
            return actions

    def next_page(self):
        self.actions.click().perform()
        time.sleep(0.4)

    def is_done(self):
        self.wait.until(ec.presence_of_element_located((By.TAG_NAME, "body")))
        self.wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(0.1)

    def get_total_page(self):
        return int(re.findall(r"\d / \d.*?(?=<)", self.driver.page_source)[0].split(r"/")[-1])

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

    def crawl(self):
        print("等会")
        self.load_source()

        self.get_source()
