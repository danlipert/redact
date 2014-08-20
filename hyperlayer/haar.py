import cv2
import numpy
from math import sin, cos, radians

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

def ints_only(box):
    return [int(box[0]), int(box[1]), int(box[2]), int(box[3])]

def correct_cropping_region(box, region):
    return [box[0]+region['x'], box[1]+region['y'], box[2], box[3]]

def detectFaces(image, detectors):
    """
    Returns list of bounding boxes (x, y, w, h) containing human faces.
    
    image -- input image to be detected
    """

    #convert image to numpy array
    image = numpy.array(image)
    all_boxes = []
    #check different angles
    for detector in detectors:
        #crop image for region
        region = detector.region
        crop_img = image[region['y']:region['y']+region['h'], region['x']:region['x']+region['w']] # Crop from x, y, w, h -> 100, 200, 300, 400
        # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
        #setup parameters
        detector_scale_factor = detector.scale_factor
        detector_minimum_neighbors = detector.minimum_neighbors
        detector_minimum_size_square = detector.minimum_size_square
        detector_maximum_size_square = detector.maximum_size_square
        cascade = detector.cascade
        for angle in [0, -25, 25]:
            r_image = rotate_image(crop_img, angle)
            boxes = cascade.detectMultiScale(r_image, scaleFactor=detector_scale_factor, minNeighbors=detector_minimum_neighbors, minSize=(detector_minimum_size_square, detector_minimum_size_square), maxSize=(detector_maximum_size_square, detector_maximum_size_square), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
            #convert to regular array
            boxes = list(boxes)
            if len(boxes):
                for box in boxes:
                    print box
                    box = rotate_point(box, image, -angle)
                    print box
                    box = correct_cropping_region(box, region)
                    box = ints_only(box)
                    all_boxes.append(box)
                    print '%s faces found in frame' % len(all_boxes)
    return all_boxes

def muxBoxes(boxes, minSize=(0,0)):
    """
    Returns list of bounding boxes (x, y, w, h) where overlapping boxes are combined.
    
    boxes -- list of boxes to mux
    minSize -- boxes below this size (both width and height) will be discarded
    """
    
    return boxes
