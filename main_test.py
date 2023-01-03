#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import configparser
import datetime
import json
import re
import threading

import cv2
import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
from flasgger import Swagger
from idna import unichr
# from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
import difflib
import pytesseract
from PIL import ImageFile
from win32com.client import constants, gencache
import pythoncom
from flask import Response

from file_utils import to_json, file_iterator
from pdf_utils import read_pdf, create_text_watermark, add_watermark, create_image_watermark, create_qrcode, \
    add_blank_page, transform_pdf_page, add_seal_image_on_right, pdf_to_image

ImageFile.LOAD_TRUNCATED_IMAGES = True

# 读取配置文件
try:
    cf = configparser.ConfigParser()
    cf.read("./config.ini", encoding='utf-8')
    port = cf.get("config", "port")
    pdf_to_image_path = cf.get("config", "pdfToImagePath")
    host = cf.get("config", "host")
    img_crop_len = cf.get("config", "img_crop_len")
except Exception as e:
    print("读取配置文件异常：%s" % (e))

# Flask
app = Flask(__name__)
CORS(app, resources=r'/*')
Swagger(app)


@app.route('/difffile/<string:filename>/', methods=['POST', 'GET'])
def render_html(filename):
    filename = filename.lower().strip()
    path = 'static/%s' % filename
    count = 0
    for file in os.listdir(path):
        if file.endswith('.html'):
            count = count + 1
    return render_template('index.html', file_count=count, filename=filename)


# 构建接口返回结果
def build_api_result(code, message, data):
    result = {
        "code": code,
        "message": message,
        "data": data
    }
    print(result)
    return jsonify(result)


# 打印分割线
def print_split_line():
    print("=" * 90)


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


class PdfThread(threading.Thread):
    def __init__(self, func, pdf_path, page_no):
        super(PdfThread, self).__init__()
        self.func = func
        self.pdf_path = pdf_path
        self.page_no = page_no

    def run(self):
        self.result = self.func(self.pdf_path, self.page_no)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += unichr(inside_code)
    return rstring


# 裁剪图片
# def crop_img(pic_data):
#     img = cv2.imread(pic_data)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     (height, width) = gray.shape
#     result = []
#     for y in range(height):
#         if abs(y - height / 2) < 20:
#             for x in range(width):
#                 if gray[y, x] == 0:
#                     if not y in result:
#                         result.append(y)
#     threads = []
#     if len(result) > 0:
#         thread1 = MyThread(identify_picture, img[0:result[0] - 20, 0:width])
#         thread2 = MyThread(identify_picture, img[result[0] - 20:height, 0:width])
#         thread1.start()
#         thread2.start()
#         threads.append(thread1)
#         threads.append(thread2)
#         for t in threads:
#             t.join()  # 一定要join，不然主线程比子线程跑的快，会拿不到结果
#         if threads[0].get_result() is None or threads[1].get_result() is None:
#             return None
#         text_result = threads[0].get_result() + '\n' + threads[1].get_result()
#     else:
#         text_result = identify_picture(img)
#     self_text = text_result.splitlines(keepends=True)
#     return self_text
def get_blank_position(img):
    img, y, threads_len = img
    h, w = img.shape
    for position_y in range(y, y + int(h / threads_len)):
        cut = 0
        for rx in img[position_y, :]:
            if rx > 0:
                cut += 1
        if cut == 0:
            # if position_y:
            return position_y


def crop_img(pic_data):
    img = cv2.imread(pic_data)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (height, width) = gray.shape
    gray = gray[50:height - 50, 50:width - 50]
    img = img[50:height - 50, 50:width - 50]
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    threads = []
    result = []
    self_threads = []

    for count in range(int(img_crop_len)):
        thread = MyThread(get_blank_position, (thresh, int(height / int(img_crop_len)) * count, int(img_crop_len)))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()
        result.append(t.get_result())
    for i in range(len(result)):
        if i < len(result) - 1:
            new_thread = MyThread(post_chinese_ocr, img[result[i]:result[i + 1], 0:width])
            new_thread.start()
            self_threads.append(new_thread)
        else:
            new_thread = MyThread(post_chinese_ocr, img[result[i]:height, 0:width])
            new_thread.start()
            self_threads.append(new_thread)

    text_result = ""
    for tt in range(len(self_threads)):
        self_threads[tt].join()
        if tt < len(self_threads) - 1:
            text_result += self_threads[tt].get_result() + '\n'
        else:
            text_result += self_threads[tt].get_result()

    self_text = text_result.splitlines(keepends=True)
    return self_text


