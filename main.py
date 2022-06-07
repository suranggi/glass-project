import cv2
import numpy as np

img_path = 'laser_pattern/red11.jpg'


def empty(a):
    pass


def img_resize(img, scale):
    img_width = int(img.shape[1] * scale)
    img_height = int(img.shape[0] * scale)
    img_dim = (img_width, img_height)
    img_resized = cv2.resize(img, img_dim, interpolation=cv2.INTER_AREA)
    return img_resized


def pattern_detect(path, blur2, par1, par2, blur1=5):
    img = cv2.imread(path)
    img = img[20:100, 20:100]
    # img = img_resize(img, 0.4)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (blur1, blur1), blur2)
    thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    ret, otsu = cv2.threshold(img_blur, 230, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    edges = cv2.Canny(img_blur, par1, par2)
    sobel = cv2.Sobel(img_blur, cv2.CV_64F, 1, 0, 3)
    cv2.imshow('result', edges)
    cv2.imshow('result_gray', img_gray)
    cv2.imshow('thresh', thresh)
    cv2.imshow('otsu', otsu)
    cv2.imshow('sobel', sobel)
    cv2.waitKey(1)


win_name = 'Trackbars'
cv2.namedWindow(win_name)
cv2.resizeWindow(win_name, 640, 480)
cv2.createTrackbar('blur1', win_name, 1, 20, empty)
cv2.createTrackbar('blur2', win_name, 0, 1000, empty)
cv2.createTrackbar('thresh1', win_name, 110, 1000, empty)
cv2.createTrackbar('thresh2', win_name, 3, 15, empty)
cv2.createTrackbar('kernel', win_name, 0, 20, empty)


if __name__ == '__main__':
    while True:
        blur1 = cv2.getTrackbarPos('blur1', win_name)
        if blur1 % 2 == 0:
            blur1 += 1
        blur2 = cv2.getTrackbarPos('blur2', win_name)

        thresh1 = cv2.getTrackbarPos('thresh1', win_name)
        if thresh1 < 3:
            thresh1 = 3
        if thresh1 % 2 == 0:
            thresh1 += 1
        thresh2 = cv2.getTrackbarPos('thresh2', win_name)

        kernel = cv2.getTrackbarPos('kernel', win_name)
        if kernel % 2 == 0:
            kernel += 1

        kernal = np.ones((kernel, kernel), np.uint8)

        img_ori = cv2.imread(img_path)
        img_ori = img_ori[:, 440:3400]
        # img_ori = img_resize(img_ori, 0.45)
        img = img_ori
        img = img_resize(img, 0.3)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # img_gray = cv2.fastNlMeansDenoising(img_gray)
        img_blur = cv2.GaussianBlur(img_gray, (blur1, blur1), blur2)

        adapt_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, thresh1,
                                             thresh2)
        moprh_img = cv2.erode(adapt_thresh, kernal, iterations=1)
        # denoised = cv2.morphologyEx(adapt_thresh, cv2.MORPH_CLOSE, kernal)

        edged = cv2.Canny(moprh_img, 75, 100)

        #test
        se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1,2))
        bg = cv2.morphologyEx(adapt_thresh, cv2.MORPH_ERODE, se)
        out_gray = cv2.divide(adapt_thresh, bg, scale=255)
        out_binary = cv2.threshold(out_gray, 0, 255, cv2.THRESH_OTSU)[1]


        # For detect lines pattern
        lines = cv2.HoughLinesP(out_binary, 1, np.pi/180, 50)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(img, (x1,y1), (x2,y2), (0,255,0),3)

        cv2.imshow('img_ori', img_ori)
        cv2.imshow('img', img)
        cv2.imshow('result', adapt_thresh)
        cv2.imshow('denoised', out_binary)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
