from pypylon import pylon
import cv2
import os
import numpy as np
from pathlib import Path
from CreateBoundingBoxes import annotate_file


def ImageResize(img, scale):
    img_width = int(img.shape[1] * scale)
    img_height = int(img.shape[0] * scale)
    img_dim = (img_width, img_height)
    img_resized = cv2.resize(img, img_dim, interpolation=cv2.INTER_AREA)
    return img_resized


class Camera:
    def __init__(self, serial_number, exp_time=60000.0):
        # camera serial number can be found in the device label S/N
        self.serial = serial_number
        self.camera = self.OpenCam()
        self.converter = self.CreateConverter()
        self.camera.ExposureTime.SetValue(exp_time)

    # connect to camera serial number and grabbing continuously
    def OpenCam(self):
        info = pylon.DeviceInfo()
        info.SetSerialNumber(self.serial)
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(info))
        camera.Open()
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        return camera

    # converter to opencv bgr format
    def CreateConverter(self):
        converter = pylon.ImageFormatConverter()
        converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        return converter

    # convert grabbing result to opencv format
    def GrabbingCam(self):
        grab_result = self.camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
        if grab_result.GrabSucceeded():
            image = self.converter.Convert(grab_result)
            image = image.GetArray()
            return image

    def StopGrabbing(self):
        self.camera.StopGrabbing()


class Image:
    def __init__(self,directory,filename,scale):
        self.dir = directory
        self.filename = filename
        self.path = f'{self.dir}\\{self.filename}'
        self.scale = scale
        self.img = cv2.imread(self.path)
        self.pts = []


    def ResizeImage(self, img):
        img_width = int(img.shape[1] * self.scale)
        img_height = int(img.shape[0] * self.scale)
        img_dim = (img_width, img_height)
        img_resized = cv2.resize(img, img_dim, interpolation=cv2.INTER_AREA)
        return img_resized


if __name__ == "__main__":
    serial = '40049922'
    # serial = '23643314'
    cam = Camera(serial)  # set camera serial number
    if serial == '40049922':
        path = '15072022\\grayscale'  # set saving directory grayscale-camera
    else:
        path = '15072022\\RGB'  # set saving directory RGB-camera
    Path(path).mkdir(parents=True, exist_ok=True)  # create directory if not exist

    # get file number in directory
    files = os.listdir(path)
    if len(files) == 0:
        num = 1  # if no existing file, start from 0
    else:
        li = [x.split('.')[0] for x in files]
        li = list(map(int, li))
        num = max(li) + 1  # start from biggest number+1

    # define class names
    class_name_list = ['dot', 'scratch', 'blur', 'cloudy', 'dust', 'other']

    while True:
        file = f'{num}.jpg'
        img = cam.GrabbingCam()
        if img is None:
            continue
        img_resize = ImageResize(img,0.4)

        # cv2.imshow(f'Camera {cam.serial}', img)
        cv2.imshow(f'Camera Resize {cam.serial}', img_resize)
        k = cv2.waitKey(1)

        # shortcut to quit windows
        if k == ord('q') or k == ord('Q'):
            print(f"Finished capturing image!")
            cam.StopGrabbing()
            break

        # shortcut to save image
        elif k == ord("s") or k == ord("S"):
            cv2.imwrite(f'{path}\\{num}.jpg', img)
            print(f"{num}.jpg image saved!")
            annotate_file(path, file, classNameList=class_name_list)
            num += 1

    cv2.destroyAllWindows()
