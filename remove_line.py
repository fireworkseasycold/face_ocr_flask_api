import cv2
""""
根据需要去除表格
"""

def remove_table(img):
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
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // 50))
    eroded = cv2.erode(binary, kernel, iterations=1)
    dilatedrow = cv2.dilate(eroded, kernel, iterations=1)

    # 标识交点
    bitwiseAnd = cv2.bitwise_and(dilatedcol, dilatedrow)

    # 标识表格
    merge = cv2.add(dilatedcol, dilatedrow)
    _, contours, hierarchy = cv2.findContours(merge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img, contours, -1, (255, 255, 255), 3)
    cv2.imwrite("C:/Users/mahao/Desktop/test2/ceshi.png", img)
    return img

#
# img = cv2.imread('C:/Users/mahao/Desktop/test2/wyzd/6.jpeg')
# img1 = remove_table(img)
# cv2.imwrite('C:/Users/mahao/Desktop/test2/1.jpg', img1)
