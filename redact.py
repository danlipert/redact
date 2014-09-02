import cv2
from util import image
from hyperlayer import haar, morphology, classes
from event import event
from render import blur
import sys
from datetime import timedelta
import json
import argparse
import numpy
import click
from PIL import Image
from util.image import isHumanColor

def show_usage():
	print 'Please enter the path of the video to be redacted as the 1st argument'
	print 'Please enter the blur type as the 2nd argument'
	print 'Supported test types: motion'
	print 'Usage:'
	print 'python redact.py video.mp4 motion'

def alarm():
    sys.stdout.write('\a')
    sys.stdout.flush()

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

def loadDetectors(FRAME_HEIGHT, FRAME_WIDTH):
    detectors = [
        #face detection on full frame
        classes.Detector(path='data/haarcascade_frontalface_alt.xml', scale_factor=1.1, minimum_neighbors=0, 
        region={'x':0, 'y':0, 'w':FRAME_WIDTH, 'h':FRAME_HEIGHT}),
        #upper body on full frame
        classes.Detector(path='data/haarcascade_upperbody.xml', scale_factor=1.05, minimum_neighbors=2, 
        region={'x':0, 'y':0, 'w':FRAME_WIDTH, 'h':FRAME_HEIGHT}),
        #mouth detection for top of frame
        #profile face detection on full frame
        classes.Detector(path='data/haarcascade_profileface.xml', scale_factor=1.1, minimum_neighbors=0,
        region={'x':0, 'y':0, 'w':FRAME_WIDTH, 'h':FRAME_HEIGHT})]

    '''
    classes.Detector(path='data/haarcascade_mcs_mouth.xml', scale_factor=1.3, minimum_neighbors=0,
    region={'x':0, 'y':0, 'w':FRAME_WIDTH, 'h':100}),
    #eye detection for bottom of frame
    classes.Detector(path='data/haarcascade_eye.xml', scale_factor=1.3, minimum_neighbors=0,
    region={'x':0, 'y':FRAME_HEIGHT-100, 'w':FRAME_WIDTH, 'h':100}),
    #eye detection for left and right side of frame
    classes.Detector(path='data/haarcascade_eye.xml', scale_factor=1.3, minimum_neighbors=0,
    region={'x':0, 'y':0, 'w':100, 'h':FRAME_HEIGHT}),
    classes.Detector(path='data/haarcascade_eye.xml', scale_factor=1.3, minimum_neighbors=0,
    region={'x':FRAME_WIDTH-100, 'y':0, 'w':100, 'h':FRAME_HEIGHT}),
    '''
    
    return detectors


def loadDetectorsForVideo(video):
    fourcc = cv2.cv.CV_FOURCC(*'mp4v')
    cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH = extract_capture_metadata(video)
    return loadDetectors(FRAME_HEIGHT, FRAME_WIDTH)