def post_chinese_ocr(img):
    img_str = cv2.imencode(".png", img)[1].tostring()
    b64_code = base64.b64encode(img_str)
    postdata = {'imgString': b64_code, 'textAngle': False, 'textLine': False, 'billModel': ''}
    r = requests.post('http://192.168.0.137:8080/get_text', data=postdata)
    response_jeon = json.loads(r.text)
    print(response_jeon)


# 识别图片
def identify_picture(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(~gray, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)
        rows, cols = binary.shape
        scale = 20
        # 识别横线
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // scale, 1))
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilatedcol = cv2.dilate(eroded, kernel, iterations=1)
        # 识别竖线
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // scale))
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilatedrow = cv2.dilate(eroded, kernel, iterations=1)

        # 标识交点
        bitwiseAnd = cv2.bitwise_and(dilatedcol, dilatedrow)

        # 标识表格
        merge = cv2.add(dilatedcol, dilatedrow)
        _, contours, hierarchy = cv2.findContours(merge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img, contours, -1, (255, 255, 255), 3)
        img_text = pytesseract.image_to_string(img, lang='chi_sim')
        img_text = strQ2B(re.sub('\\n(\\s)+', '\n', img_text, 0).replace(' ', ''))
        return img_text
    except Exception as error:
        print(error)
        return None


# word转pdf
def createPdf(word_path, pdf_path):
    """
    word转pdf
    :param word_path: word文件路径
    :param pdf_path:  生成pdf文件路径
    """
    try:
        pythoncom.CoInitialize()
        word = gencache.EnsureDispatch('Word.Application')
        doc = word.Documents.Open(word_path, ReadOnly=1)
        doc.ExportAsFixedFormat(pdf_path,
                                constants.wdExportFormatPDF,
                                Item=constants.wdExportDocumentWithMarkup,
                                CreateBookmarks=constants.wdExportCreateHeadingBookmarks)
        word.Quit(constants.wdDoNotSaveChanges)
        return pdf_path
    except Exception as error:
        print(error)
        return None


# 获取pdf文字
def get_txt_from_pdf(path, doc_page):
    try:
        # 获取文档对象
        fp = open(path, "rb")
        # 创建一个PDF文档解释器
        parser = PDFParser(fp)
        # PDF文档的对象
        doc = PDFDocument()
        # 连接解释器和文档对象
        parser.set_document(doc)
        doc.set_parser(parser)
        # 初始化文档
        doc.initialize('')
        # 创建PDF资源管理器
        resource = PDFResourceManager()
        # 参数分析器
        laparam = LAParams()
        # 创建一个聚合器
        device = PDFPageAggregator(resource, laparams=laparam)
        # 创建PDF页面解释器
        interpreter = PDFPageInterpreter(resource, device=device)
        result = []
        i = 0
        # 使用文档对象得到页面的集合
        for page in doc.get_pages():
            # 使用页面解释器来读取
            if i == doc_page - 1:
                interpreter.process_page(page)
                # 使用聚合器来获取内容
                layout = device.get_result()
                for out in layout:
                    if hasattr(out, "get_text"):
                        result.append(out.get_text())
            i += 1
        pdf_text = ''
        for text in result:
            pdf_text += text
        pdf_text = strQ2B(re.sub('\\n(\\s)+', '\n', pdf_text, 0).replace(' ', ''))
        pdf_text = pdf_text.splitlines(keepends=True)
        fp.close()
        return pdf_text
    except Exception as error:
        print(error)
        return None


@app.route('/ocr/word_to_pdf/', methods=["POST"])
def word_to_pdf():
    """
        This is the word to pdf API
        ---
        tags:
          - word转pdf
        parameters:
          - name: sourcePath
            type: string
            required: true
            in: formData
            description: word文件路径
          - name: targetPath
            type: string
            required: true
            in: formData
            description: 生成pdf文件路径
        responses:
          500:
            description:  word to pdf failed!
          200:
            description: A language with its awesomeness
            schema:
              id: wordToPdf
              properties:
                success:
                  type: boolean
                  description: success
                  default: false
                totalTime:
                  type: string
                  description: totalTime
                  default: totalTime
                pdfPath:
                  type: string
                  description: pdfPath
                  default: pdfPath
                message:
                  type: string
                  description: message
                  default: message
        """
    start_time = datetime.datetime.now()
    word_path = request.form["sourcePath"]
    pdf_path = request.form["targetPath"]
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    if os.path.exists(word_path) is not True:
        return jsonify(
            success=False,
            totalTime=0,
            pdfPath=None,
            message='没有找到word文件'
        )
    path = createPdf(word_path, pdf_path)
    if path is not None:
        message = '成功'
    else:
        message = '失败'
    return jsonify(
        success=path is not None,
        totalTime=(datetime.datetime.now() - start_time).seconds,
        pdfPath=path,
        message=message
    )


@app.route("/ocr/image_pdf_diff/", methods=['POST'])
def image_pdf_diff():
    """
        This is the image and pdf diff API
        ---
        tags:
          - 图片pdf对比api
        parameters:
          - name: picUrl
            type: string
            required: true
            in: formData
            description: 图片url
          - name: pdfUrl
            type: string
            in: formData
            required: true
            description: pdf url
          - name: pageNo
            type: number
            in: formData
            required: true
            description: 页数
          - name: fileName
            type: string
            in: formData
            required: true
            description: 文件名
        responses:
          500:
            description: image diff failed!
          200:
            description: A language with its awesomeness
            schema:
              id: pdfDiff
              properties:
                success:
                  type: boolean
                  description: success
                  default: false
                totalTime:
                  type: string
                  description: totalTime
                  default: totalTime
                diffPageUrl:
                  type: string
                  description: diffPageUrl
                  default: diffPageUrl
                message:
                  type: string
                  description: message
                  default: message
        """
    starttime = datetime.datetime.now()
    pic_url = request.form['picUrl']
    pdf_url = request.form["pdfUrl"]
    page_no = int(request.form["pageNo"])
    file_name = request.form["fileName"]
    if os.path.exists(pic_url) is not True:
        return jsonify(
            success=False,
            totalTime=0,
            diffPageUrl=None,
            message="没有找到图片"
        )
    elif os.path.exists(pdf_url) is not True:
        return jsonify(
            success=False,
            totalTime=0,
            diffPageUrl=None,
            message="没有找到pdf文件"
        )
    threads = []
    thread1 = PdfThread(get_txt_from_pdf, pdf_url, page_no)
    thread2 = MyThread(crop_img, pic_url)
    thread1.start()
    thread2.start()
    threads.append(thread1)
    threads.append(thread2)
    for t in threads:
        t.join()  # 一定要join，不然主线程比子线程跑的快，会拿不到结果

    if threads[0].get_result() is None or threads[1].get_result() is None:
        return jsonify(
            success=False,
            totalTime=(datetime.datetime.now() - starttime).seconds,
            diffPageUrl=None,
            message="失败"
        )
    d = difflib.HtmlDiff()
    html = d.make_file(threads[0].get_result(), threads[1].get_result(),
                       pdf_url.split("/")[len(pdf_url.split("/")) - 1],
                       pic_url.split("/")[len(pic_url.split("/")) - 1])  # context不填默认显示全部的数据。那就太大了，填了true默认显示5行数据
    html = html.encode()
    if not os.path.exists('./static/%s/' % file_name):
        os.makedirs(r'./static/%s/' % file_name)
    fp = open("./static/" + file_name + "/%s.html" % (page_no), "w+b")
    fp.write(html)
    fp.close()
    endtime = datetime.datetime.now()
    return jsonify(
        success=True,
        totalTime=(endtime - starttime).seconds,
        diffPageUrl='/difffile/%s/' % file_name,
        message="成功"
    )


@app.route('/ocr/image_diff/', methods=['POST'])
def image_diff():
    """
        This is the image diff API
        ---
        tags:
          - 图图对比api
        parameters:
          - name: pic1
            type: string
            required: true
            in: formData
            description: 第一张图片base64
          - name: pic2
            type: string
            in: formData
            required: true
            description: 第二章图片base64
          - name:  pageNo
            type: number
            in: formData
            required: true
            description: 页数
          - name:  fileName
            type: string
            in: formData
            required: true
            description: 文件名
        responses:
          500:
            description: image diff failed!
          200:
            description: A language with its awesomeness
            schema:
              id: image_diff
              properties:
                success:
                  type: boolean
                  description: success
                  default: false
                totalTime:
                  type: string
                  description: totalTime
                  default: totalTime
                diffPageUrl:
                  type: string
                  description: diffPageUrl
                  default: diffPageUrl
                message:
                  type: string
                  description: message
                  default: message
        """
    starttime = datetime.datetime.now()
    page_no = int(request.form['pageNo'])
    pic1_url = request.form["pic1"]
    pic2_url = request.form["pic2"]
    file_name = request.form["fileName"]
    if os.path.exists(pic2_url) is not True or os.path.exists(pic1_url) is not True:
        return "没有找到图片", 500
    threads = []
    thread1 = MyThread(crop_img, pic1_url)
    thread2 = MyThread(crop_img, pic2_url)
    thread1.start()
    thread2.start()
    threads.append(thread1)
    threads.append(thread2)
    for t in threads:
        t.join()  # 一定要join，不然主线程比子线程跑的快，会拿不到结果

    if threads[0].get_result() is None or threads[1].get_result() is None:
        return jsonify(
            success=False,
            totalTime=0,
            diffPageUrl=None,
            message="没有找到图片"
        )
    d = difflib.HtmlDiff()
    html = d.make_file(threads[0].get_result(), threads[1].get_result(),
                       pic1_url.split("/")[len(pic1_url.split("/")) - 1],
                       pic2_url.split("/")[len(pic2_url.split("/")) - 1])  # context不填默认显示全部的数据。那就太大了，填了true默认显示5行数据
    html = html.encode()
    if not os.path.exists('./static/%s/' % file_name):
        os.makedirs(r'./static/%s/' % file_name)
    fp = open("./static/" + file_name + "/%s.html" % (page_no), "w+b")
    fp.write(html)
    fp.close()
    endtime = datetime.datetime.now()
    return jsonify(
        success=True,
        totalTime=(endtime - starttime).seconds,
        diffPageUrl='/difffile/%s/' % file_name,
        message='成功'
    )


@app.route('/ocr/image_text_diff/', methods=['POST'])
def imageTextDiff():
    """
            This is the image text diff API
            ---
            tags:
              - 图片文字对比api
            parameters:
              - name: picPath
                type: string
                required: true
                in: formData
                description: 图片路径
              - name: diffText
                in: formData
                type: string
                required: true
                description: 比对文本
              - name:  pageNo
                type: number
                in: formData
                required: true
                description: 页数
              - name:  fileName
                type: string
                in: formData
                required: true
                description: 文件名称
            responses:
              500:
                description: image diff failed!
              200:
                description: A language with its awesomeness
                schema:
                  id: image_pdf_diff
                  properties:
                    success:
                      type: boolean
                      description: success
                      default: false
                    totalTime:
                      type: string
                      description: totalTime
                      default: totalTime
                    diffPageUrl:
                      type: string
                      description: diffPageUrl
                      default: diffPageUrl
                    message:
                      type: string
                      description: message
                      default: message
            """
    starttime = datetime.datetime.now()
    page_no = int(request.form['pageNo'])
    pic_path = request.form['picPath']
    diff_text = request.form['diffText']
    file_name = request.form['fileName']

    if os.path.exists(pic_path) is not True:
        return jsonify(
            success=False,
            totalTime=0,
            diffPageUrl=None,
            message='没有找到图片'
        )
    pic_text = crop_img(pic_path)
    d = difflib.HtmlDiff()
    html = d.make_file(pic_text, diff_text,
                       pic_path.split("/")[len(pic_path.split("/")) - 1],
                       file_name)  # context不填默认显示全部的数据。那就太大了，填了true默认显示5行数据
    html = html.encode()
    if os.path.exists('./static/%s/' % file_name) is not True:
        os.makedirs(r'./static/%s/' % file_name)
    fp = open("./static/" + file_name + "/%s.html" % page_no, "w+b")
    fp.write(html)
    fp.close()
    endtime = datetime.datetime.now()
    return jsonify(
        success=True,
        totalTime=(endtime - starttime).seconds,
        diffPageUrl='/difffile/%s/' % file_name,
        message='成功'
    )


@app.route("/pdf/pdf2ImagePdf/", methods=["POST"])
def pdf_to_image_pdf():
    """
        This is the image text diff API
        ---
        tags:
          - pad转图片pdf
        parameters:
          - name: filePath
            type: string
            required: true
            in: formData
            description: pdf路径
          - name: targetPath
            type: string
            required: true
            in: formData
            description: 新的pdf路径
        responses:
          500:
            description: image diff failed!
          200:
            description: A language with its awesomeness
            schema:
              id: pdf_to_image
              properties:
                success:
                  type: boolean
                  description: success
                  default: false
                path:
                  type: string
                  description: path
                  default: path
                message:
                  type: string
                  description: message
                  default: message
        """
    file_path = request.form['filePath']
    out_put_path = request.form['targetPath']
    if not os.path.exists(file_path):
        return jsonify(
            success=False,
            path=None,
            message="没有找到pdf文件"
        )
    path = read_pdf(file_path, out_put_path, pdf_to_image_path)
    return jsonify(
        success=path is not None,
        path=path,
        message="成功" if path is not None else "失败"
    )


@app.route("/pdf/pdfToImage/", methods=["POST"])
def pdfToImage():
    """
        This is the image text diff API
        ---
        tags:
          - pdf转图片
        parameters:
          - name: filePath
            type: string
            required: true
            in: formData
            description: pdf路径
          - name: targetImageFolder
            type: string
            required: true
            in: formData
            description: 新的pdf路径
        responses:
          500:
            description: image diff failed!
          200:
            description: A language with its awesomeness
            schema:
              id: pdf_to_image
              properties:
                success:
                  type: boolean
                  description: success
                  default: false
                path:
                  type: string
                  description: path
                  default: path
                message:
                  type: string
                  description: message
                  default: message
        """
    pdf_path = request.form["filePath"]
    target_image_folder = request.form["targetImageFolder"]
    if not os.path.exists(pdf_path):
        return jsonify(
            success=False,
            page=None,
            message='没有找到pdf文件'
        )
    if not os.path.exists(target_image_folder):
        os.makedirs(target_image_folder)
    path = pdf_to_image(pdf_path, target_image_folder)
    return jsonify(
        success=path,
        page=target_image_folder,
        message="成功" if path is not None else "失败"
    )


@app.route("/pdf/transformPage/", methods=["POST"])
def transformPage():
    """
        This is the image text diff API
        ---
        tags:
          - pdf调整页序
        parameters:
          - name: filePath
            type: string
            required: true
            in: formData
            description: pdf路径
          - name: targetPath
            type: string
            required: true
            in: formData
            description: 新的pdf路径
          - name: pageList
            type: string
            required: true
            in: formData
            description: 页码列表  用逗号隔开
        responses:
          500:
            description: image diff failed!
          200:
            description: A language with its awesomeness
            schema:
              id: pdf_to_image
              properties:
                success:
                  type: boolean
                  description: success
                  default: false
                path:
                  type: string
                  description: path
                  default: path
                message:
                  type: string
                  description: message
                  default: message
        """
    pdf_path = request.form["filePath"]
    out_put_path = request.form["targetPath"]
    page_list = request.form["pageList"]
    page_list = page_list.split('-')
    path = transform_pdf_page(pdf_path, out_put_path, page_list)
    return jsonify(
        success=path is not None,
        page=path,
        message="成功" if path is not None else "失败"
    )


@app.route("/pdf/<string:transformPdf>/", methods=["POST"])
def set_text_watermark(transformPdf):
    """
        This is the image text diff API
        ---
        tags:
          - pdf添加文字水印
        parameters:
          - name: filePath
            type: string
            required: true
            in: formData
            description: pdf路径
          - name: text
            type: string
            required: false
            in: formData
            description: 水印文字
          - name: fontSize
            type: number
            required: false
            in: formData
            description: 文字大小
          - name: left
            type: number
            required: false
            in: formData
            description: 左边偏移
          - name: bottom
            type: number
            required: false
            in: formData
            description: 底部偏移
          - name: rotate
            type: number
            required: false
            in: formData
            description: 旋转角度
          - name: opacity
            type: number
            required: false
            in: formData
            description: 透明度
          - name: width
            type: number
            required: false
            in: formData
            description: 图片宽度
          - name: height
            type: number
            required: false
            in: formData
            description: 图片高度
          - name: picPath
            type: string
            required: false
            in: formData
            description: 图片名称
          - name: targetPath
            type: string
            required: true
            in: formData
            description: 新的pdf路径
          - name: onlyLast
            type: number
            required: false
            in: formData
            description: 是否最后一页添加空白页
        responses:
          500:
            description: image diff failed!
          200:
            description: A language with its awesomeness
            schema:
              id: pdf_to_image
              properties:
                success:
                  type: boolean
                  description: success
                  default: false
                path:
                  type: string
                  description: path
                  default: path
                message:
                  type: string
                  description: message
                  default: message
        """
    default_left = 0
    default_bottom = 0
    if transformPdf == "create_text_watermark":
        default_left = 1
        default_bottom = 5
    elif transformPdf == "create_image_watermark":
        default_left = 10
        default_bottom = 0
    elif transformPdf == "create_qrcode":
        default_left = 0
        default_bottom = 10
    file_path = request.form['filePath']
    text = request.form.get('text', "")
    position_left = request.form.get('left', default_left)
    position_bottom = request.form.get('bottom', default_bottom)
    font_size = request.form.get('fontSize', 40)
    rotate = request.form.get('rotate', 30)
    opacity = request.form.get('opacity', 0.6)
    pic_filename = request.form.get('picPath', '')
    pic_width = request.form.get('width', 60)
    pic_height = request.form.get('height', 60)
    out_put_path = request.form["targetPath"]
    only_last = request.form.get('onlyLast', 0)
    pdf_file_mark = ""
    if transformPdf == "create_text_watermark":
        if text == '':
            return jsonify(
                success=False,
                path=None,
                message='水印文字不能为空'
            )
        pdf_file_mark = create_text_watermark(text, int(position_left), int(position_bottom), int(font_size),
                                              int(rotate),
                                              float(opacity))
    elif transformPdf == "create_image_watermark":
        if pic_filename == '':
            return jsonify(
                success=False,
                path=None,
                message='图片不能为空'
            )
        pdf_file_mark = create_image_watermark(pic_filename, int(position_left), int(position_bottom), int(pic_width),
                                               int(pic_height), int(rotate), float(opacity))
    elif transformPdf == "create_qrcode":
        if text == '':
            return jsonify(
                success=False,
                path=None,
                message='二维码文字不能为空'
            )
        pdf_file_mark = create_qrcode(text, int(position_left), int(position_bottom), int(pic_width), int(pic_height))
    elif transformPdf == "add_blank_page":
        pdf_file_mark = create_qrcode(text, int(position_left), int(position_bottom), int(pic_width), int(pic_height))
    if transformPdf == "add_blank_page":
        path = add_blank_page(file_path, out_put_path, int(only_last))
    else:
        path = add_watermark(file_path, pdf_file_mark, out_put_path, False)
    return jsonify(
        success=path is not None,
        path=path,
        message='成功' if path is not None else '失败'
    )


@app.route("/pdf/perforationWithType", methods=["POST"])
def perforationWithType():
    """
        This is the image text diff API
        ---
        tags:
          - pdf盖骑缝章
        parameters:
          - name: filePath
            type: string
            required: true
            in: formData
            description: pdf路径
          - name: targetPath
            type: string
            required: true
            in: formData
            description: 新的pdf路径
          - name: imagePath
            type: string
            required: true
            in: formData
            description: 印章图片,
          - name: isDoublePrint
            type: number
            required: false
            in: formData
            description: 是否双面打印
        responses:
          500:
            description: image diff failed!
          200:
            description: A language with its awesomeness
            schema:
              id: pdf_to_image
              properties:
                success:
                  type: boolean
                  description: success
                  default: false
                path:
                  type: string
                  description: path
                  default: path,
                message:
                  type: string
                  description: message
                  default: message
        """
    pdf_path = request.form["filePath"]
    out_put_path = request.form["targetPath"]
    image_path = request.form["imagePath"]
    is_double_print = request.form.get("isDoublePrint", 0)
    is_double_print = int(is_double_print)
    if not os.path.exists(pdf_path):
        return jsonify(
            success=False,
            path=None,
            message='没有找到pdf文件'
        )
    if not os.path.exists(image_path):
        return jsonify(
            success=False,
            path=None,
            message='没有找到印章图片'
        )
    path = add_seal_image_on_right(pdf_path, image_path, out_put_path, is_double_print)
    return jsonify(
        success=path is not None,
        path=path,
        message='成功' if path is not None else '失败'
    )


# 下载
@app.route('/download', methods=['GET'])
def download():
    """
        文件下载
    :return:
    """
    file_path = request.values.get('filepath')
    if file_path is None:
        return to_json({'success': 0, 'message': '请输入参数'})
    else:
        if file_path == '':
            return to_json({'success': 0, 'message': '请输入正确路径'})
        else:
            if not os.path.isfile(file_path):
                return to_json({'success': 0, 'message': '文件路径不存在'})
            else:
                filename = os.path.basename(file_path)
                response = Response(file_iterator(file_path))
                response.headers['Content-Type'] = 'application/octet-stream'
                response.headers["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
                return response


if __name__ == "__main__":
    print_split_line()
    print("Welcome")
    print_split_line()
    # Run
    app.config['JSON_AS_ASCII'] = False
    app.run(host=host, port=port, debug=False, use_reloader=False)
