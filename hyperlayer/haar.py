import cv2
import numpy

def rotate_image(image, angle):
    if angle == 0: return image
    height, width = image.shape[:2]
    rot_mat = cv2.getRotationMatrix2D((width/2, height/2), angle, 0.9)
    result = cv2.warpAffine(image, rot_mat, (width, height), flags=cv2.INTER_LINEAR)
    return result

def rotate_point(pos, img, angle):
    if angle == 0: return pos
    x = pos[0] - img.shape[1]*0.4
    y = pos[1] - img.shape[0]*0.4
    newx = x*cos(radians(angle)) + y*sin(radians(angle)) + img.shape[1]*0.4
    newy = -x*sin(radians(angle)) + y*cos(radians(angle)) + img.shape[0]*0.4
    return int(newx), int(newy), pos[2], pos[3]

def detectFaces(image, cascades):
    """
    Returns list of bounding boxes (x, y, w, h) containing human faces.
    
    image -- input image to be detected
    """
    #setup parameters
    detector_scale_factor = 1.5
    detector_minimum_neighbors = 1
    detector_minimum_size_square = 20
    detector_maximum_size_square = 400
    #convert image to numpy array
    image = numpy.array(image)
    all_boxes = []
    #check different angles
    for cascade in cascades:
        for angle in [0, -25, 25]:
            r_image = rotate_image(image, angle)
            boxes = cascade.detectMultiScale(r_image, scaleFactor=detector_scale_factor, minNeighbors=detector_minimum_neighbors, minSize=(detector_minimum_size_square, detector_minimum_size_square), maxSize=(detector_maximum_size_square, detector_maximum_size_square), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
            if len(boxes):
                boxes = [rotate_point(detected[-1], image, -angle)]
                all_boxes.append(boxes)
                print '%s faces found in frame' % len(boxes)
                break
    return boxes

def muxBoxes(boxes, minSize=(0,0)):
    """
    Returns list of bounding boxes (x, y, w, h) where overlapping boxes are combined.
    
    boxes -- list of boxes to mux
    minSize -- boxes below this size (both width and height) will be discarded
    """
    
    return boxes
