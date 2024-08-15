import json
import requests
import math
import random
import pandas as pd
from Agent import UserAgent
from api import WxApi
import os
import time
from datetime import datetime

class WeChatSpider:
    def __init__(self, key, token, fakeid):
        self.ua = UserAgent()
        self.key = key
        self.token = token
        self.fakeid = fakeid
        self.wxapi = WxApi(key)
        self.content_excel = []
        self.cookie_path = 'cookie.txt'
        self.data_json_path = 'data.json'
        self.url = self.ua.get_url()
        self.random_agent = self.ua.get_random_agent()
        self.data_json = None
        self.cookie = None
        self.score = ''
        self.data_print = None

    def load_cookies(self):
        with open(self.cookie_path, encoding='utf-8') as f:
            self.cookie = f.read().strip()

    def load_data_json(self):
        with open(self.data_json_path, 'r', encoding='utf-8') as f:
            self.data_json = json.load(f)
        self.data_json['token'] = self.token
        self.data_json['fakeid'] = self.fakeid

    def fetch_content(self, start_time=None, end_time=None):
        self.load_cookies()
        self.load_data_json()
        headers = {
            "Cookie": self.cookie,
            'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Mobile Safari/537.36"
        }
        content = requests.get(self.url, headers=headers, params=self.data_json).json()
        sum_count = int(content["app_msg_cnt"])
        page = int(math.ceil(sum_count / 5))
        print('page:', page)
        url_tile_list = []

        # 将 start_time 和 end_time 从字符串格式转换为 datetime 对象
        if start_time:
            start_time = datetime.strptime(start_time, "%Y-%m-%d")
        if end_time:
            end_time = datetime.strptime(end_time, "%Y-%m-%d")

        for i in range(page):
            self.data_json['begin'] = i * 5
            random_agent = self.ua.get_random_agent()
            header = {
                'cookie': self.cookie,
                'User-Agent': random_agent
            }
            content = requests.get(self.url, headers=header, params=self.data_json).json()
            for result in content['app_msg_list']:
                url = result['link']
                title = result['title']
                create_time = datetime.fromtimestamp(result["create_time"])  # 将时间戳转换为 datetime 对象
                create_time_str = create_time.strftime("%Y-%m-%d")  # 转换为字符串以用于显示

                # 根据时间范围筛选
                if start_time and end_time:
                    if start_time <= create_time <= end_time:
                        url_tile_list.append((url, title, create_time_str))
                else:
                    url_tile_list.append((url, title, create_time_str))

            if i % 10 == 0:
                time_sleep = random.randint(60, 100)
                print('sleep time:', time_sleep)
                time.sleep(time_sleep)
            else:
                time_sleep = random.randint(15, 30)
                print('sleep time:', time_sleep)
                time.sleep(time_sleep)

        for url, title, create_time in url_tile_list:
            self.wxapi.set_url(url)
            self.wxapi.data_json()
            item = {
                '公众号名字': self.wxapi.nickname,
                '文章标题': title,
                '文章发布时间': create_time,
                '阅读数': self.wxapi.read_num,
                '点赞数': self.wxapi.like_num,
                '在看数': self.wxapi.look_num,
                '分享数': self.wxapi.share_num,
                '收藏数': self.wxapi.collect_num,
                '留言数': self.wxapi.comment_num,
                'URL': url
            }
            self.content_excel.append(item)
        return self.content_excel

    def save_to_csv(self,root_path):
        header_excel = ['公众号名字', '文章标题', '文章发布时间', '阅读数',
                        '点赞数', '在看数', '分享数', '收藏数', '留言数']
        df = pd.DataFrame(self.content_excel, columns=header_excel)
        nickname = self.content_excel[0]['公众号名字']
        abs_path = os.path.join(root_path, nickname)
        df.to_csv(f"{abs_path}.csv", index=False, encoding='utf-8-sig')
        print('Save Successful !')




