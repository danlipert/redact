from PIL import ImageOps

def adjustImage(image):
    """
    Returns image adjusted for facial detection.
    
    image -- input image to be adjusted
    type -- string representing adjustment type
    """
    
    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image)
    return image


