import os
import cv2
import numpy as np
import shutil
from scipy.stats import mode
from scipy import misc, ndimage
import math
list_a = []
list_b = []
list_t = []

def crop(gray):
    closed_1 = cv2.erode(gray, None, iterations=4)
    closed_1 = cv2.dilate(closed_1, None, iterations=4)
    blurred = cv2.blur(closed_1, (9, 9))
    # get the most frequent pixel
    num = mode(blurred.flat)[0][0] + 1
    # the threshold depends on the mode of your images' pixels
    num = num if num <= 30 else 1

    _, thresh = cv2.threshold(blurred, num, 200, cv2.THRESH_BINARY)
    # thresh = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,3,5)

    # you can control the size of kernel according your need.
    kernel = np.ones((13, 13), np.uint8)
    closed_2 = cv2.erode(thresh, kernel, iterations=4)
    closed_2 = cv2.dilate(closed_2, kernel, iterations=4)

    _, cnts, _ = cv2.findContours(closed_2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = sorted(cnts, key=cv2.contourArea, reverse=True)[0]

    # compute the rotated bounding box of the largest contour
    rect = cv2.minAreaRect(c)
    box = np.int0(cv2.boxPoints(rect))

    xs = [i[0] for i in box]
    ys = [i[1] for i in box]
    x1 = min(xs)
    x2 = max(xs)
    y1 = min(ys)
    y2 = max(ys)
    height = y2 - y1
    width = x2 - x1
    # crop_img = img[y1 + 100 :y1 + height - 100, x1 + 100:x1 + width -100]
    crop_img = gray[y1 :y1 + height, x1:x1 + width]
    return crop_img

def sift_kp(image):
    gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    sift = cv2.xfeatures2d_SIFT.create()
    kp,des = sift.detectAndCompute(image,None)
    kp_image = cv2.drawKeypoints(gray_image,kp,None)
    return kp_image,kp,des
def get_good_match(des1,des2):
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)
    return good
def siftImageAlignment(img1,img2):
   _,kp1,des1 = sift_kp(img1)
   _,kp2,des2 = sift_kp(img2)
   goodMatch = get_good_match(des1,des2)
   if len(goodMatch) > 4:
       ptsA= np.float32([kp1[m.queryIdx].pt for m in goodMatch]).reshape(-1, 1, 2)
       ptsB = np.float32([kp2[m.trainIdx].pt for m in goodMatch]).reshape(-1, 1, 2)
       ransacReprojThreshold = 4
       H, status =cv2.findHomography(ptsA,ptsB,cv2.RANSAC,ransacReprojThreshold);
       imgOut = cv2.warpPerspective(img2, H, (img1.shape[1],img1.shape[0]),flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
   return imgOut,H,status


def divide_method2(img, m, n):  # 分割成m行n列
    h, w = img.shape[0], img.shape[1]
    grid_h = int(h * 1.0 / (m - 1) + 0.5)  # 每个网格的高
    grid_w = int(w * 1.0 / (n - 1) + 0.5)  # 每个网格的宽

    # 满足整除关系时的高、宽
    h = grid_h * (m - 1)
    w = grid_w * (n - 1)

    # 图像缩放
    img_re = cv2.resize(img, (w, h),
                        cv2.INTER_LINEAR)  # 也可以用img_re=skimage.transform.resize(img, (h,w)).astype(np.uint8)
    # plt.imshow(img_re)
    gx, gy = np.meshgrid(np.linspace(0, w, n), np.linspace(0, h, m))
    gx = gx.astype(np.int)
    gy = gy.astype(np.int)

    divide_image = np.zeros([m - 1, n - 1, grid_h, grid_w],
                            np.uint8)  # 这是一个五维的张量，前面两维表示分块后图像的位置（第m行，第n列），后面三维表示每个分块后的图像信息

    for i in range(m - 1):
        for j in range(n - 1):
           # for n in range(3):
                divide_image[i, j] = img_re[gy[i][j]:gy[i + 1][j + 1], gx[i][j]:gx[i + 1][j + 1]]
    return divide_image

def center(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 200, apertureSize=3)

    # 霍夫变换
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 0)
    for rho, theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        if x1 == x2 or y1 == y2:
            continue

        t = float(y2 - y1) / (x2 - x1)
        rotate_angle = math.degrees(math.atan(t))
        if rotate_angle > 45:
            rotate_angle = -90 + rotate_angle
        elif rotate_angle < -45:
            rotate_angle = 90 + rotate_angle
        rotate_img = ndimage.rotate(img, rotate_angle)
        return rotate_img


