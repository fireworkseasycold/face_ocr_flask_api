import base64
import json
import configparser
import cv2
import requests

from remove_line import remove_table

try:
    cf = configparser.ConfigParser()
    cf.read("./config.ini", encoding='utf-8')
    ocrPath = cf.get("config", "ocrPath")
except Exception as e:
    print("读取配置文件异常:%s" % e)


def img_to_b46_code(img):
    img_str = cv2.imencode(".png", img)[1].tostring()
    b64_code = base64.b64encode(img_str)
    return b64_code


def get_double_image_text(img, img1, needRemoveSeal):
    """img=cv2.imread(imgurl)"""
    if needRemoveSeal != 0:
        _, _, img = cv2.split(img)
        _, _, img1 = cv2.split(img1)
    # img = img[50:img.shape[0] - 50, 50:img.shape[1] - 50]
    # img1 = img1[50:img1.shape[0] - 50, 50:img1.shape[1] - 50]
    img = remove_table(img)
    img1 = remove_table(img1)
    postdata = {'pic1': img_to_b46_code(img), 'pic2': img_to_b46_code(img1)}
    r = requests.post('http://%s/img_diff' % ocrPath, data=postdata)
    res = json.loads(r.text)
    return res


def get_once_image_text(img, textLine):
    if int(textLine) != 1:  #不是单行，就去表格
        img = remove_table(img)
    # cv2.imwrite('C:/Users/gly/Desktop/test2/1.png',img[(1148 - 32):(1148 + 32), (int(1244 - 372 / 2)):int(1244 + 372 / 2)])
    postdata = {'pic': img_to_b46_code(img), 'textLine': textLine}
    r = requests.post('http://%s/img_to_text' % ocrPath, data=postdata)  #https://127.0.0.1/:8080/img_to_text
    res = json.loads(r.text)
    return res

if __name__ == '__main__':
    p = 'F:/hlsdkj/chineseocr/test/ocr.jpg'
    img_to_b46_code(p)
    get_once_image_text(p, 0)

