from enum import Enum
from pypylon import pylon
import cv2
import os

class CameraPos(Enum):
    first = "first"
    second = "second"
    SIDE_120 = "120degree"
    SIDE_240 = "240degree"

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



class CameraPair:
    img_path = "glass_img/"

    def __init__(self, serial_left, serial_right, cam_pos:CameraPos):
        self.left_camera = Camera(serial_left)
        self.right_camera = Camera(serial_right)
        self.camera_position = cam_pos.value
        self.left_original = None
        self.right_original = None

    def grabbing_pair_cam(self):
        left_original, left_resized = self.left_camera.grabbing_cam()
        right_original, right_resized = self.right_camera.grabbing_cam()
        self.left_original, self.right_original = left_original, right_original
        return left_original, left_resized, right_original, right_resized

    def save_image(self,num):
        cv2.imwrite(f'{CameraPair.img_path}{self.camera_position}/image_L_{num}.jpg', self.left_original)
        cv2.imwrite(f'{CameraPair.img_path}{self.camera_position}/image_R_{num}.jpg', self.right_original)
        print(f"Image {num} saved!")


camera_dict = {"1":["23643314", "21819175", CameraPos.first],
               "2":["40156421", "40156409", CameraPos.second],
               "3":["40118988", "40118977", CameraPos.SIDE_120],
               "4":["40003776", "40070109", CameraPos.SIDE_240]}

if __name__ == "__main__":
    # Folder path to save image taken (date taken)
    img_path = "img_19052022\\blue"
    if not os.path.exists(img_path):
        os.mkdir(img_path)

    # Camera serial number can be found in the device label S/N
    # cam = Camera("23643314")
    cam = Camera("40049922")

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

