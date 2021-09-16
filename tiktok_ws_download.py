import json
import random
import time

import requests
import websocket

from driver import Driver


class TiktokDownloader(object):
    def __init__(self, url=None) -> None:
        super().__init__()
        self.request_id = 0
        self.target_url = url
        self.count = 0
        self.video_list = []
        self.height_list=0

    # 通过websocket接管浏览器，建立连接
    @staticmethod
    def new_websocket_connection():
        # url:chrome的机器地址
        response = requests.get(url='http://127.0.0.1:9222/json')
        print(response)
        if response.status_code != 200:
            raise ValueError("Remote chrome is not ready ,please check")

        # 接管浏览器
        ws_conn = response.json()[0].get('webSocketDebuggerUrl')
        print(ws_conn)
        return websocket.create_connection(ws_conn)

    # websocket向浏览器发送指令
    def ws_command(self, ws_conn, method, **kwargs):
        self.request_id += 1
        command = {'method': method,
                   'id': self.request_id,
                   'params': kwargs}
        ws_conn.send(json.dumps(command))
        msg = json.loads(ws_conn.recv())
        if msg.get('id') == self.request_id:
            return msg

    # 获取页面信息
    def parse_page(self):
        ws_conn = self.new_websocket_connection()
        msg = self.ws_command(ws_conn, 'Page.navigate', url=self.target_url)
        time.sleep(1.5)
        get_href = """$x = function (xpath, context) { //定义$x方法执行xpath
            var nodes = [];
            try {
                var doc = (context && context.ownerDocument) || window.document;
                var results = doc.evaluate(xpath, context || doc, null, XPathResult.ANY_TYPE, null);
                var node;
                while (node = results.iterateNext()) {
                    nodes.push(node);
                }
            } catch (e) {
                throw e;
            }
            return nodes;
        };
        var href_obj=$x('//*[@id="root"]/div/div[2]/div/div[4]/div[1]/div[2]/ul//a/@href');
        var href_array=[];
        for(var i=0;i<href_obj.length;i++){href_array[i]=href_obj[i]['value']};JSON.stringify(href_array);
        """
        page_down = "window.scrollTo(0,document.body.scrollHeight)"  # 向下翻页

        while True:
            # 获取页面中的视频详情页链接
            msg = self.ws_command(
                ws_conn, 'Runtime.evaluate', expression=get_href)

            # 控制浏览器向下翻页
            self.ws_command(ws_conn, 'Runtime.evaluate', expression=page_down)
            time.sleep(random.random()+3)

            href_list = json.loads(msg['result']['result']['value'])
            for url in href_list:
                if 'http' in url:
                    self.video_list.append(url)
                    print(url)
            self.video_list = list(set(self.video_list))

            print("共抓取%s条" % len(self.video_list))

            # 获取当前页面高度
            end_page_height = int(self.ws_command(
                ws_conn, 'Runtime.evaluate', expression='document.body.scrollHeight')['result']['result']['value'])
            print("end_page_height:%s" % end_page_height)

            # 判断是否到页面最底部
            if end_page_height == self.height_list:
                break
            else:
                self.height_list=end_page_height

        return self.video_list



if __name__ == '__main__':
    # 实例化浏览器对象
    driver = Driver()  # 传入浏览器路劲
    proc = driver.proc()
    try:
        ttDownloader = TiktokDownloader(
            url='https://www.douyin.com/user/MS4wLjABAAAA4N4OrZzTSmCPp8vVAqCeyU215Kav2JgFv2Lfy4DNWRs')
        ttDownloader.parse_page()
    except Exception as e:
        print(e)

    # 关闭浏览器
    proc.kill()
