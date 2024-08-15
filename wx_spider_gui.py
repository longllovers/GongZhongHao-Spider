import wx
import threading
import os
from wx_spider import WeChatSpider
from api import WxApi
import re


class SpiderApp(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(500, 360),
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetIcon(wx.Icon('wechat.ico'))
        self.spider = None

        self.panel = wx.Panel(self)
        sizer = wx.GridBagSizer(5, 5)

        # 创建输入key的标签和文本框
        self.key_label = wx.StaticText(self.panel, label='{:^10}'.format('API Key'))
        self.key_text = wx.TextCtrl(self.panel)
        sizer.Add(self.key_label, pos=(0, 0), flag=wx.ALL, border=5)
        sizer.Add(self.key_text, pos=(0, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # 创建一个积分标签和文本框
        self.score_label = wx.StaticText(self.panel, label='积分')
        self.score_text = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        sizer.Add(self.score_label, pos=(0, 2), flag=wx.ALL, border=10)
        sizer.Add(self.score_text, pos=(0, 3), flag=wx.EXPAND | wx.ALL, border=5)

        # 创建输入token的标签和文本框
        self.token_label = wx.StaticText(self.panel, label='{:^10}'.format('Token'))
        self.token_text = wx.TextCtrl(self.panel)
        sizer.Add(self.token_label, pos=(2, 0), flag=wx.ALL, border=5)
        sizer.Add(self.token_text, pos=(2, 1), span=(1, 3), flag=wx.EXPAND | wx.ALL, border=5)

        # 创建输入fakeid的标签和文本框
        self.fakeid_label = wx.StaticText(self.panel, label='{:^10}'.format('Fake ID'))
        self.fakeid_text = wx.TextCtrl(self.panel)
        sizer.Add(self.fakeid_label, pos=(3, 0), flag=wx.ALL, border=5)
        sizer.Add(self.fakeid_text, pos=(3, 1), span=(1, 3), flag=wx.EXPAND | wx.ALL, border=5)
        # 添加开始日期标签和文本框
        self.start_date_label = wx.StaticText(self.panel, label='开始日期')
        self.start_date_text = wx.TextCtrl(self.panel)
        self.start_date_text.SetHint("yyyy-mm-dd")  # 设置虚影提示
        sizer.Add(self.start_date_label, pos=(1, 0), flag=wx.ALL, border=5)
        sizer.Add(self.start_date_text, pos=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)

        # 添加结束日期标签和文本框
        self.end_date_label = wx.StaticText(self.panel, label='结束日期')
        self.end_date_text = wx.TextCtrl(self.panel)
        self.end_date_text.SetHint("yyyy-mm-dd")  # 设置虚影提示
        sizer.Add(self.end_date_label, pos=(1, 2), flag=wx.ALL, border=5)
        sizer.Add(self.end_date_text, pos=(1, 3), flag=wx.EXPAND | wx.ALL, border=5)

        # 创建显示wxapi.print()内容的文本框
        self.output_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.output_text, pos=(4, 0), span=(1, 4), flag=wx.EXPAND | wx.ALL, border=5)

        # 创建提交按钮
        self.fetch_button = wx.Button(self.panel, label='{:^10}'.format('提交'))
        self.fetch_button.Bind(wx.EVT_BUTTON, self.on_fetch_content)
        self.fetch_button.SetBackgroundColour('#4F4F2F')
        self.fetch_button.SetForegroundColour('#FFFFFF')
        sizer.Add(self.fetch_button, pos=(5, 0), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=10)

        # 创建保存为CSV文件的按钮
        self.save_button = wx.Button(self.panel, label='{:^10}'.format('保存'))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save_to_csv)
        self.save_button.SetBackgroundColour('#4F4F2F')
        self.save_button.SetForegroundColour('#FFFFFF')
        sizer.Add(self.save_button, pos=(5, 2), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=10)

        # 创建刷新积分的按钮
        self.refresh_button = wx.Button(self.panel, label='刷新积分')
        self.refresh_button.Bind(wx.EVT_BUTTON, self.on_refresh_score)
        self.refresh_button.SetBackgroundColour('#4F4F2F')
        self.refresh_button.SetForegroundColour('#FFFFFF')
        sizer.Add(self.refresh_button, pos=(6, 0), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=10)

        # 创建教程按钮
        self.tutorial_button = wx.Button(self.panel, label='教程')
        self.tutorial_button.Bind(wx.EVT_BUTTON, self.on_tutorial)
        self.tutorial_button.SetBackgroundColour('#4F4F2F')
        self.tutorial_button.SetForegroundColour('#FFFFFF')
        sizer.Add(self.tutorial_button, pos=(6, 2), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=10)

        sizer.AddGrowableCol(1)
        self.panel.SetSizerAndFit(sizer)
        self.Show()

    def on_fetch_content(self, event):
        key = self.key_text.GetValue().strip()
        token = self.token_text.GetValue().strip()
        fakeid = self.fakeid_text.GetValue().strip()
        print('key',key,type(key))
        print('token',token,type(token))
        print('fakeid',fakeid,type(fakeid))

        self.spider = WeChatSpider(key, token, fakeid)
        fetch_thread = threading.Thread(target=self.fetch_content_thread)
        fetch_thread.start()

    def fetch_content_thread(self):
        start_time = self.start_date_text.GetValue().strip()
        end_time = self.end_date_text.GetValue().strip()
        if not start_time or not end_time:
            start_time , end_time = None,None
        content = self.spider.fetch_content(start_time,end_time)
        content = '\n'.join([str(item) for item in content])
        wx.CallAfter(self.output_text.SetValue, content)

    def on_save_to_csv(self, event):
        with wx.DirDialog(self, "Choose a folder", style=wx.DD_DEFAULT_STYLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                save_path = dlg.GetPath()
                save_thread = threading.Thread(target=self.save_csv_thread, args=(save_path,))
                save_thread.start()

    def save_csv_thread(self, save_path):
        self.spider.save_to_csv(save_path)
        wx.CallAfter(wx.MessageBox, 'Saved to CSV successfully!', 'Info', wx.OK | wx.ICON_INFORMATION)

    def on_refresh_score(self, event):
        key = self.key_text.GetValue()
        wxapi_load = WxApi(key)
        res = wxapi_load.get_score()
        res = re.findall(r'\d+', str(res))
        res = ''.join(res)
        self.score_text.SetValue(res)

    def on_tutorial(self, event):
        tutorial_content = {
            '教程':"",
            '1':'填入Api Key',
            '2':'获取对应你公众号的Token 和 Fake ID，在电脑上通过开发者工具，然后找到这两个',
            '3':'填入Token 和 Fake ID 和修改目录下的cookie文件',
            '4':'输入开始时间和结束时间（请按照时间格式),没有输入默认抓取全部',
            '5':'点击提交按钮',
            '6':'点击保存按钮，保存到csv',
            '7':'刷新积分，是查看剩余积分数'
        } # 教程内容
        tutorial_content = '\n'.join(f"{key}:{value}"for key,value in tutorial_content.items())
        self.output_text.SetValue(tutorial_content)


if __name__ == '__main__':
    app = wx.App()
    frame = SpiderApp(None, title='WeChat Spider')
    app.MainLoop()
