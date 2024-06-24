import time

import cv2
import numpy as np
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed, PDFResourceManager, PDFPageInterpreter
import os
import fitz
import glob
from win32com.client import constants, gencache


def read_pdf(filename):
    pdffile = glob.glob(filename)[0]
    doc = fitz.open(pdffile)
    for pg in range(0, doc.pageCount):
        page = doc[pg]
        zoom = int(300)
        rotate = int(0)
        trans = fitz.Matrix(zoom / 100.0, zoom / 100.0).preRotate(rotate)
        pm = page.getPixmap(matrix=trans, alpha=0)
        pm.writePNG(r'../ocr/image2/%s.png' % str(pg + 1))


def createPdf(wordPath, pdfPath):
    """
    word转pdf
    :param wordPath: word文件路径
    :param pdfPath:  生成pdf文件路径
    """
    word = gencache.EnsureDispatch('Word.Application')
    doc = word.Documents.Open(wordPath, ReadOnly=1)
    doc.ExportAsFixedFormat(pdfPath,
                            constants.wdExportFormatPDF,
                            Item=constants.wdExportDocumentWithMarkup,
                            CreateBookmarks=constants.wdExportCreateHeadingBookmarks)
    word.Quit(constants.wdDoNotSaveChanges)


def get_txt_from_pdf(path, file_name, doc_page):
    # 获取文档对象
    fp = open(os.path.join(path, file_name), "rb")
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
    return result


if __name__ == "__main__":
    # ---------按页获取pdf文字---------
    # b_content = get_txt_from_pdf('d:/project/ocr/', "doc1.pdf", 1)
    # pdf_text = ''
    # for text in b_content:
    #     pdf_text += text + '\n'

    # ---------识别图片---------
    # img = cv2.imread("d:/project/ocr/image/1.png")
    # # 二值化
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # binary = cv2.adaptiveThreshold(~gray, 255,
    #                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)
    #
    # rows, cols = binary.shape
    # scale = 20
    # # 识别横线
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // scale, 1))
    # eroded = cv2.erode(binary, kernel, iterations=1)
    # # cv2.imshow("Eroded Image",eroded)
    # dilatedcol = cv2.dilate(eroded, kernel, iterations=1)
    # # 识别竖线
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // scale))
    # eroded = cv2.erode(binary, kernel, iterations=1)
    # dilatedrow = cv2.dilate(eroded, kernel, iterations=1)
    # # 标识交点
    # bitwiseAnd = cv2.bitwise_and(dilatedcol, dilatedrow)
    # # 标识表格
    # merge = cv2.add(dilatedcol, dilatedrow)
    # _, contours, hierarchy = cv2.findContours(merge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(img, contours, -1, (255, 255, 255), 3)
    # stext1 = pytesseract.image_to_string(img, lang='chi_sim')
    # stext1 = re.sub('\\n(\\s)+', '\n', stext1, 0).replace(' ', '')
    # pdf_text = re.sub('\\n(\\s)+', '\n', pdf_text, 0).replace(' ', '')
    # text1_lines = stext1.splitlines()
    # text2_lines = pdf_text.replace(" ", "").splitlines()
    # d = difflib.HtmlDiff()
    # html = d.make_file(text1_lines, text2_lines, "gxte.json", "gxzs.json")  # context不填默认显示全部的数据。那就太大了，填了true默认显示5行数据
    # html = html.encode()
    # fp = open("./static/diff.html", "w+b")
    # fp.write(html)
    # fp.close()

    # ---------pdf转图片---------
    # read_pdf(r'../ocr/doc1.pdf')

    # ---------word转pdf---------
    # createPdf('d:/project/ocr/doc1.doc', 'd:/project/ocr/doc1.pdf')

    # ---------打印格式化时间---------
    # t = time.localtime(time.time())
    # print(time.strftime("%Y-%m-%d %H:%M:%S", t))

    # ---------霍夫直线---------
    # img = cv2.imread('d:/project/ocr/image_doc2/3.png')
    # img = cv2.GaussianBlur(img, (3, 3), 0)
    # edges = cv2.Canny(img, 50, 150, apertureSize=3)
    # lines = cv2.HoughLines(edges, 1, np.pi / 180, 118)
    # result = img.copy()
    # # 经验参数
    # minLineLength = 100
    # maxLineGap = 50
    # lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 30, minLineLength, maxLineGap)
    # for line in lines:
    #     for x1, y1, x2, y2 in line:
    #         cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 5)
    # cv2.imwrite("d:/project/ocr/image_doc2/111.png", img)

    img = cv2.imread("d:/project/ocr/image/8888.jpg")
    # 二值化
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
    cv2.imwrite("D:/project/ocr/image/8889.jpg", img)
