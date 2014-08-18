import cv2
import numpy

def detectFaces(image, cascades):
    """
    Returns list of bounding boxes (x, y, w, h) containing human faces.
    
    image -- input image to be detected
    """
    #setup parameters
    detector_scale_factor = 1.3
    detector_minimum_neighbors = 1
    detector_minimum_size_square = 20
    detector_maximum_size_square = 400
    #convert image to numpy array
    image = numpy.array(image)
    all_boxes = []
    for cascade in cascades:
        boxes = cascade.detectMultiScale(image, scaleFactor=detector_scale_factor, minNeighbors=detector_minimum_neighbors, minSize=(detector_minimum_size_square, detector_minimum_size_square), maxSize=(detector_maximum_size_square, detector_maximum_size_square), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
        if len(boxes) > 0:
            print '%s faces found in frame' % len(boxes)
            all_boxes.append(boxes)
    return boxes

def muxBoxes(boxes, minSize=(0,0)):
    """
    Returns list of bounding boxes (x, y, w, h) where overlapping boxes are combined.
    
    boxes -- list of boxes to mux
    minSize -- boxes below this size (both width and height) will be discarded
    """
    
    return boxes
