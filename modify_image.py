import cv2

from PIL import Image
import numpy


def modify_image(pic_path, pos_x, pos_y, seal_w, seal_h):
    img = cv2.imread(pic_path)
    # pos_x = 1128
    # pos_y = 1913
    # # 截图的长和宽
    # seal_w = 430
    # seal_h = 430
    # 截图
    cut_img = img[pos_y:pos_y + seal_h, pos_x:pos_x + seal_w]

    # opencv转格式到Image
    img2 = Image.fromarray(cv2.cvtColor(cut_img, cv2.COLOR_BGR2RGBA))
    # img2.show()
    # img2 = cut_img.convert('RGBA')
    im = img2.copy()

    # 分离红色通道
    im_cv = cv2.cvtColor(numpy.asarray(im), cv2.COLOR_RGB2BGR)
    for col in ['Blue', "Green", 'Red']:
        cv2.namedWindow(col, 0)
        cv2.resizeWindow(col, 960, 480)
    _, _, r = cv2.split(im_cv)

    # 去红色
    im1 = Image.fromarray(cv2.cvtColor(r, cv2.COLOR_BGR2RGBA))
    im2 = im1.copy()
    pixdata = im2.load()
    r_value = 125
    g_value = 15
    b_value = 0
    for y in range(im2.size[1]):
        for x in range(im2.size[0]):
            b = pixdata[x, y][0]
            g = pixdata[x, y][1]
            r = pixdata[x, y][2]
            if (r > r_value or g < g_value or b < b_value):
                pixdata[x, y] = (5, 5, 255, 0)

    im = im2
    im_orgin = Image.open(pic_path)
    x, y = im.size
    p = Image.new('RGBA', im.size, (255, 255, 255))
    p.paste(im, (0, 0, x, y), im)

    im_orgin.paste(p, (pos_x, pos_y, pos_x + x, pos_y + y))
    return numpy.asarray(im_orgin)

if __name__ == "__main__":
    img = modify_image('C:\\Users\\mahao\\Desktop\\test2\\1.jpg',1128,1913,430,430)
    cv2.imwrite('C:\\Users\\mahao\\Desktop\\test2\\11.jpg', img)
