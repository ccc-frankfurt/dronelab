import cv2
from PIL import Image
import numpy as np


def as_bgr(img_path):
    '''
    Loads Imge as CV2 BGR format (numpy array as of OpenCV 4)
    '''
    img = cv2.imread(img_path)
    return img

def as_rgb(img_path):
    '''
    Loads Image as RGB format using pillow

    Return a numpy array
    '''

    # NOTE: As this uses pillow format, PNG is loaded with RGBA format by default
    img = Image.open(img_path)
    arr = np.array(img)
    return arr




