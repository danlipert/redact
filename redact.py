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
    '''
    detectors = [
        classes.Detector(path='data/haarcascade_frontalface_alt.xml', scale_factor=1.1, minimum_neighbors=0, 
        region={'x':0, 'y':0, 'w':FRAME_WIDTH, 'h':FRAME_HEIGHT})]
    '''
    border_height = int(FRAME_HEIGHT * 0.15)
    border_width = int(FRAME_WIDTH * 0.15)
    detectors = [
        #face detection on full frame
        classes.Detector(path='data/haarcascade_frontalface_alt.xml', scale_factor=1.05, minimum_neighbors=0, 
        region={'x':0, 'y':0, 'w':FRAME_WIDTH, 'h':FRAME_HEIGHT}),
        #upper body on full frame
        classes.Detector(path='data/haarcascade_upperbody.xml', scale_factor=1.05, minimum_neighbors=2, 
        region={'x':0, 'y':0, 'w':FRAME_WIDTH, 'h':FRAME_HEIGHT}),
        #mouth detection for top of frame
        #profile face detection on full frame
        classes.Detector(path='data/haarcascade_profileface.xml', scale_factor=1.1, minimum_neighbors=2,
        region={'x':0, 'y':0, 'w':FRAME_WIDTH, 'h':FRAME_HEIGHT}),
        classes.Detector(path='data/haarcascade_mcs_mouth.xml', scale_factor=1.2, minimum_neighbors=3,
        region={'x':0, 'y':0, 'w':FRAME_WIDTH, 'h':border_height}),
        #eye detection for bottom of frame
        classes.Detector(path='data/haarcascade_eye.xml', scale_factor=1.2, minimum_neighbors=3,
        region={'x':0, 'y':FRAME_HEIGHT-border_height, 'w':FRAME_WIDTH, 'h':border_height}),
        #eye detection for left and right side of frame
        classes.Detector(path='data/haarcascade_eye.xml', scale_factor=1.2, minimum_neighbors=3,
        region={'x':0, 'y':0, 'w':border_width, 'h':FRAME_HEIGHT}),
        classes.Detector(path='data/haarcascade_eye.xml', scale_factor=1.2, minimum_neighbors=3,
        region={'x':FRAME_WIDTH-border_width, 'y':0, 'w':border_width, 'h':FRAME_HEIGHT})]
    
    
    return detectors


def loadDetectorsForVideo(video):
    fourcc = cv2.cv.CV_FOURCC(*'mp4v')
    cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH = extract_capture_metadata(video)
    return loadDetectors(FRAME_HEIGHT, FRAME_WIDTH)

def redactVideo(video, blurType, videoPath, output):
    """
    Redacts all faces in video.
    
    video -- the source video to be redacted.
    blurType -- the type of burring effect to use.
    """
    if output == None:
        outputPath = '%s-haar.mov' % videoPath.split('.')[0]
    else:
        outputPath = output
    
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
            faces = haar.detectFaces(adjustedFrame, frame, detectors)
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
    event.spreadAllFacesOnEvents(10, events)

    if blurType == 'boxes':
        blur.boxVideo(writer, events, video)
    else:
        blur.blurVideo(writer, events, video)



