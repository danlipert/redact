from PIL import ImageOps, Image
import cv2
import numpy

def adjustImage(image):
    """
    Returns image adjusted for facial detection.
    
    image -- input image to be adjusted
    type -- string representing adjustment type
    """
    image = Image.fromarray(image)
    #brighten
    image = image.point(lambda p: p * 1.2)
    image = ImageOps.grayscale(image)
    image = ImageOps.equalize(image)
    #image = ImageOps.autocontrast(image)

    image = ImageOps.colorize(image, (0,0,0), (255,255,255))
    return image

def isHumanColor(image):
    #convert image to HSV
    image = numpy.array(image)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #create H ranges
    h_low = 320
    h_high = 355
    h_low2 = 400
    h_high2 = 400
    #calculate average
    h_values = []
    #sample the middle of the image
    height = image.shape[0]
    width = image.shape[1]
    crop_hsv = hsv[height/2-3:height/2+3, width/2-3:width/2+3]
    for eachLine in crop_hsv:
        for eachPixel in eachLine:
            h_values.append(eachPixel[0])
    h_average = sum(h_values)/float(len(h_values))
    #correct for byte crushing in HSV space -> opencv cuts H in half to fit in 8 bits, i.e. 360 > 255, so record 360 as 180
    #so we double the average to be a normal H cause who cares
    h_average = h_average * 2
    print h_average
    #test
    if h_high > h_average > h_low or h_high2 > h_average > h_low2:
        return True
    else:
        return False

