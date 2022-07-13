# Teste Capturing image ROI with Python and OpenCV
# 25/01/2017 - Marcelo Cabral 

# import the necessary packages
import argparse
import cv2
import os
import numpy as np
from libraryTools import imageRegionOfInterest

def annotate_file(path, filename, classNumber="0", classNameList=None):
    obj = imageRegionOfInterest(path)

    obj.isSavePoints = True
    obj.pathToSave = path
    obj.classNumber = classNumber
    obj.classNameList = classNameList


    obj.loadImage(filename)

    wait = 10
    # keep looping until the 'q' key is pressed
    while True:

        key = cv2.waitKey(33) & 0xFF
        # if key != 255:
        #    print("Key "+str(key))

        # refresh
        if key == ord("r"):
            print('refresh')
            obj.refresh()

        # save
        elif key == ord("s"):
            print('savePoints')
            obj.savePoints()

        # change Class Number
        elif key >= ord("0") and key <= ord("9"):
            print('change Class to ' + chr(key))
            obj.classNumber = chr(key)
            obj.RefreshSelectedClass()

        # change Class 0  (' key is left side 1 key)
        elif key == ord("`"):
            print('change Class to 0')
            obj.classNumber = "0"
            obj.RefreshSelectedClass()

        # next image or spacebar
        # elif key == ord("n") or key == 32:
        #     print('next image')
        #     obj.savePoints()
        #     index += 1
        #     break
        #
        # # previus image
        # elif key == ord("p"):
        #     print('previus image')
        #     obj.savePoints()
        #     index -= 1
        #     break

        # box to left
        elif key == ord("j"):
            # print('box to left')
            obj.moveLastBox(-1, 0)
        # box to right
        elif key == ord("l"):
            # print('box to right')
            obj.moveLastBox(1, 0)

        # box to up
        elif key == ord("i"):
            # print('box to up')
            obj.moveLastBox(0, -1)
        # box to down
        elif key == ord("k"):
            # print('box to down')
            obj.moveLastBox(0, 1)


        # copy last bounding boxes
        # elif key == ord("c"):
        #     print('copy last bounding boxes')
        #     obj.copyLastBoundingBoxes()
        #
        # # shift last bounding box
        # elif key == ord("x"):
        #     print('shift last bounding box')
        #     obj.shiftLastBoundingBox()


        # quit
        elif key == ord("q") or key == 27 or cv2.getWindowProperty(filename, 1) + wait == -1:
            print('quit')
            if len(obj.points) > 0:
                obj.savePoints()
            cv2.destroyWindow(obj.windowName)
            return

        # elif key == ord('q'):
        #     break

        # wait = wait - 1 if wait > 0 else wait