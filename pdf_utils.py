import math
import os
import shutil

from PIL import Image
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import glob
import fitz
from reportlab.pdfgen import canvas
import qrcode
import logging


# 删除置顶目录下的所有文件
def _del_files(path_file):
    ls = os.listdir(path_file)
    for i in ls:
        f_path = os.path.join(path_file, i)
        # 判断是否是一个目录,若是,则递归删除
        if os.path.isdir(f_path):
            _del_files(f_path)
        else:
            os.remove(f_path)


# 复制文件
def _copy_file(path_file):
    if not os.path.exists('./temp/'):
        os.makedirs('./temp/')
    if len(path_file.rsplit('/', 1)) > 1:
        target_file = './temp/%s' % path_file.rsplit('/', 1)[1]
    else:
        target_file = './temp/%s' % path_file.rsplit('\\', 1)[1]
    shutil.copyfile(path_file, target_file)
    return target_file


# 把指定图片打包为pdf
def _pic2pdf(image_folder, output_path):
    doc = fitz.open()
    for img in sorted(glob.glob("%s*.png" % image_folder)):  # 读取图片，确保按文件名排序
        img_doc = fitz.open(img)  # 打开图片
        pdf_bytes = img_doc.convertToPDF()  # 使用图片创建单页的 PDF
        img_pdf = fitz.open("pdf", pdf_bytes)
        doc.insertPDF(img_pdf)  # 将当前页插入文档
    if os.path.exists(output_path):
        os.remove(output_path)
    doc.save(output_path)  # 保存pdf文件
    doc.close()
    return output_path


# 把指定pdf按页转为图片pdf
def read_pdf(filename, output_path, image_folder):
    try:
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        pdffile = glob.glob(filename)[0]
        doc = fitz.open(pdffile)
        _del_files(image_folder)
        for pg in range(0, doc.pageCount):
            page = doc[pg]
            zoom = int(130)
            rotate = int(0)
            trans = fitz.Matrix(zoom / 100.0, zoom / 100.0).preRotate(rotate)
            pm = page.getPixmap(matrix=trans, alpha=0)
            pm.writePNG(image_folder + '%s.png' % str(pg + 1))
        path = _pic2pdf(image_folder, output_path)
        return path
    except Exception as e:
        print(e)
        logging.error(e)
        return None


# 把指定pdf按页转为图片
def pdf_to_image(filename, image_folder):
    try:
        pdffile = glob.glob(filename)[0]
        doc = fitz.open(pdffile)
        _del_files(image_folder)
        for pg in range(0, doc.pageCount):
            page = doc[pg]
            zoom = int(300)
            rotate = int(0)
            trans = fitz.Matrix(zoom / 100.0, zoom / 100.0).preRotate(rotate)
            pm = page.getPixmap(matrix=trans, alpha=0)
            pm.writePNG(image_folder + '%s.png' % str(pg + 1))
        return True
    except Exception as e:
        print(e)
        logging.error(e)
        return False


# 添加文字水印
def create_text_watermark(content, translate_x=1, translate_y=5, font_size=40, rotate=30, opacity=0.6):
    """水印信息"""
    # 默认大小为21cm*29.7cm
    file_name = "mark.pdf"
    c = canvas.Canvas(file_name)
    # 移动坐标原点(坐标系左下为(0,0))
    c.translate(translate_x * cm, translate_y * cm)
    # 设置字体
    pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))
    # c.setFont("Helvetica", 80)
    c.setFont("SimHei", font_size)
    # 指定描边的颜色
    c.setStrokeColorRGB(0, 1, 0)
    # 指定填充颜色
    c.setFillColorRGB(0, 1, 0)
    # 旋转45度,坐标系被旋转
    c.rotate(rotate)
    # 指定填充颜色
    c.setFillColorRGB(0, 0, 0, 0.1)
    # 设置透明度,1为不透明
    # c.setFillAlpha(0.1)
    # 画几个文本,注意坐标系旋转的影响
    c.drawString(100, 0, content)
    c.setFillAlpha(opacity)
    # 关闭并保存pdf文件
    c.save()
    return file_name


