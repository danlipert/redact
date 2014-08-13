from PIL import ImageOps, Image

def adjustImage(image):
    """
    Returns image adjusted for facial detection.
    
    image -- input image to be adjusted
    type -- string representing adjustment type
    """
    image = Image.fromarray(image)
    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image)
    return image


