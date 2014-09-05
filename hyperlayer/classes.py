import math
import numpy
from event.event import centerOfBox
import cv2
import random
from PIL import Image, ImageFilter
from util.image import isHumanColor

def closestBoxToPoint(point, candidates):
    """
    Returns the closest bounding box out of the candidates to the provided box
    
    point -- point to find the closest to
    candidates -- array of boxes to compare to
    """
    
    #first guess that its the first one (why not?)
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        return None
    
    boxCenter = point
    closest = candidates[0]
    #some large distance to start
    kingDistance = 99999999999
    for i, eachCandidate in enumerate(candidates):
        if i == 0:
            #already handled
            continue
        candidateCenter = centerOfBox(eachCandidate)
        dist = numpy.linalg.norm(point-candidateCenter)
        if dist < kingDistance:
            kingDistance = dist
            closest = eachCandidate
    
    return closest

class Detector:
	"""
	A haar cascade classifier with associated settings
	
	path -- local file path of detector
	region -- x,y,w,h for running the classifier within a specific region
	minimum_size_square -- minimum size of detection bounds square
	maximum_size_square -- maximum size of detection bounds square
	scale_factor -- multiplier to scale by when interpolating cascade size between min and max
	minimum_neighbors -- how many nearby results should be found to count as a detection
	cascade -- OpenCV Haar Cascade
	"""
	
	def __init__(self, path=None, region={'x':0, 'y':0, 'w':0, 'h':0}, minimum_size_square=40, maximum_size_square=200, scale_factor=1.3, minimum_neighbors=3, cascade=None):
		self.path = path
		self.region = region
		self.minimum_size_square = minimum_size_square
		self.maximum_size_square = maximum_size_square
		self.scale_factor = scale_factor
		self.minimum_neighbors = minimum_neighbors
		self.cascade = cascade

class Mob:
    """
    A video game-AI style object that controls rendering

    x, y -- center of mob
    target -- current location that the mob is approaching
    velocity -- maximum distance that can be moved
    """

    def __init__(self, x=0, y=0, target=[0,0], velocity=3):
        self.x = x
        self.y = y
        self.target = target
        self.velocity = velocity

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.target == other.target and self.velocity == other.velocity:
            return True
        else:
            return False

    def move(self):
        y0 = self.target[1] - self.y
        x0 = self.target[0] - self.x
        angleToTarget = math.atan2(y0, x0)
        yv = self.velocity * math.sin(angleToTarget)
        xv = self.velocity * math.cos(angleToTarget)
        print 'moving mob at %s angle (%s, %s) -> (%s, %s)' % (math.degrees(angleToTarget), self.x, self.y, self.x+xv, self.y+yv)
        self.x = self.x + xv
        self.y = self.y + yv



class MobManager:
    """
    A manager object to control a set of mobs intelligently
    
    mobs -- array of mob objects
    """
    
    def __init__(self, mobs=[]):
		self.mobs = mobs

    def tick(self, event):
        faces = event['faces']
        #check to see if we need to add a mob
        if len(event['faces']) > len(self.mobs):
            newFace = event['faces'][-1]
            #generate 1 mob per frame
            self.mobs.append(Mob(x=newFace[0], y=newFace[1], target=(newFace[0], newFace[1])))
        
        mobsToRemove = []
        
        for mob in self.mobs:
            #match each mob to target face
            mob.target = closestBoxToPoint([mob.x, mob.y], faces)
            if mob.target == None:
                mobsToRemove.append(mob)
            else:
                faces.remove(mob.target)
                mob.move()
        
        for mob in mobsToRemove:
            #randomly remove mobs...
            if random.randint(0, 10) == 5:
                self.mobs.remove(mob)

    def renderBlur(self, frame):
        mobSize = 50
        blurredFrame = frame
        frameImage = Image.fromarray(numpy.uint8(frame))
        for mob in self.mobs:
            eachFaceRect = [int(mob.x-mobSize/2), int(mob.y-mobSize/2), int(mob.x+mobSize/2), int(mob.y+mobSize/2)]
            
            blurX = eachFaceRect[0] - int(eachFaceRect[2])
            blurY = eachFaceRect[1] - int(eachFaceRect[3])
            
            blurXC = eachFaceRect[0] + int(eachFaceRect[2])
            blurYC = eachFaceRect[1] + int(eachFaceRect[3])
            ic = frameImage.crop((blurX, blurY, blurXC, blurYC))
            if isHumanColor(ic):
                for i in range(5):  # with the BLUR filter, you can blur a few times to get the effect you're seeking
                    ic = ic.filter(ImageFilter.BLUR)
                frameImage.paste(ic, (blurX, blurY))
            blurredImage = frameImage

            blurredFrame = numpy.array(blurredImage)
                

        #write frame
        return blurredFrame

    def render(self, frame):
        mobSize = 50
        for mob in self.mobs:
            eachFaceRect = [int(mob.x-mobSize/2), int(mob.y-mobSize/2), int(mob.x+mobSize/2), int(mob.y+mobSize/2)]
            frameImage = Image.fromarray(numpy.uint8(frame))
            croppedImage = frameImage.crop((eachFaceRect[0], eachFaceRect[1], eachFaceRect[0]+eachFaceRect[2], eachFaceRect[1]+eachFaceRect[3]))
            if isHumanColor(croppedImage):
                cv2.rectangle(frame, (eachFaceRect[0], eachFaceRect[1]), (eachFaceRect[0] + eachFaceRect[2], eachFaceRect[1]+eachFaceRect[3]), (255,100,100), thickness = 1, lineType=8, shift=0)


        #write frame
        return frame