def redactVideoFromHyperframes(video, blurType, videoPath, hyperframes, output):
    """
    Redacts all faces in video.
    
    video -- the source video to be redacted.
    blurType -- the type of burring effect to use.
    """
    
    print 'redacting...'
    if output == None:
        outputPath = '%s-haar.mov' % videoPath.split('.')[0]
    else:
        outPutPath = output
    
    print 'rendering to %s' % outputPath
    
    fourcc = cv2.cv.CV_FOURCC(*'mp4v')
    cv_fourcc_code, FRAME_RATE, FRAME_HEIGHT, FRAME_WIDTH, VIDEO_LENGTH = extract_capture_metadata(video)
    writer = cv2.VideoWriter(outputPath, fourcc, FRAME_RATE, (int(FRAME_WIDTH), int(FRAME_HEIGHT)), True)
    
    events = event.generateSimpleEvents(hyperframes)

    event.spreadAllFacesOnEvents(5, events)

    print 'events created'
    
    if blurType == 'boxes':
        print 'boxing video'
        blur.boxVideo(writer, events, video)
    elif blurType == 'boxmob':
        print 'boxing video with mobs'
        blur.boxVideoMob(writer, events, video)
    else:
        print 'blurring video'
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
    print 'loaded hyperframes'
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
            faces = haar.detectFaces(adjustedFrame, frame, detectors)
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
    #loadDetectors takes height, width
    detectors = loadDetectors(frame.shape[0], frame.shape[1])
    for detector in detectors:
        print 'loading %s' % detector.path
        cascade = cv2.CascadeClassifier(detector.path)
        detector.cascade = cascade
    faces = haar.detectFaces(frame, frame, detectors)
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
    spreadAllFacesOnEvents(1, events)
    print 'DONE SPREADING'
    print events

def testRotate(path):
    from hyperlayer.haar import rotate_image, rotate_point
    #load image
    frame = cv2.imread(path)
    #haar it
    #loadDetectors takes height, width
    detectors = loadDetectors(frame.shape[0], frame.shape[1])
    print 'frame shape is %s, %s' % (frame.shape[0], frame.shape[1])
    for detector in detectors:
        print 'loading %s' % detector.path
        cascade = cv2.CascadeClassifier(detector.path)
        detector.cascade = cascade
    #faces = haar.detectFacesAnyColor(frame, frame, detectors)
    #rotate image
    angle = 35
    r_frame = rotate_image(frame, angle)
    #haar it
    r_faces = haar.detectFacesAnyColor(r_frame, r_frame, detectors)
    #render boxes
    print 'boxes pre muxing: %s' % len(r_faces)
    r_faces = haar.muxBoxes(r_faces)
    print 'boxes post muxing: %s' % len(r_faces)
    for i, box in enumerate(r_faces):
        cv2.rectangle(r_frame, (box[0], box[1]), (box[0] + box[2], box[1]+box[3]), (100,100,255), thickness = 1, lineType=8, shift=0)
        cv2.circle(r_frame, (box[0] + box[2]/2, box[1]+box[3]/2), 1, (100,100,255), thickness = 1, lineType=8, shift=0)
    cv2.imshow('haar-rotate', r_frame)
    
    for i, eachBox in enumerate(r_faces):
        #rotate points and render
        box = rotate_point(eachBox, frame, -angle)
        cv2.rectangle(frame, (box[0], box[1]), (box[0] + box[2], box[1]+box[3]), (100,100,255), thickness = 1, lineType=8, shift=0)
        cv2.circle(frame, (box[0] + box[2]/2, box[1]+box[3]/2), 1, (100,100,255), thickness = 1, lineType=8, shift=0)
    cv2.imshow('haar', frame)

    while(1):
        cv2.waitKey(25)

@click.command()
@click.argument('path')
@click.argument('blurtype', default='motion')
@click.option('--jsonpath', help='Json Hyperframe data for import.')
@click.option('--rendertype', default='boxes', help='Render style.')
@click.option('--output', default=None, help='Output file name.')
def redact(path, blurtype, jsonpath, rendertype, output):
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
    elif rendertype == 'testrotate':
        testRotate(path)
    elif jsonpath:
        print 'loading video %s' % path
        video = loadVideo(path)
        print 'loading json %s' % jsonpath
        hyperframes = loadHyperframesFromJson(jsonpath)
        print 'redacting video'
        redactVideoFromHyperframes(video, blurtype, path, hyperframes, output)
        print 'done!'
    elif blurtype != 'motion' and blurtype != 'boxes':
        show_usage()
        raise Exception('ERROR: Could not parse blur type "%s"' % arg)
    else:
        video = loadVideo(path)
        redactVideo(video, blurtype, path, output)
    exit()

if __name__ == '__main__':
    redact()







