from enum import Enum
from pypylon import pylon
import cv2
import os


class Camera:
    # scale for imshow window
    scale = 25

    def __init__(self, serial_number):
        self.serial = serial_number
        self.camera = self.open_cam()
        self.converter = self.create_converter()

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



if __name__ == "__main__":
    # Folder path to save image taken (date taken)
    img_path = "img_08062022\\tes"
    if not os.path.exists(img_path):
        os.mkdir(img_path)

    # Camera serial number can be found in the device label S/N
    cam = Camera("23643314")
    # cam = Camera("40049922")

    num = 1
    i = 0
    while True:
        ori2, resize2 = cam.grabbing_cam()
        if ori2 is None or resize2 is None:
            continue

        cv2.imshow(f'result cam2', resize2)
        k = cv2.waitKey(1)
        if k == ord("s") or k == ord("S"):
            cv2.imwrite(f'{img_path}\\{num}.jpg', ori2)
            print(f"{num}.jpg image captured!")
            num += 1
        if k == 27:
            print(f"Finished capturing image!")
            break

