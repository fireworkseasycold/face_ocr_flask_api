import datetime

import cv2
import numpy as np
import pytesseract
from PIL import Image
import threading

'''水平投影'''


class MyThread(threading.Thread):
    def __init__(self, func, pic_data):
        super(MyThread, self).__init__()
        self.func = func
        self.pic_data = pic_data

    def run(self):
        self.result = self.func(self.pic_data)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


def fun(region):
    stext1 = pytesseract.image_to_string(region, lang='chi_sim').replace(" ", "")
    return stext1


def getHProjection(image):
    # hProjection = np.zeros(image.shape, np.uint8)
    # 图像高与宽
    (h, w) = image.shape
    # 长度与图像高度一致的数组
    h_ = [0] * h
    # 循环统计每一行白色像素的个数
    for y in range(h):
        for x in range(w):
            if image[y, x] == 255:
                h_[y] += h / 3
    return h_


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    # 读入原始图像
    origineImage = cv2.imread('image_ch4.png')
    # 图像灰度化
    # image = cv2.imread('test.jpg',0)
    image = cv2.cvtColor(origineImage, cv2.COLOR_BGR2GRAY)
    # 将图片二值化
    retval, img = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    # cv2.imshow('binary', img)
    # 图像高与宽
    (h, w) = img.shape
    Position = []
    # 水平投影
    H = getHProjection(img)

    start = 0
    H_Start = []
    H_End = []
    list = []
    # 根据水平投影获取垂直分割位置
    for i in range(len(H)):
        if H[i] > 0 and start == 0:
            H_Start.append(i)
            start = 1
        if H[i] <= 0 and start == 1:
            H_End.append(i)
            start = 0
    # 分割行，分割之后再进行列分割并保存分割位置
    for i in range(len(H_Start)):
        # 获取行图像
        # 对行图像进行垂直投影
        Position.append([0, H_Start[i], w, H_End[i]])
    # 根据确定的位置分割字符
    text = ""
    threads = []
    for m in range(3):
        start_index = m * int(len(Position) / 3)
        end_index = (m + 1) * int(len(Position) / 3) - 1
        test = len(Position) - 1
        img = Image.open("image_ch4.png")
        if m < 2:
            print(Position[m][0], Position[start_index][1], Position[m][2], Position[end_index][3])
            region = img.crop((Position[m][0], Position[start_index][1], Position[m][2], Position[end_index][3]))
            thread1 = MyThread(fun, region)
            thread1.start()
            threads.append(thread1)
            for t in threads:
                t.join()  # 一定要join，不然主线程比子线程跑的快，会拿不到结果
        else:
            print(Position[m][0], Position[start_index][1], Position[m][2], Position[len(Position) - 1][3])
            region = img.crop(
                (Position[m][0], Position[start_index][1], Position[m][2], Position[len(Position) - 1][3]))
            thread1 = MyThread(fun, region)
            thread1.start()
            threads.append(thread1)
        for t in threads:
            t.join()
            print(t.get_result())

    end_time = datetime.datetime.now()
    print(text)
    print((end_time - start_time).seconds)
