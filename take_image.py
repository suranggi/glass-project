from pypylon import pylon
import cv2
import os
import numpy as np


def empty(a):
    pass

class Camera:
    # scale for imshow window
    scale = 25

    def __init__(self, serial_number, exp_time=60000.0):
        self.serial = serial_number
        self.camera = self.open_cam()
        self.converter = self.create_converter()
        self.camera.ExposureTime.SetValue(exp_time)

    def open_cam(self):
        info = pylon.DeviceInfo()
        info.SetSerialNumber(self.serial)
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(info))
        camera.Open()
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        return camera

    def create_converter(self):
        converter = pylon.ImageFormatConverter()
        converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        return converter

    def grabbing_cam(self):
        grab_result = self.camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
        if grab_result.GrabSucceeded():
            img_original = self.converter.Convert(grab_result)
            img_original = img_original.GetArray()
            img_width = int(img_original.shape[1] * self.scale / 100)
            img_height = int(img_original.shape[0] * self.scale / 100)
            img_dim = (img_width, img_height)
            img_resized = cv2.resize(img_original, img_dim, interpolation = cv2.INTER_AREA)
            return img_original, img_resized
        else:
            return None,None

    def cam_set_value(self, a):
        self.camera.ExposureTime.SetValue(a)

def imgResize(img, scale):
    img_width = int(img.shape[1] * scale)
    img_height = int(img.shape[0] * scale)
    img_dim = (img_width, img_height)
    img_resized = cv2.resize(img, img_dim, interpolation=cv2.INTER_AREA)
    return img_resized

win_name = 'Trackbars'
cv2.namedWindow(win_name)
cv2.resizeWindow(win_name, 640, 480)
cv2.createTrackbar('blur1', win_name, 13, 20, empty)
cv2.createTrackbar('blur2', win_name, 0, 1000, empty)
cv2.createTrackbar('thresh1', win_name, 0, 1000, empty)
cv2.createTrackbar('thresh2', win_name, 0, 15, empty)
cv2.createTrackbar('kernel', win_name, 0, 20, empty)

if __name__ == "__main__":
    # Folder path to save image taken (date taken)
    img_path = "img_01072022\\tes"
    if not os.path.exists(img_path):
        os.mkdir(img_path)

    # Camera serial number can be found in the device label S/N
    # cam = Camera("40049922") #Grayscale
    cam = Camera("23643314") #RGB

    num = 1
    i = 0
    while True:
        ori2, resize2 = cam.grabbing_cam()
        if ori2 is None or resize2 is None:
            continue

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

        # kernal_scratch = np.ones((0, 0), np.uint8)
        kernal_dot = np.ones((kernel, kernel), np.uint8)

        img_ori = ori2.copy()
        # img_ori = cv2.imread('img_08062022/multi45deg/1all.jpg')
        img_ori = imgResize(img_ori, 0.35)
        img = img_ori.copy()
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # img_blur_scratch = cv2.GaussianBlur(img_gray, (13, 13), 0)
        img_blur_dot = cv2.GaussianBlur(img_gray, (blur1, blur1), blur2)

        # adapt_thresh_scratch = cv2.adaptiveThreshold(img_blur_scratch, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #                                              cv2.THRESH_BINARY, 3, 0)
        adapt_thresh_dot = cv2.adaptiveThreshold(img_blur_dot, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                     cv2.THRESH_BINARY, thresh1, thresh2)

        # moprh_img_scratch = cv2.erode(adapt_thresh_scratch, kernal_scratch, iterations=1)
        moprh_img_dot = cv2.erode(adapt_thresh_dot, kernal_dot, iterations=1)

        # edged = cv2.Canny(moprh_img_scratch, 75, 100)

        # test
        se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 2))
        # bg1 = cv2.morphologyEx(adapt_thresh_scratch, cv2.MORPH_ERODE, se)
        bg2 = cv2.morphologyEx(adapt_thresh_dot, cv2.MORPH_ERODE, se)
        # out_gray1 = cv2.divide(adapt_thresh_scratch, bg1, scale=255)
        out_gray2 = cv2.divide(adapt_thresh_dot, bg2, scale=255)
        # out_binary1 = cv2.threshold(out_gray1, 0, 255, cv2.THRESH_OTSU)[1]
        out_binary2 = cv2.threshold(out_gray2, 0, 255, cv2.THRESH_OTSU)[1]

        ## For detect contours
        # contours1, hierarchy1 = cv2.findContours(adapt_thresh_scratch, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contours2, hierarchy2 = cv2.findContours(adapt_thresh_dot, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # draw contours
        # for cnt in contours1:
        #     cnt_area = cv2.contourArea(cnt)
        #     if 5 < cnt_area < 50:
        #         cv2.drawContours(img, cnt, -1, (0, 255, 0), 2, cv2.LINE_AA)
        #         M = cv2.moments(cnt)
        #         cX = int(M["m10"] / M["m00"])
        #         cY = int(M["m01"] / M["m00"])
        #         cv2.circle(img, (cX, cY), 1, (0, 0, 255), -1)
        #         text = f"[{cX} , {cY}]"
        #         cv2.putText(img, text, (cX + 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        for cnt in contours2:
            cnt_area = cv2.contourArea(cnt)
            if 5 < cnt_area < 50:
                cv2.drawContours(img, cnt, -1, (0, 255, 0), 2, cv2.LINE_AA)
                M = cv2.moments(cnt)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.circle(img, (cX, cY), 1, (0, 0, 255), -1)
                text = f"[{cX} , {cY}]"
                cv2.putText(img, text, (cX + 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow(f'result cam2', img)
        # cv2.imshow('denoised_scratch', out_binary1)
        cv2.imshow('denoised_dot', out_binary2)
        k = cv2.waitKey(1)
        if k == ord("s") or k == ord("S"):
            cv2.imwrite(f'{img_path}\\{num}.jpg', ori2)
            print(f"{num}.jpg image captured!")
            num += 1
        if k == 27:
            print(f"Finished capturing image!")
            break

