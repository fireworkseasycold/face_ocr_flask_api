# 水平仪自动矫正后根据水印图像某些像素点的间距进行判断
import cv2
# 待检验
path = r"E:\shiyin\temp_b-011.jpg"
img = cv2.imread(path)
template = cv2.imread(path,0)
# 检测model
target1 = cv2.imread(r"E:\shiyin\demo_a_2.jpg",0)
# target2 = cv2.imread(r"D:\xupython\2018-12-29test_Gra\demo_a_3.jpg",0)
# target3 = cv2.imread(r"D:\xupython\2018-12-29test_Gra\demo_a_4.jpg",0)
# target4 = cv2.imread(r"D:\xupython\2018-12-29test_Gra\demo_a_5.jpg",0)
# target5 = cv2.imread(r"D:\xupython\2018-12-29test_Gra\demo_a_6.jpg",0)
# target6 = cv2.imread(r"D:\xupython\2018-12-29test_Gra\demo_a_7.jpg",0)
# target7 = cv2.imread(r"D:\xupython\2018-12-29test_Gra\demo_a_8.jpg",0)
# target8 = cv2.imread(r"D:\xupython\2018-12-29test_Gra\demo_a_9.jpg",0)
# target9 = cv2.imread(r"D:\xupython\2018-12-29test_Gra\demo_a_10.jpg",0)

w1, h1 = target1.shape[::-1]
# w2, h2 = target2.shape[::-1]
# w3, h3 = target3.shape[::-1]
# w4, h4 = target4.shape[::-1]
# w5, h5 = target5.shape[::-1]
# w6, h6 = target6.shape[::-1]
# w7, h7 = target7.shape[::-1]
# w8, h8 = target8.shape[::-1]
# w9, h9 = target9.shape[::-1]

res1 = cv2.matchTemplate(template, target1, cv2.TM_SQDIFF)
# res2 = cv2.matchTemplate(template, target2, cv2.TM_SQDIFF)
# res3 = cv2.matchTemplate(template, target3, cv2.TM_SQDIFF)
# res4 = cv2.matchTemplate(template, target4, cv2.TM_SQDIFF)
# res5 = cv2.matchTemplate(template, target5, cv2.TM_SQDIFF)
# res6 = cv2.matchTemplate(template, target6, cv2.TM_SQDIFF)
# res7 = cv2.matchTemplate(template, target7, cv2.TM_SQDIFF)
# res8 = cv2.matchTemplate(template, target8, cv2.TM_SQDIFF)
# res9 = cv2.matchTemplate(template, target9, cv2.TM_SQDIFF)

min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
# min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(res2)
# min_val3, max_val3, min_loc3, max_loc3 = cv2.minMaxLoc(res3)
# min_val4, max_val4, min_loc4, max_loc4 = cv2.minMaxLoc(res4)
# min_val5, max_val5, min_loc5, max_loc5 = cv2.minMaxLoc(res5)
# min_val6, max_val6, min_loc6, max_loc6 = cv2.minMaxLoc(res6)
# min_val7, max_val7, min_loc7, max_loc7 = cv2.minMaxLoc(res7)
# min_val8, max_val8, min_loc8, max_loc8 = cv2.minMaxLoc(res8)
# min_val9, max_val9, min_loc9, max_loc9 = cv2.minMaxLoc(res9)

top_left1 = min_loc1
# top_left2 = min_loc2
# top_left3 = min_loc3
# top_left4 = min_loc4
# top_left5 = min_loc5
# top_left6 = min_loc6
# top_left7 = min_loc7
# top_left8 = min_loc8
# top_left9 = min_loc9

bottom_right1 = (top_left1[0] + w1, top_left1[1] + h1)
# bottom_right2 = (top_left2[0] + w2, top_left2[1] + h2)
# bottom_right3 = (top_left3[0] + w3, top_left3[1] + h3)
# bottom_right4 = (top_left4[0] + w4, top_left4[1] + h4)
# bottom_right5 = (top_left5[0] + w5, top_left5[1] + h5)
# bottom_right6 = (top_left6[0] + w6, top_left6[1] + h6)
# bottom_right7 = (top_left7[0] + w7, top_left7[1] + h7)
# bottom_right8 = (top_left8[0] + w8, top_left8[1] + h8)
# bottom_right9 = (top_left9[0] + w9, top_left9[1] + h9)

cv2.rectangle(img, top_left1, bottom_right1, (0,0,255), 2)
# cv2.rectangle(img, top_left2, bottom_right2, (0,255,0), 2)
# cv2.rectangle(img, top_left3, bottom_right3, (255,0,0), 2)
# cv2.rectangle(img, top_left4, bottom_right4, (0,160,255), 2)
# cv2.rectangle(img, top_left5, bottom_right5, (255,255,0), 2)
# cv2.rectangle(img, top_left6, bottom_right6, (180,180,0), 2)
# cv2.rectangle(img, top_left7, bottom_right7, (100,100,160), 2)
# cv2.rectangle(img, top_left8, bottom_right8, (100,160,100), 2)
# cv2.rectangle(img, top_left9, bottom_right9, (160,100,200), 2)

print(max_loc1)
# print(max_loc2)
# print(max_loc3)
# print(max_loc4)
# print(max_loc5)
# print(max_loc6)
# print(max_loc7)
# print(max_loc8)
# print(max_loc9)

cv2.namedWindow("result",0)
cv2.resizeWindow("result", 1080, 1528)
cv2.imshow("result", img)
cv2.waitKey(0)
cv2.destroyAllWindows()