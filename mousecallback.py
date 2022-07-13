import cv2

def mousePoints(event,x,y,flags,params):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img,(x,y),2,(0,0,255),cv2.FILLED)
        pts.append([x,y])
        print(pts)

path = 'asd\\now\\1.jpg'
img = cv2.imread(path)
pts=[]
label =[]

while True:
    if len(pts) != 0 and len(pts) % 2 ==0:
        cv2.rectangle(img,pts[-2],pts[-1],(0,255,0),1)
        x = input('Annotation :')
        label.append(x)
        print(label)
        # print(f'pt1: {pts[-2]}, pt2: {pts[-1]}')

    cv2.imshow('img',img)
    cv2.setMouseCallback('img', mousePoints)
    k = cv2.waitKey(1)
    if k == ord('q') or k == ord('Q'):
        break