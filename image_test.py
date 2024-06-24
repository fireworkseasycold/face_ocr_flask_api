import cv2

# 读入原始图像
from img_touying import getHProjection, getVProjection

origineImage = cv2.imread('C:/Users/mahao/Desktop/test/test.png')

# 图像灰度化
image = cv2.cvtColor(origineImage, cv2.COLOR_BGR2GRAY)
# cv2.imshow('gray', image)
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
    cropImg = img[H_Start[i]:H_End[i], 0:w]
    # cv2.imshow('cropImg',cropImg)
    # 对行图像进行垂直投影
    W = getVProjection(cropImg)
    Wstart = 0
    Wend = 0
    W_Start = 0
    W_End = 0
    for j in range(len(W)):
        if W[j] > 0 and Wstart == 0:
            W_Start = j
            Wstart = 1
            Wend = 0
        if W[j] <= 0 and Wstart == 1:
            W_End = j
            Wstart = 0
            Wend = 1
        if Wend == 1:
            Position.append([W_Start, H_Start[i], W_End, H_End[i]])
            Wend = 0
print(Position)
# 根据确定的位置分割字符
for m in range(len(Position)):
    if Position[m][2] - Position[m][0] < 15 and Position[m][3] - Position[m][1] < 15:
        cv2.rectangle(origineImage, (Position[m][0], Position[m][1]), (Position[m][2], Position[m][3]), (255, 255, 255),
                  Position[m][2] - Position[m][0])
cv2.imshow('image', origineImage)
cv2.waitKey(0)