def redactVideo(video, blurType, videoPath):
    """
    Redacts all faces in video.
    
    video -- the source video to be redacted.
    blurType -- the type of burring effect to use.
    """
    
    outputPath = '%s-haar.mov' % videoPath.split('.')[0]
    
    print '%s applied to %s -> %s' % (blurType, videoPath, outputPath)
    
    fourcc = cv2.cv.CV_FOURCC(*'mp4v')
    cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH = extract_capture_metadata(video)
    writer = cv2.VideoWriter(outputPath, fourcc, FRAME_RATE, (int(FRAME_WIDTH), int(FRAME_HEIGHT)), True)
    
    hyperframes = []
    cascades = []

    detectors = loadDetectorsForVideo(video)
    
    for detector in detectors:
        print 'loading %s' % detector.path
        cascade = cv2.CascadeClassifier(detector.path)
        detector.cascade = cascade

    ret = True
    while(ret):
        frame_count = video.get(1)
        timestamp = timedelta(seconds=(video.get(0) / 1000))
        sys.stdout.write("Processed {0} of {1}\r".format(timestamp, VIDEO_LENGTH))
        sys.stdout.flush()
        
        ret, frame = video.read()

        if ret==True:
            adjustedFrame = image.adjustImage(frame)
            faces = haar.detectFaces(adjustedFrame, detectors)
            muxedFaces = haar.muxBoxes(faces)
            #convert from np array to python list
            if len(muxedFaces) > 0:
                finalFaces = []
                for face in muxedFaces:
                    if type(face) is tuple:
                        finalFaces.append(list(face))
                    elif type(face) is list and len(face) is 1:
                        finalFaces.append(face[0])
                    elif type(face) is list:
                        finalFaces.append(face)
                    else:
                        finalFaces.append(face.tolist())
                muxedFaces = finalFaces
            hyperframe = {'frameNumber':frame_count, 'faces':muxedFaces}
            hyperframes.append(hyperframe)

    #hyperframes = morphology.erode(hyperframes)
    
    #store for re-use
    pickleHyperframes(hyperframes, videoPath)
    
    events = event.generateSimpleEvents(hyperframes)
    spreadAllFacesOnEvents(10, events)

    if blurType == 'boxes':
        blur.boxVideo(writer, events, video)
    else:
        blur.blurVideo(writer, events, video)



def redactVideoFromHyperframes(video, blurType, videoPath, hyperframes):
    """
    Redacts all faces in video.
    
    video -- the source video to be redacted.
    blurType -- the type of burring effect to use.
    """
    
    outputPath = '%s-haar.mov' % videoPath.split('.')[0]
    
    fourcc = cv2.cv.CV_FOURCC(*'mp4v')
    cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH = extract_capture_metadata(video)
    writer = cv2.VideoWriter(outputPath, fourcc, FRAME_RATE, (int(FRAME_WIDTH), int(FRAME_HEIGHT)), True)
    
    events = event.generateEvents(hyperframes)
    if blurType == 'boxes':
        blur.boxVideoMob(writer, events, video)
    else:
        blur.blurVideo(writer, events, video)


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

def renderAdjustedVideo(path):
    video = loadVideo(path)
    outputPath = '%s-adjusted.mov' % path.split('.')[0]
    fourcc = cv2.cv.CV_FOURCC(*'mp4v')
    cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH = extract_capture_metadata(video)
    writer = cv2.VideoWriter(outputPath, fourcc, FRAME_RATE, (int(FRAME_WIDTH), int(FRAME_HEIGHT)), True)
    ret = True

    while(ret):
        frame_count = video.get(1)
        timestamp = timedelta(seconds=(video.get(0) / 1000))
        sys.stdout.write("Processed {0} of {1}\r".format(timestamp, VIDEO_LENGTH))
        sys.stdout.flush()

        ret, frame = video.read()
        if ret:
            adjustedFrame = image.adjustImage(frame)
            writer.write(numpy.array(adjustedFrame))
        else:
            break
    writer.release()

def testSimpleHaar(path):
    video = loadVideo(path)
    fourcc = cv2.cv.CV_FOURCC(*'mp4v')
    cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH = extract_capture_metadata(video)
    detectors = loadDetectorsForVideo(video)
    
    for detector in detectors:
        print 'loading %s' % detector.path
        cascade = cv2.CascadeClassifier(detector.path)
        detector.cascade = cascade
    
    hyperframes = []
    
    ret = True
    while(ret):
        frame_count = video.get(1)
        timestamp = timedelta(seconds=(video.get(0) / 1000))
        sys.stdout.write("Processed {0} of {1}\r".format(timestamp, VIDEO_LENGTH))
        sys.stdout.flush()
        
        ret, frame = video.read()

        if ret==True:
            adjustedFrame = image.adjustImage(frame)
            faces = haar.detectFaces(adjustedFrame, detectors)
            muxedFaces = haar.muxBoxes(faces)
            #convert from np array to python list
            if len(muxedFaces) > 0:
                finalFaces = []
                for face in muxedFaces:
                    if type(face) is tuple:
                        finalFaces.append(list(face))
                    elif type(face) is list and len(face) is 1:
                        finalFaces.append(face[0])
                    elif type(face) is list:
                        finalFaces.append(face)
                    else:
                        finalFaces.append(face.tolist())
                muxedFaces = finalFaces
            hyperframe = {'frameNumber':frame_count, 'faces':muxedFaces}
            hyperframes.append(hyperframe)
    
    events = []
    
    outputPath = '%s-haartest.mov' % path.split('.')[0]
    
    fourcc = cv2.cv.CV_FOURCC(*'mp4v')
    cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH = extract_capture_metadata(video)
    writer = cv2.VideoWriter(outputPath, fourcc, FRAME_RATE, (int(FRAME_WIDTH), int(FRAME_HEIGHT)), True)
    
    for hyperframe in hyperframes:
        events.append({'faces':hyperframe['faces'], 'type':'move'})
    
    blur.boxVideo(writer, events, video)
    alarm()

