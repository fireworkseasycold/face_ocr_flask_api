# !/usr/bin/python
# encoding:utf-8
import base64
import datetime
import os

import cv2
import requests
import threading

from log import Logger

log = Logger('test.log', level='debug')


def send_post(i):
    postdata = {'picPath': 'C:/Users/mahao/Desktop/test2/zjcs/%s.Jpeg' % str(i + 1), 'keyword': '银行盖章,公司盖章'}
    r = requests.post('http://localhost:5000/ocr/keyword_position/', data=postdata)
    log.logger.info(r.text)


class myThread(threading.Thread):
    def __init__(self, page_no):
        threading.Thread.__init__(self)
        self.page_no = page_no

    def run(self):
        log.logger.info("-----第%s页----------" % str(self.page_no + 1))
        send_post(self.page_no)
        print("退出线程：" + str(self.page_no))


if __name__ == "__main__":
    starttime = datetime.datetime.now()
    threads = []
    for i in range(125):
        thread = myThread(i)
        thread.start()
        thread.join()
        threads.append(thread)
    for t in threads:
        t.join()
    print(datetime.datetime.now() - starttime)
