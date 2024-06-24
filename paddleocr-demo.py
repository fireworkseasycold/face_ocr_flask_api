# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/12/31 20:08
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : paddleocr-demo.py
# @Software: PyCharm

"""
pip install paddlepaddle paddleocr
修改报错：paddleocr\paddleocr.py", line 33, in <module>
    tools = importlib.import_module('.', 'tools')
    为
tools = importlib.import_module('tools')
ppocr = importlib.import_module('ppocr')
ppstructure = importlib.import_module( 'ppstructure')
"""

from paddleocr import PaddleOCR, draw_ocr

# 模型路径下必须含有model和params文件
# ocr = PaddleOCR(use_angle_cls=True,
#                 use_gpu=False)  # det_model_dir='{your_det_model_dir}', rec_model_dir='{your_rec_model_dir}', rec_char_dict_path='{your_rec_char_dict_path}', cls_model_dir='{your_cls_model_dir}', use_angle_cls=True
# #没有模型会自动下载
# img_path = 'ocr.jpg'
# result = ocr.ocr(img_path, cls=True)
#
# for line in result:
#     print('一行',line,sep=':::')


#s为paddleocr返回的数据结构例子
s=[
    [

    [
    [[27.0, 194.0], [358.0, 194.0], [358.0, 207.0], [27.0, 207.0]],
     ('人生是一场负重的狂奔，需要不停地在每一个', 0.9453936815261841)
    ],

    [
        [[28.0, 217.0], [357.0, 217.0], [357.0, 231.0], [28.0, 231.0]],
     ('密路口做出选择。而每一个选择，都将通往另', 0.8914216160774231)
    ],

    [
        [[27.0, 241.0], [216.0, 241.0], [216.0, 255.0], [27.0, 255.0]],
     ('一条截然不同的命运之路。', 0.8970022797584534)
    ]

    ]
]
print('识别字体行数:',len(s[0]))
for i in s[0]:
    print('识别框：',i[0],'识别结果：',i[1][0],'准确率：',i[1][1])


# # 显示结果
# from PIL import Image
#
# image = Image.open(img_path).convert('RGB')
# boxes = [line[0] for line in result]
# txts = [line[1][0] for line in result]
# scores = [line[1][1] for line in result]
# im_show = draw_ocr(image, boxes, txts, scores, font_path='simfang.ttf')
# im_show = Image.fromarray(im_show)
# im_show.save('result.jpg')  # 结果图片保存在代码同级文件夹中。


import numpy as np

def np_to_list(arr):
    """判断是否为numpy，如果是，转为list"""
    this_type_str = type(arr)
    if this_type_str is np.ndarray:
        arr = arr.tolist()
    elif this_type_str in [np.int, np.int32, np.int64]:
        arr = [int(arr), ]
    else:
        arr = arr
    return arr