def chopFrames(path):
    video = loadVideo(path)
    cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH = extract_capture_metadata(video)
    ret = True
    while(ret):
        frame_count = video.get(1)
        timestamp = timedelta(seconds=(video.get(0) / 1000))
        sys.stdout.write("Processed {0} of {1}\r".format(timestamp, VIDEO_LENGTH))
        sys.stdout.flush()
        
        ret, frame = video.read()

        if ret==True:
            cv2.imwrite('chopped/%s-%i.jpg' % (path, frame_count), frame)

def haarImage(path):
    frame = cv2.imread(path)
    detectors = loadDetectors(frame.shape[0], frame.shape[1])
    for detector in detectors:
        print 'loading %s' % detector.path
        cascade = cv2.CascadeClassifier(detector.path)
        detector.cascade = cascade
    faces = haar.detectFaces(frame, detectors)
    for face in faces:
        eachFaceRect = face
        image = Image.fromarray(numpy.uint8(frame))
        croppedImage = image.crop((eachFaceRect[0], eachFaceRect[1], eachFaceRect[0]+eachFaceRect[2], eachFaceRect[1]+eachFaceRect[3]))
        if isHumanColor(croppedImage):
            cv2.rectangle(frame, (eachFaceRect[0], eachFaceRect[1]), (eachFaceRect[0] + eachFaceRect[2], eachFaceRect[1]+eachFaceRect[3]), (255,100,100), thickness = 1, lineType=8, shift=0)
    cv2.imshow('haar', frame)
    while(1):
        cv2.waitKey(25)

def testEventSpread(path):
    from event.event import spreadAllFacesOnEvents
    hyperframes = loadHyperframesFromJson(path)
    events = event.generateSimpleEvents(hyperframes)
    spreadAllFacesOnEvents(30, events)
    print 'DONE SPREADING'
    print events


@click.command()
@click.argument('path')
@click.argument('blurtype', default='motion')
@click.option('--jsonpath', help='Json Hyperframe data for import.')
@click.option('--rendertype', default='boxes', help='Render style.')
def redact(path, blurtype, jsonpath, rendertype):
    if rendertype == 'adjusted':
        renderAdjustedVideo(path)
    elif rendertype == 'haartest':
        testSimpleHaar(path)
    elif rendertype == 'chopframes':
        chopFrames(path)
    elif rendertype == 'haarimage':
        haarImage(path)
    elif rendertype == 'testeventspread':
        testEventSpread(path)
    elif jsonpath:
        video = loadVideo(path)
        hyperframes = loadHyperframesFromJson(jsonpath)
        redactVideoFromHyperframes(video, blurtype, path, hyperframes)
    elif blurtype != 'motion' and blurtype != 'boxes':
        show_usage()
        raise Exception('ERROR: Could not parse blur type "%s"' % arg)
    else:
        video = loadVideo(path)
        redactVideo(video, blurtype, path)
    exit()

if __name__ == '__main__':
    redact()







