import cv2
from util import image
from hyperlayer import haar, morphology
from event import event
from render import blur
import sys
from datetime import timedelta
import json

def show_usage():
	print 'Please enter the path of the video to be redacted as the 1st argument'
	print 'Please enter the blur type as the 2nd argument'
	print 'Supported test types: motion'
	print 'Usage:'
	print 'python redact.py video.mp4 motion'

def parse_test_type(arg):
	"""
	Option to allow different test types
	Currently supported: PCA LDA
	"""
	if arg != 'PCA' and arg != 'LDA':
		show_usage()
		raise Exception('ERROR: Could not parse test type "%s"' % arg)
		exit()
	else:
		return arg

def extract_capture_metadata(cap):
    '''
    extracts metadata on framerate, resolution, codec, and length from opencv video capture object
    '''
    cv_fourcc_code = cap.get(6)
    FRAME_RATE = cap.get(5)
    FRAME_HEIGHT = cap.get(4)
    FRAME_WIDTH = cap.get(3)
    VIDEO_LENGTH = timedelta(seconds=(cap.get(7) * (1 / FRAME_RATE)))
    return (cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH)

def pickleHyperframes(hyperframes, sourceFilename):
    outputFilename = '%s-hf.json' % sourceFilename
    print hyperframes
    with open(outputFilename, 'w') as outfile:
        json.dump(hyperframes, outfile)
    print 'Wrote Hyperframe JSON'

def redactVideo(video, blurType, videoPath):
    """
    Redacts all faces in video.
    
    video -- the source video to be redacted.
    blurType -- the type of burring effect to use.
    """
    
    fourcc = cv2.cv.CV_FOURCC(*'mp4v')
    cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH = extract_capture_metadata(video)
    writer = cv2.VideoWriter('output.mov', fourcc, FRAME_RATE, (int(FRAME_WIDTH), int(FRAME_HEIGHT)), True)
    
    hyperframes = []
    cascades = []
    detector_paths = ['data/haarcascade_frontalface_alt_tree.xml',
        'data/haarcascade_frontalface_default.xml',
        'data/haarcascade_upperbody.xml']
    for detector_path in detector_paths:
        cascade = cv2.CascadeClassifier(detector_path)
        cascades.append(cascade)

    ret = True
    print 'creating hyperframes...'
    while(ret):
        frame_count = video.get(1)
        timestamp = timedelta(seconds=(video.get(0) / 1000))
        sys.stdout.write("Processed {0} of {1}\r".format(timestamp, VIDEO_LENGTH))
        sys.stdout.flush()
        
        ret, frame = video.read()

        if ret==True:
            adjustedFrame = image.adjustImage(frame)
            faces = haar.detectFaces(adjustedFrame, cascades)
            muxedFaces = haar.muxBoxes(faces)
            #convert from np array to python list
            if len(muxedFaces) > 0:
                finalFaces = []
                for face in muxedFaces:
                    finalFaces.append(face.tolist())
                muxedFaces = finalFaces
            hyperframe = {'frameNumber':frame_count, 'faces':muxedFaces}
            hyperframes.append(hyperframe)
    print 'hyperframe created'
    hyperframes = morphology.erode(hyperframes)
    
    #store for re-use
    pickleHyperframes(hyperframes, videoPath)
    
    events = event.generateEvents(hyperframes)
    blur.blurVideo(writer, events, video, blurType)

def redactVideoFromHyperframes(video, blurType, videoPath, hyperframes):
    """
    Redacts all faces in video.
    
    video -- the source video to be redacted.
    blurType -- the type of burring effect to use.
    """
    
    fourcc = cv2.cv.CV_FOURCC(*'mp4v')
    cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH = extract_capture_metadata(video)
    writer = cv2.VideoWriter('output.mov', fourcc, FRAME_RATE, (int(FRAME_WIDTH), int(FRAME_HEIGHT)), True)
    
    events = event.generateEvents(hyperframes)
    blur.blurVideo(writer, events, video, blurType)


def loadVideo(videoPath):
    """
    Loads video for processing.
    
    videoPath -- the source video's path to be redacted.
    """
    
    video = cv2.VideoCapture(videoPath)
    
    return video

def loadHyperframesFromJson(jsonPath):
    jsonData = open(jsonPath)
    hyperframes = json.load(jsonData)
    return hyperframes

# main
try:
    videoPath = sys.argv[1]
except Exception as e:
    show_usage()
    exit()

blurType = sys.argv[2]
if blurType != 'motion':
    show_usage()
    raise Exception('ERROR: Could not parse blur type "%s"' % arg)
    exit()

try:
    jsonPath = sys.argv[3]
except Exception as e:
    print e
    video = loadVideo(videoPath)
    redactVideo(video, blurType, videoPath)
    exit()

video = loadVideo(videoPath)
hyperframes = loadHyperframesFromJson(jsonPath)
redactVideoFromHyperframes(video, blurType, videoPath, hyperframes)
exit()




