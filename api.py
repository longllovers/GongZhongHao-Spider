import requests

class WxApi:
    def __init__(self, key):
        self.wx_url = 'http://111.67.193.171:8081/weixin/getrk'
        self.key = key
        self.url = None
        self.response = None
        self.socre = ''
        # 初始化存储各项数据的属性
        self.nickname = ''
        self.pub_time = ''
        self.read_num = 0
        self.like_num = 0
        self.look_num = 0
        self.share_num = 0
        self.collect_num = 0
        self.comment_num = 0

    def set_url(self, url):
        self.url = url

    def data_json(self):
        data = {
            'url': self.url,
            'key': self.key
        }
        self.response = requests.get(self.wx_url, params=data).json()
        print("API Response:", self.response)  # 打印完整响应
        if 'data' in self.response:
            self.socre = self.response['msg']
            # 将获取到的数据保存到类的属性中
            self.nickname = self.response['data'].get('nickname', '')
            self.pub_time = self.response['data'].get('pub_time', '')
            self.read_num = self.response['data'].get('read_num', 0)
            self.like_num = self.response['data'].get('like_num', 0)
            self.look_num = self.response['data'].get('look_num', 0)
            self.share_num = self.response['data'].get('share_num', 0)
            self.collect_num = self.response['data'].get('collect_num', 0)
            self.comment_num = self.response['data'].get('comment_num', 0)
            self.print()
        else:
            print("Warning: 'data' not found in response.")

    def print(self):
        if self.response and 'data' in self.response:
            print(
                f"url: {self.url}, 公众号名称: {self.nickname}, 文章的发布时间: {self.pub_time}, "
                f"阅读数: {self.read_num}, 点赞数: {self.like_num}, 在看数: {self.look_num}, "
                f"分享数: {self.share_num}, 收藏数: {self.collect_num}, 留言数: {self.comment_num}")
        else:
            print("No data available or 'data' key missing in the response.")

    def get_score(self):
        url = 'http://mp.weixin.qq.com/s?__biz=MzU2MDc5NzI1MA==&mid=2247498850&idx=1&sn=c48df2faaaaee23e9dc7bf3027c0c634&chksm=fc003f4fcb77b659d6327fd5a0e8b30d8705268b5f8c8ef1caefde50bbec67142e26a9a1dfce#rd'
        data = {
            'url': url,
            'key': self.key
        }
        self.socre = self.response = requests.get(self.wx_url, params=data).json()['msg']
        return self.socre

