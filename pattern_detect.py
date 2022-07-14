from pypylon import pylon
import cv2
import os
import numpy as np
from pathlib import Path

def empty(a):
    pass

class Camera:
    # scale for imshow window
    scale = 45

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

def adaptive_threshold(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    adapt = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, 101, 3)
    return adapt

win_name = 'Trackbars'
cv2.namedWindow(win_name)
cv2.resizeWindow(win_name, 640, 480)
cv2.createTrackbar('blur1', win_name, 0, 20, empty)
cv2.createTrackbar('blur2', win_name, 0, 100, empty)
cv2.createTrackbar('thresh1', win_name, 100, 100, empty)
cv2.createTrackbar('thresh2', win_name, 3, 15, empty)
cv2.createTrackbar('kernel', win_name, 0, 20, empty)

if __name__ == "__main__":
    # Folder path to save image taken (date taken)
    path = "pattern"
    Path(path).mkdir(parents=True, exist_ok=True)  # create directory if not exist
    if not os.path.exists(path):
        os.mkdir(path)

    # Camera serial number can be found in the device label S/N
    cam = Camera("40049922",320.0) #Grayscale
    # cam = Camera("23643314") #RGB

    files = os.listdir(path)
    if len(files) == 0:
        num = 1  # if no existing file, start from 0
    else:
        li = [x.split('.')[0] for x in files]
        li = list(map(int, li))
        num = max(li) + 1  # start from biggest number+1

    while True:
        ori, resize = cam.grabbing_cam()
        if ori is None or resize is None:
            continue

        # get trackbar value
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


        img = ori
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (blur1, blur1), blur2)
        adapt_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, thresh1, thresh2)

        # for display
        img_display = imgResize(img.copy(),0.4)
        adapt_thresh_display = imgResize(adapt_thresh.copy(),0.4)
        cv2.imshow('Camera', img_display)
        cv2.imshow(f'Result', adapt_thresh_display)

        # morph_img = cv2.erode(adapt_thresh, kernal, iterations=1)
        # cv2.imshow('erode', morph_img)
        # edged = cv2.Canny(morph_img, 75, 100)
        # cv2.imshow('erode', edged)


        k = cv2.waitKey(1)
        if k == ord("s") or k == ord("S"):
            cv2.imwrite(f'{path}\\{num}.jpg', img)
            cv2.imwrite(f'{path}\\{num}_result.jpg', adapt_thresh)
            print(f"{num}.jpg image captured!")
            cv2.destroyWindow(f'Camera')
            cv2.destroyWindow(f'Result')
            new_img = cv2.imread(f'{path}\\{num}.jpg')
            new_adapt = adaptive_threshold(new_img)

            cv2.imshow(f'{num}.jpg', imgResize(new_img,0.4))
            cv2.imshow(f'{num}.jpg Result', imgResize(new_adapt, 0.4))
            k = cv2.waitKey(0)
            if k == ord('d'):
                cv2.destroyWindow(f'{num}.jpg')
                cv2.destroyWindow(f'{num}.jpg Result')
            num += 1

        if k == 27 or k == ord('q') or k == ord('Q'):
            print(f"Finished capturing image!")
            break