# 添加图片水印
def create_image_watermark(filename, translate_x=10, translate_y=0, width=60, height=60, rotate=0, opacity=0.6):
    """水印信息"""
    # 默认大小为21cm*29.7cm
    file_name = "qrmark.pdf"
    c = canvas.Canvas(file_name)
    c.translate(translate_x * cm, translate_y * cm)
    # 移动坐标原点(坐标系左下为(0,0))
    c.drawImage(filename, (1 * cm), (17 * cm), width, height, mask='auto')
    c.rotate(rotate)
    # 关闭并保存pdf文件
    c.setFillAlpha(opacity)
    c.save()
    return file_name


# 添加二维码
def create_qrcode(content, translate_x=0, translate_y=10, width=60, height=60):
    """水印信息"""
    # 默认大小为21cm*29.7cm
    file_name = "qrmark.pdf"
    c = canvas.Canvas(file_name, pagesize=(20 * cm, 20 * cm))
    c.translate(translate_x * cm, translate_y * cm)
    # 移动坐标原点(坐标系左下为(0,0))
    img = qrcode.make(content)
    img.save("qrcode.png")
    c.drawImage("qrcode.png", (1 * cm), (17 * cm), width, height)
    # 关闭并保存pdf文件
    c.save()
    return file_name


# 添加骑缝章
def create_seal_image(image_path, page_width, page_height, count, is_double_print):
    try:
        img = Image.open(image_path)
        width = img.size[0]
        height = img.size[1]
        if is_double_print == 0:
            create_count = count
        else:
            create_count = math.ceil(count / 2)
        step = width / create_count
        pdf_list = []
        if not os.path.exists('./static/image/'):
            os.makedirs('./static/image/')
        _del_files('./static/image/')
        for i in range(count):
            img1 = img.crop((step * i, 0, step * (i + 1), height))
            img1.save('./static/image/%s.png' % str(i))
            """水印信息"""
            # 默认大小为21cm*29.7cm
            file_name = "./static/image/seal%s.pdf" % str(i)
            c = canvas.Canvas(file_name, pagesize=(page_width, page_height))
            # 移动坐标原点(坐标系左下为(0,0))
            c.drawImage('./static/image/%s.png' % str(i), int(page_width) - step, int(page_height) / 2 - height / 2,
                        step, height,
                        mask='auto')
            c.save()
            os.remove('./static/image/%s.png' % str(i))
            pdf_list.append(file_name)
        return pdf_list
    except Exception as e:
        print(e)
        logging.error(e)
        return None


# 打印骑缝页
def add_seal_image_on_right(pdf_file_in, image_path, pdf_file_out, is_double_print):
    """把水印添加到pdf中"""
    try:
        pdf_output = PdfFileWriter()
        new_path = _copy_file(pdf_file_in)
        input_stream = open(new_path, 'rb')
        pdf_input = PdfFileReader(input_stream, strict=False)
        # 获取PDF文件的页数
        pageNum = pdf_input.getNumPages()
        lastpage = pdf_input.getPage(pageNum - 1)
        page_width = lastpage.mediaBox.getWidth()
        page_height = lastpage.mediaBox.getHeight()
        mark_list = create_seal_image(image_path, page_width, page_height, pageNum, is_double_print)
        # 读入水印pdf文件
        # 给每一页打水印
        file_list = []
        for i in range(pageNum):
            page = pdf_input.getPage(i)
            if is_double_print == 0:
                f = open(mark_list[i], 'rb')
                pdf_watermark = PdfFileReader(f, strict=False)
                page.mergePage(pdf_watermark.getPage(0))
                file_list.append(f)
            else:
                if i % 2 == 0:
                    f = open(mark_list[int(i / 2)], 'rb')
                    pdf_watermark = PdfFileReader(f, strict=False)
                    page.mergePage(pdf_watermark.getPage(0))
                    file_list.append(f)

            page.compressContentStreams()  # 压缩内容
            pdf_output.addPage(page)
        if pdf_file_in == pdf_file_out:
            os.remove(pdf_file_in)
        if os.path.exists(pdf_file_out):
            os.remove(pdf_file_out)
        pdf_output.write(open(pdf_file_out, 'wb'))
        for i in range(len(file_list)):
            file_list[i].close()
        input_stream.close()
        os.remove(new_path)
        return pdf_file_out
    except Exception as e:
        print(e)
        logging.error(e)
        return None


