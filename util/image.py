from PIL import ImageOps, Image
import cv2
def adjustImage(image):
    """
    Returns image adjusted for facial detection.
    
    image -- input image to be adjusted
    type -- string representing adjustment type
    """
    image = Image.fromarray(image)
    image = ImageOps.grayscale(image)
    image = ImageOps.equalize(image)
    #image = ImageOps.autocontrast(image)

    image = ImageOps.colorize(image, (0,0,0), (255,255,255))
    return image


