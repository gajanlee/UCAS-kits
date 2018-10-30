import configparser
import requests
import time
import numpy as np
from PIL import Image
from io import BytesIO
import configparser

from code import CodeRecognizer
from utils import  *

class UCAS:
    def __init__(self, user):
        self.__session = requests.Session()
        self.__user = user
        # self.login()
        
    def login(self):
        pass

    @property
    def session(self):
        return self.__session
    @property
    def user(self):
        return self.__user

class PaymentUCAS(UCAS):
    def __init__(self, user, order):
        self.host_url = "http://payment.ucas.ac.cn"
        self.base_url = "http://payment.ucas.ac.cn/NetWorkUI/"
        self.order = order
        super(PaymentUCAS, self).__init__(user)
    
    def login(self):
        if self.request("login", "post", data={
            'nickName': self.user.get("username"),
            'password': self.user.get("password"),
            'checkCode': self.checkCode(),
            'logintype': 'PLATFORM',
        }).text.find("退出") != -1:
            return True
        # }).text.find("退出") != -1:
        #return True

    def routes_vali(self):
        """
            Get Nominated Route's Information, check the remaining seats.
        """
        msg = self.request("querySeat", "post", data={
            "bookingdate": self.order["date"],
            "factorycode": "R001",
            "routecode": self.order["routecode"],
        }).json()

        remainseat = int(msg["returndata"]["freeseat"])

        if msg["returncode"] != "SUCCESS" or not remainseat:
            log("查询余票失败，剩余座位：%s" % (remainseat))
        else:
            log("剩余票：%s" % (remainseat))
            return True
    
    def bookTicket(self):
        msg = self.request("bookTicket", "post", data={
            "routecode": self.order["routecode"],
            "payAmt": "6.00",
            "bookingdate": self.order["date"],
            "payProjectId": "4",
            "tel": self.user.get("telnum"),
            "factorycode": "R001",
        }).json()

        if msg["returncode"] == "SUCCESS":
            log("预订成功，请打开这个网址完成支付: {baseurl}{bookprefix}{orderno}".format(baseurl=self.base_url, bookprefix="showUserSelectPayType25", orderno=msg["payOrderTrade"]["id"]))
            return True
        else:
            log("预订失败，请重试")

    def checkCode(self):
        img = Image.open(BytesIO(self.request("checkCode", "get").content))
        # binary and gray
        img = img.point(lambda p: 255 if p > 127 else 0).convert("1")
        # Cut the image brims with width 1
        w, h = img.size
        img = img.crop((1, 1, w-1, h-1))
        # divide checkcode image into 4 pieces.
        w, h = img.size
        imgs = [img.crop((w/4*i, 0, w/4*(i+1), h)) for i in range(4)]
        return "".join([CodeRecognizer(img) for img in imgs])
    
    def request(self, step="login", type="get", data=None):
        opts = {
            "login": "fontuserLogin",
            "checkCode": "authImage?temp=0.10349747758414296",
            "queryBusDate": "queryBusByDate",
            "querySeat": "queryRemainingSeats",
            "bookTicket": "reservedBusCreateOrder",
        }
        return getattr(self.session, type)(self.base_url + opts[step], data=data)


def process_orders(cf):
    user, order_keys = cf["user"], [order for order in cf.sections() if order.startswith("order")]
    for order in order_keys:
        log("正在处理订单：%s" % (",".join(["%s: %s" % (k, v) for k, v in cf[order].items()])))

        payment = PaymentUCAS(user, cf[order])
        if not payment.login():
            raise(Exception("用户信息错误！"))
        elif not payment.routes_vali():
            cf.remove_section(order)
            log("移除了此订单")
        elif not payment.bookTicket():
            cf.remove_section(order)
            log("移除了此订单")
    return not [order for order in cf.sections() if order.startswith("order")]

if __name__ == "__main__":
    cf = configparser.ConfigParser()
    cf.read("info.conf")
   
    while process_orders(cf):
        time.sleep(2)