# 合并pdf
def add_watermark(pdf_file_in, pdf_file_mark, pdf_file_out, add_black_page):
    """把水印添加到pdf中"""
    try:
        pdf_output = PdfFileWriter()
        new_path = _copy_file(pdf_file_in)
        input_stream = open(new_path, 'rb')
        pdf_input = PdfFileReader(input_stream, strict=False)

        # 获取PDF文件的页数
        pageNum = pdf_input.getNumPages()

        # 读入水印pdf文件
        pdf_watermark = PdfFileReader(open(pdf_file_mark, 'rb'), strict=False)
        # 给每一页打水印
        for i in range(pageNum):
            page = pdf_input.getPage(i)
            page.mergePage(pdf_watermark.getPage(0))
            page.compressContentStreams()  # 压缩内容
            pdf_output.addPage(page)
            if add_black_page is True:
                pdf_output.addBlankPage()
        if pdf_file_in == pdf_file_out:
            os.remove(pdf_file_in)
        if os.path.exists(pdf_file_out):
            os.remove(pdf_file_out)
        pdf_output.write(open(pdf_file_out, 'wb'))
        input_stream.close()
        os.remove(new_path)
        return pdf_file_out
    except Exception as e:
        print(e)
        logging.error(e)
        return None


# 添加pdf空白页
def add_blank_page(pdf_file_in, pdf_file_out, only_last):
    try:
        pdf_output = PdfFileWriter()
        new_path = _copy_file(pdf_file_in)
        input_stream = open(new_path, 'rb')
        pdf_input = PdfFileReader(input_stream, strict=False)
        # 获取PDF文件的页数
        pageNum = pdf_input.getNumPages()
        # 给每一页打水印
        for i in range(pageNum):
            page = pdf_input.getPage(i)
            page.compressContentStreams()  # 压缩内容
            pdf_output.addPage(page)
            if only_last == 0:
                if i == 0:
                    pdf_output.insertBlankPage()
                    pdf_output.addBlankPage()
                else:
                    if i != pageNum - 1:
                        pdf_output.addBlankPage()
            else:
                if i == pageNum - 1:
                    pdf_output.addBlankPage()
        if pdf_file_in == pdf_file_out:
            os.remove(pdf_file_in)
        if os.path.exists(pdf_file_out):
            os.remove(pdf_file_out)
        pdf_output.write(open(pdf_file_out, 'wb'))
        input_stream.close()
        os.remove(new_path)
        return pdf_file_out
    except Exception as e:
        print(e)
        logging.error(e)
        return None


# 调整页序
def transform_pdf_page(pdf_file_in, pdf_file_out, page_list):
    try:
        pdf_output = PdfFileWriter()
        new_path = _copy_file(pdf_file_in)
        input_stream = open(new_path, 'rb')
        pdf_input = PdfFileReader(input_stream, strict=False)
        # 获取PDF文件的页数
        pageNum = pdf_input.getNumPages()
        # 给每一页打水印
        result = []
        for i in range(pageNum):
            for j in range(len(page_list)):
                new_list = page_list[j].split(',')
                if str(i + 1) == new_list[0]:
                    result.append(int(new_list[1]) - 1)
                if str(i + 1) == new_list[1]:
                    result.append(int(new_list[0]) - 1)
        for i in range(pageNum):
            if i in result:
                str_index = result.index(i)
                if str_index % 2 == 0:
                    page = pdf_input.getPage(result[str_index + 1])
                else:
                    page = pdf_input.getPage(result[str_index - 1])
            else:
                page = pdf_input.getPage(i)
            page.compressContentStreams()  # 压缩内容
            pdf_output.addPage(page)
        if pdf_file_in == pdf_file_out:
            os.remove(pdf_file_in)
        if os.path.exists(pdf_file_out):
            os.remove(pdf_file_out)
        pdf_output.write(open(pdf_file_out, 'wb'))
        input_stream.close()
        os.remove(new_path)
        return pdf_file_out
    except Exception as e:
        print(e)
        logging.error(e)
        return None
