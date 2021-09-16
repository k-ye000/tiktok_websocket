from subprocess import Popen


class Driver(object):
    def __init__(self,path=r'C:\Program Files\Google\Chrome\Application\chrome.exe') -> None:
        super().__init__()
        # 开启chrome远程调试功能
        self.args = [path,   #传入浏览器路径
                     '--remote-debugging-port=9222',
                     ]
    def proc(self):
        return Popen(self.args)
    