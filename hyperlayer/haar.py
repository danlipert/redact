import cv2
import numpy
from math import sin, cos, radians
from util.image import isHumanColor

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

def detectFaces(image, colorImage, detectors):
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
                    box = rotate_point(box, image, -angle)

                    box = correct_cropping_region(box, region)
                    box = ints_only(box)
                    croppedFace = colorImage[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
                    try:
                        if isHumanColor(croppedFace):
                            all_boxes.append(box)
                            print '%s faces found in frame' % len(all_boxes)
                    except:
                        pass
    return all_boxes

def boxesOverlap(boxA, boxB):
    '''
    determines if two boxes overlap
    http://stackoverflow.com/questions/306316/determine-if-two-rectangles-overlap-each-other
    '''
    
    ax1 = boxA[0]
    ax2 = boxA[0]+boxA[2]
    ay1 = boxA[1]
    ay2 = boxA[1]+boxA[3]
    
    bx1 = boxB[0]
    bx2 = boxB[0]+boxB[2]
    by1 = boxB[1]
    by2 = boxB[1]+boxB[3]
    
    if ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1:
        return True
    else:
        return False

def combinedBox(boxA, boxB):
    #first lets assign the top box as box A, regardless of how we received them
    if boxA[0] > boxB[0]:
        #swap
        print 'swapped'
        tempBox = boxA
        boxA = boxB
        boxB = tempBox
    
    ax1 = boxA[0]
    ax2 = boxA[0]+boxA[2]
    ay1 = boxA[1]
    ay2 = boxA[1]+boxA[3]
    
    bx1 = boxB[0]
    bx2 = boxB[0]+boxB[2]
    by1 = boxB[1]
    by2 = boxB[1]+boxB[3]
    
    #origin (top left) x is the least of the origin xs of the two boxes
    
    if ax1 < bx1:
        cx1 = ax1
    else:
        cx1 = bx1
    
    #origin y is the least of the origin ys of the two boxes
    
    if ay1 < by1:
        cy1 = ay1
    else:
        cy1 = by1
    
    #opposite x is the greatest of the opposite xs of the two boxes
    
    if ax2 > bx2:
        cx2 = ax2
    else:
        cx2 = bx2
    
    #opposite y is the greatest of the opposite ys of the two boxes
    
    if ay2 > by2:
        cy2 = ay2
    else:
        cy2 = by2
    
    return [cx1, cy1, cx2 - cx1, cy2 - cy1]

def muxBoxes(boxes, minSize=(0,0)):
    """
    Returns list of bounding boxes (x, y, w, h) where overlapping boxes are combined.
    
    boxes -- list of boxes to mux
    minSize -- boxes below this size (both width and height) will be discarded
    """
    return boxes
    '''
    muxedBoxes = []
    
    for eachBox in boxes:
        boxOverlapped = False
        for eachOtherBox in boxes:
            if boxesOverlap(eachBox, eachOtherBox) and eachBox != eachOtherBox:
                boxOverlapped = True
                muxedBoxes.append(combinedBox(eachBox, eachOtherBox))
        if boxOverlapped == False:
            muxedboxes.append(eachBox)

    return boxes
    '''
