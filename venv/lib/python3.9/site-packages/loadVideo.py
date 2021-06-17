import cv2
import numpy as np
from imutils.video import VideoStream


class fromCamera:
    '''
        Loads from camera from an external source
    '''
    def __init__(self, src=0, res=None):
        self.src = src
        self.res = res
        self.capture = cv2.VideoCapture(self.src)
        self.ret = False
        self.frame = None

        if self.res is not None:
            setResolution(self.res)

    
    def setResolution(self, res):
        self.res = res
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.res[0])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.res[1])
    
    def readFrame(self):
        ret, frame = self.capture.read()
        self.ret = ret
        self.frame = frame



class fromVideo:
    '''
        Loads from a video path into the camera
    '''

    def __init__(self, path=None, res=None):
        self.path = path
        self.res = res
        self.capture = cv2.VideoCapture(self.path)
        self.ret = False
        self.frame = None

        if self.res is not None:
            setResolution(self.res)

    
    def setResolution(self, res):
        self.res = res
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.res[0])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.res[1])
    
    def readFrame(self):
        ret, frame = self.capture.read()
        self.ret = ret
        self.frame = frame


class fromPiCamera:
    '''
        Loads the video source from Pi Camera
    '''
    def __init__(self, res=None):
        self.res = res
        self.frame = None

        if self.res is not None:
            self.capture = VideoStream(usePiCamera = True, resolution = (self.res[0], self.res[1])).start()
        else:
            self.capture = VideoStream(usePiCamera = True).start()
    
    def readFrame(self):
        self.frame = self.capture.read()