def mathc_img(image,Target,value):

    img_gray = cv2.imread(image)
    w,h = img_gray.shape[:2]
    # img_gray = cv2.resize(img_gray,(int(w / 2), int(h / 2)))
    # img_gray = center(img_gray)
    if img_gray is None:
        return
    # img_gray = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)

    template = cv2.imread(Target)
    w, h = template.shape[:2]
    # template = cv2.resize(template, (int(w / 2), int(h / 2)))
    # template = center(template)

    template, _, _ = siftImageAlignment(img_gray, template)
    # cv2.imshow('template',template)
    # cv2.imshow('img_gray',img_gray)
    # cv2.waitKey(0)
    img_gray = cv2.cvtColor(img_gray, cv2.COLOR_BGR2GRAY)
    # img_gray = crop(img_gray)
    if template is None:
        return
    # template =  cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    # template = crop(template)
    # w, h = template.shape[::-1]
    # template = template[100:h - 200,500:w - 200]
    img1 = [[]]
    img2 = [[]]
    img1 = divide_method2(img_gray, 10, 10)
    img2 = divide_method2(template, 10, 10)

    dif_array_mean = []
    dif_array_stdv = []
    for i in range(0, img1.shape[0]):
        for j in range(0, img1.shape[1]):
            img_1 = img1[i][j]
            # img_2 = crop(img2[i][j])
            img_2 = img2[i][j]
            (mean1, stddv1) = cv2.meanStdDev(img_1)
            (mean2, stddv2) = cv2.meanStdDev(img_2)
            dif_stddv = stddv1 - stddv2
            dif_mean = mean1 - mean2
            dif_array_mean.append(dif_mean)
            dif_array_stdv.append(dif_stddv)
            print(image,i, "--》", Target,i, '-->  dif=', str(dif_mean), 'dif2-->', str(dif_stddv))

            if math.fabs(dif_stddv) > 1:
                cv2.imshow('img_1',img_1)
                cv2.imshow('img_2',img_2)
                # cv2.imshow('diff',cv2.absdiff(img_1,img_2))
                cv2.waitKey(0)
    print('max_diff==',max(dif_array_stdv,key=abs))
    # w0,h0 = img_gray.shape[::-1]
    # if w > w0 or h > h0:
    #     return -1
    # for i in range(h0):
    #     for j in range(w0):
    #         img_gray[i][j] = 255 - img_gray[i][j]
    #

    # for i in range(h):
    #     for j in range(w):
    #         v = template[i][j] - dif
    #         if v > 255:
    #             v = 255
    #         if v < 0:
    #             v = 0
    #
    #         template[i][j] = v
    # (mean1, stddv1) = cv2.meanStdDev(template)
    # dif = mean0 - mean1

    # res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    # cv2.imwrite("e:/tz/gh/test_result/" + image.split('/')[-1],img_gray)
    # cv2.imwrite("e:/tz/gh/test_result/" + Target.split('/')[-1],template)
    # threshold = value
    # loc = np.where(res >= threshold)
    # if math.fabs(dif) < 10:
    # print('mean0=',mean0,'  mean1=',mean1)


    # for pt in zip(*loc[::-1]):
    #     cv2.rectangle(img_gray, pt, (pt[0] + w , pt[1] + h ), (0,255,0), 2)
    #
    #     x,y = img_gray.shape[0:2]
    #     # img_rgb = cv2.resize(img_rgb,(int(x/2),int(y/2)))
    #     list_b.append(image.split('/')[-1])
    #     list_t.append(Target.split('/')[-1])
    #     cv2.imwrite("e:/tz/test_result/" + image.split('/')[-1],img_gray)
    #     return 0
    # return -1
# 小图
path = "E:/tz/gh/words/pics/t3/img2/"
# 大图
testPath = "E:/tz/gh/words/pics/t3/img1/"
value = 0.2

g_count = 0
all_list = []
for image in os.listdir(path):
    all_list.append(image)
for f in os.listdir(testPath):
    src = testPath + f
    list_a.append(f)
    for image in os.listdir(path):
        result = mathc_img( src,path + image, value)
        # if result == 0:
        #     g_count = g_count + 1
            # print(g_count)
            # break
intersection = list(set(list_a) - set(list_b))
intersection_t = list(set(all_list) - set(list_t))
# print('all_list:')
# for i in all_list:
#     print(i)
# print('****************************************************')
# print('list_b:')
# for i in list_t:
#     print(i)
#
# print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
# print('intersectoin_t::')
# for i in intersection_t:
#     os.remove(path + i)
#     print(i)

for f in intersection:
    shutil.copy(testPath + f, "e:/tz/pj7/" + f)

# print(intersection_t,':',intersection_t.__len__())