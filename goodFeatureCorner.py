from pypylon import pylon
import cv2
import os
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt


def ImageResize(img, scale):
    img_width = int(img.shape[1] * scale)
    img_height = int(img.shape[0] * scale)
    img_dim = (img_width, img_height)
    img_resized = cv2.resize(img, img_dim, interpolation=cv2.INTER_AREA)
    return img_resized

def MousePoints(event,x,y,flags,params):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(saved_img,(x,y),5,(0,0,255),cv2.FILLED)
        point_list.append([x,y])
        print(point_list)


class Camera:
    def __init__(self, serial_number):
        # camera serial number can be found in the device label S/N
        self.serial = serial_number
        self.camera = self.OpenCam()
        self.converter = self.CreateConverter()

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

    def GetImage(self):
        while True:
            img = self.GrabbingCam()
            if img is None:
                continue

            cv2.imshow(f'Camera {self.serial}', img)
            k = cv2.waitKey(1)

            # shortcut to quit windows
            if k == ord('q') or k == ord('Q'):
                print(f"Finished capturing image!")
                self.StopGrabbing()
                break

            # shortcut to save image
            if k == ord("s") or k == ord("S"):
                cv2.imwrite(f'{path}\\{num}.jpg', img)
                print(f"{num}.jpg image saved!")
                break

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



    def ReadImage(self):
        while True:
            img = self.img
            cv2.imshow(f'{self.filename}',img)
            # cv2.setMouseCallback(f'{self.filename}',self.MousePoints)
            k = cv2.waitKey(0)
            if k == ord('d') or k == ord('D'):
                cv2.destroyWindow(f'{self.filename}')
                break





if __name__ == "__main__":
    cam = Camera("23643314")  # set camera serial number
    path = 'asd\\now'  # set saving directory
    Path(path).mkdir(parents=True, exist_ok=True)  # create directory if not exist

    # get file number in directory
    files = os.listdir(path)
    if len(files) == 0:
        num = 1  # if no existing file, start from 0
    else:
        li = [x.split('.')[0] for x in files]
        li = list(map(int, li))
        num = max(li) + 1  # start from biggest number+1

    file = f'{num}.jpg'


    while True:
        file = f'{num}.jpg'
        cam.GetImage()
        image = Image(path, file, 1)
        image.ReadImage()
        num += 1
        # break

        # img = cam.GrabbingCam()
        # if img is None:
        #     continue
        #
        # cv2.imshow(f'Camera', img)
        #
        # k = cv2.waitKey(1)
        #
        # # shortcut to quit windows
        # if k == ord('q') or k == ord('Q'):
        #     print(f"Finished capturing image!")
        #     break


        # # shortcut to save image
        # if k == ord("s") or k == ord("S"):
        #     point_list=[]
        #     cv2.imwrite(f'{path}\\{num}.jpg', img)
        #     print(f"{num}.jpg image saved!")
        #     cv2.destroyWindow(f'Camera')
        #     saved_img = cv2.imread(f'{path}\\{num}.jpg')
        #     cv2.imshow(f'result {num}.jpg', saved_img)
        #     cv2.setMouseCallback(f'result {num}.jpg', MousePoints)
        #     k = cv2.waitKey(0)
        #     if k == ord('d') or k == ord('D'):
        #         cv2.destroyWindow(f'result {num}.jpg')
        #     num += 1


    cv2.destroyAllWindows()
