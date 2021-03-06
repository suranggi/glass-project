# Capturing image ROI with Python and OpenCV
# 31/01/2017 - Marcelo Cabral 
from __future__ import division #Case python2

import cv2
import os
import sys
import math
import numpy as np
import traceback

try:#Case Windows
    from win32api import GetSystemMetrics
except:#Case Linux
    pass

from copy import copy


class imageRegionOfInterest:

    global mouse_select_area
    Instance = None
    
    def __init__(self, _path):
        self.path = _path
        self.points = []
        self.last_points = []
        self.image = None
        self.originalImage = None
        self.windowName = ""
        self.fileName = ""

        self.scale = 1.0
        self.noScale = False 
        #self.noScale = True

        self.isSavePoints = False
        self.pathToSave = _path
        self.fileNameTxt = ""

        self.classNumber = ""
        self.classNameList = None

        #to MouseSelect
        self.ptInitial = None
        self.ptFinal = None
        self.startedSelectArea = False

        self.colorList = [(0,255,0),
                          (0,0,255),
                          (255,0,0),
                          (25,25,112),
                          (112,0,25),
                          (102,205,170), 
                          (255,255,0), 
                          (153,50,204), 
                          (100,149,237), 
                          (0,255,255), 
                          (184,134,11),
                          (0,155,0),
                          (0,0,155),
                          (155,0,0),
                          (25,0,112),
                          (112,0,0),
                          (102,105,170), 
                          (255,155,0), 
                          (153,50,104), 
                          (100,149,137), 
                          (0,255,155), 
                          (184,34,11)]
        

        imageRegionOfInterest.Instance = self         

    def setTxtFileName(self):
        base_file, ext = os.path.splitext(self.fileName)
        self.fileNameTxt = os.path.join( self.pathToSave, base_file+".txt")

    def loadBoxFromTxt(self):
        self.setTxtFileName()
        points = []
        if (os.path.isfile(self.fileNameTxt)):
            try:
                if (os.stat(self.fileNameTxt).st_size>0):
                    l = np.loadtxt(self.fileNameTxt,dtype=int, delimiter=' ')
                    if len(l.shape)==1:
                        points.append([l[1],l[2],l[1]+l[3],l[2]+l[4],str(l[0])])
                    else:
                        for row in l:
                            if len(row)>=5:
                                points.append([row[1],row[2],row[1]+row[3],row[2]+row[4],str(row[0])])
            except:
                print ("Unexpected error:", sys.exc_info()[0])       

            #print("Inicio",points)
        return points

    def setFileImage(self, _filename):
        self.fileName = _filename

    def loadFromFile(self):
        self.image = cv2.imread(os.path.join(self.path,self.fileName))    
        # self.originalImage = self.image.copy()
        self.originalImage = copy(self.image)

    def extractBox(self, pathName, fileName, point):
        image = self.image[point[1]:point[3],point[0]:point[2]]
        #print(pathName,fileName, point, image.shape)
        if not os.path.exists(pathName):
            os.makedirs(pathName)
        cv2.imwrite(os.path.join(pathName,fileName), image)

    def extractBoxM(self, pathName, fileName, point, margemArea, finalSquad):
        w_m = int(abs(point[3]-point[1])*margemArea)
        h_m = int(abs(point[2]-point[0])*margemArea)
        point[1] = point[1] - w_m
        point[3] = point[3] + w_m
        point[0] = point[0] - h_m
        point[2] = point[2] + h_m

        continuar = True
        while continuar:
            if w_m<h_m:
                point[3] = point[3] + 1
                point[1] = point[1] - 1
                if abs(point[3]-point[1]) >= abs(point[2]-point[0]) or point[3]>=len(self.image) or point[1]<0:
                    continuar = False

            else:
                point[2] = point[2] + 1
                point[0] = point[0] - 1
                if abs(point[3]-point[1]) <= abs(point[2]-point[0]) or point[2]>=len(self.image[0]) or point[0]<0:
                    continuar = False


        if point[3]>=len(self.image):
            point[1] = point[1] + point[3]-len(self.image)-1
            point[3] = len(self.image)-1
        if point[2]>=len(self.image[0]):
            point[0] = point[0] + point[2]-len(self.image[0])-1
            point[2] = len(self.image[0])-1
        if point[1]<0:
            point[3] = point[3] + abs(point[1])
            point[1] = 0
        if point[0]<0:
            point[2] = point[2] + abs(point[0])
            point[0] = 0

        image = self.image[point[1]:point[3],point[0]:point[2]]
        image = cv2.resize(image,(finalSquad, finalSquad), interpolation = cv2.INTER_CUBIC)
        
        if not os.path.exists(pathName):
            os.makedirs(pathName)
        cv2.imwrite(os.path.join(pathName,fileName), image)        

    def loadImage(self, _filename):

        self.setFileImage(_filename)
        self.loadFromFile()

        if (self.windowName != ""):
            cv2.destroyWindow(self.windowName)
        self.windowName = self.fileName


       
        #base_file, ext = os.path.splitext(self.fileName)
        #self.fileNameTxt = os.path.join( self.pathToSave, base_file+".txt") 

        self.points = []
        points = self.loadBoxFromTxt()        
        for point in points:
            #print(point[0],point[1],point[2],point[3],point[4])
            #self.setInicialPoint(point[0],point[1])
            #self.setFinalPoint(point[2],point[3],point[4])
            self.points.append( [(point[0],point[1]), (point[2],point[3]), point[4]] )

        #if (os.path.isfile(self.fileNameTxt)):
        #    try:
        #        if (os.stat(self.fileNameTxt).st_size>0):
        #            l = np.loadtxt(self.fileNameTxt,dtype=int, delimiter=' ')
        #            if len(l.shape)==1:
        #                self.setInicialPoint(l[1],l[2])
        #                self.setFinalPoint(l[1]+l[3],l[2]+l[4],str(l[0]))
        #            else:
        #                for row in l:
        #                    if len(row)==5:
        #                        self.setInicialPoint(row[1],row[2])
        #                        self.setFinalPoint(row[1]+row[3],row[2]+row[4],str(row[0]))
        #    except:
        #        print ("Unexpected error:", sys.exc_info()[0])
            
        self.showImage()

    def showImage(self):
        cv2.namedWindow(self.windowName)
        cv2.setMouseCallback(self.windowName, mouse_select_area)
        cv2.moveWindow(self.windowName, 1, 1)
        self.refresh()

    def textPoint(self, pt1):
        return (pt1[0], pt1[1]-4)


    def loadClassName(self,classNumber):
        className = 'C'+classNumber
        if self.classNameList is not None:
            i = int(classNumber)
            if len(self.classNameList)>i:
               className = self.classNameList[i]

        return className

    def paintClassName(self):
        cv2.rectangle(self.image, (5,5), (120,180), (150,150,150), thickness=-1, lineType=8, shift=0)

        cv2.putText(self.image, "("+str(len(self.points))+") "+self.loadClassName(self.classNumber), (10,20) , cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50,50,50), 1)
        cv2.putText(self.image, f'` or 0:dot', (10,50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255),1)
        cv2.putText(self.image, f'1:scratch', (10,70), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255),1)
        cv2.putText(self.image, f'2:blur', (10,90), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255),1)
        cv2.putText(self.image, f'3:cloudy', (10,110), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255),1)
        cv2.putText(self.image, f'4:dust', (10,130), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255),1)
        cv2.putText(self.image, f'5:other', (10,150), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255),1)
        cv2.putText(self.image, f'right-click:undo', (10,170), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255),1)

    def RefreshSelectedClass(self):
        self.paintClassName()
        cv2.imshow(self.windowName, self.image)

    

    def refresh(self):
        self.image = copy(self.originalImage)
        height, width = self.image.shape[:2]

        if self.noScale:
            final_height = height
            final_width = width 
        
        else:
            try:#Windows
                screen_width = GetSystemMetrics(0)
                screen_height = GetSystemMetrics(1)
            except:#Linux
                info = os.popen("xrandr | grep '*'").read()
                i = info.rindex(' ')
                info = info[:i].strip().split('x')
                screen_width = int(info[0])
                screen_height = int(info[1])
                
            final_height = int(screen_height * 0.9)
            self.scale = final_height/height
            final_width = int(width * self.scale)
            self.image = cv2.resize(self.image,(final_width, final_height), interpolation = cv2.INTER_CUBIC)

        self.paintClassName()

        print("points: ", len(self.points))

        last = len(self.points)
        for pt in self.points:
            last = last - 1
            cor = int(pt[2])

            pt0 = list(pt[0])
            pt0[0] = int(pt[0][0] * self.scale)
            pt0[1] = int(pt[0][1] * self.scale)
            pt1 = list(pt[1])
            pt1[0] = int(pt[1][0] * self.scale)
            pt1[1] = int(pt[1][1] * self.scale)
            
            if last==0:
                thickness = 2
            else:
                thickness = 1

            cv2.putText(self.image,self.loadClassName(pt[2]),self.textPoint(tuple(pt0)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colorList[cor], thickness)
            
            cv2.rectangle(self.image, tuple(pt0), tuple(pt1), self.colorList[cor], 2)

        cv2.imshow(self.windowName, self.image)
            
    def setInicialPoint(self, x, y):
        self.ptInitial = (int(x/self.scale),int(y/self.scale))
        self.startedSelectArea = True

    def showTemporarySelectArea(self, x, y):
        if (self.startedSelectArea):
            img = copy(self.originalImage)

            height, width = img.shape[:2]
            final_width = int(width * self.scale)
            final_height = int(height * self.scale)
            img = cv2.resize(self.image,(final_width, final_height), interpolation = cv2.INTER_CUBIC)

            cor = int(self.classNumber)
            cv2.putText(img,self.loadClassName(self.classNumber),self.textPoint((int(self.ptInitial[0]*self.scale),int(self.ptInitial[1]*self.scale))), cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor,2)
            cv2.rectangle(img, (int(self.ptInitial[0]*self.scale),int(self.ptInitial[1]*self.scale)), (int(x),int(y)), cor, 2)

            cv2.imshow(self.windowName, img)

    def setFinalPoint(self, x, y, classNumber):
        if (self.startedSelectArea):
            if (classNumber==""):
                classNumber=self.classNumber
            self.ptFinal = (int(x/self.scale),int(y/self.scale))
            self.startedSelectArea = False

            if (self.ptInitial[0]<self.ptFinal[0]):
                x1 = self.ptInitial[0]
                x2 = self.ptFinal[0]
            else:
                x2 = self.ptInitial[0]
                x1 = self.ptFinal[0]

            if (self.ptInitial[1]<self.ptFinal[1]):
                y1 = self.ptInitial[1]
                y2 = self.ptFinal[1]
            else:
                y2 = self.ptInitial[1]
                y1 = self.ptFinal[1]

            #print("append ",(x1,y1), (x2,y2))
            self.points.append( [(x1,y1), (x2,y2), classNumber] )
            self.refresh()

    def cancelLastPoint(self):
        #print(self.points)
        if len(self.points) > 0:
            del self.points[-1]
            self.refresh()


    def shift(seq, n=0):
        a = n % len(seq)
        return seq[-a:] + seq[:-a]

    def shiftLastBoundingBox(self):
        if len(self.points) > 1:
            self.points = self.points[-1:] + self.points[:-1]
            self.refresh()

    def moveLastBox(self, x, y):
        if len(self.points) > 0:
            pt1 = list(self.points[-1][0])
            pt2 = list(self.points[-1][1])
            x1 = max(0,pt1[0] + x)
            y1 = max(0,pt1[1] + y)
            height, width = self.image.shape[:2]
            x2 = min(width/self.scale, pt2[0] + x)
            y2 = min(height/self.scale, pt2[1] + y)

            #print(width/self.scale, pt2[0] + x, pt1[0] + x)
            #print(height/self.scale, pt2[1] + y, pt1[1] + y)

            self.points[-1][0] = (x1, y1)
            self.points[-1][1] = (x2, y2)
            self.refresh()

    def copyLastBoundingBoxes(self):
        for pt in self.last_points:
            if not pt in self.points:
                self.points.append(pt)
        print("copyLastBoundingBoxes "+str(len(self.points)))
        self.refresh()

    def savePoints(self):
        l = []
        for pt in self.points:
            l.append([int(pt[2]), pt[0][0], pt[0][1], pt[1][0]-pt[0][0], pt[1][1]-pt[0][1], self.originalImage.shape[1], self.originalImage.shape[0] ])
        
        self.last_points = copy(self.points)
        print(self.fileNameTxt+" saved points "+str(len(self.last_points)))
        np.savetxt(self.fileNameTxt, np.asarray(l),fmt='%d', delimiter =' ',newline='\n')  


def mouse_select_area(event, x, y, flags, param):
    #start select area
    if event == cv2.EVENT_LBUTTONDOWN:
        imageRegionOfInterest.Instance.setInicialPoint(x,y)

    #show temporaty select area
    elif event == cv2.EVENT_MOUSEMOVE:
        imageRegionOfInterest.Instance.showTemporarySelectArea(x,y)

    #acept select area
    elif event == cv2.EVENT_LBUTTONUP:
        imageRegionOfInterest.Instance.setFinalPoint(x,y,"")

    #cancel select area
    elif event == cv2.EVENT_RBUTTONDOWN:
        imageRegionOfInterest.Instance.cancelLastPoint()


