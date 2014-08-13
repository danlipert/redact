import cv2
import numpy

def detectFaces(image):
    """
    Returns list of bounding boxes (x, y, w, h) containing human faces.
    
    image -- input image to be detected
    """
    #setup parameters
    detector_scale_factor = 1.1
    detector_minimum_neighbors = 3 
    detector_minimum_size_square = 50
    detector_maximum_size_square = 400
    detector_path = 'data/haarcascade_frontalface_alt_tree.xml'
    cascade = cv2.CascadeClassifier(detector_path)
    #convert image to numpy array
    image = numpy.array(image)
    boxes = cascade.detectMultiScale(image, scaleFactor=detector_scale_factor, minNeighbors=detector_minimum_neighbors, minSize=(detector_minimum_size_square, detector_minimum_size_square), maxSize=(detector_maximum_size_square, detector_maximum_size_square), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
    return boxes
    
def muxBoxes(boxes, minSize=(0,0)):
    """
    Returns list of bounding boxes (x, y, w, h) where overlapping boxes are combined.
    
    boxes -- list of boxes to mux
    minSize -- boxes below this size (both width and height) will be discarded
    """
    
    return boxes
