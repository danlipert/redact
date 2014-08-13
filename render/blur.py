import cv2

def blurVideo(writer, events, video, blurType='motion'):
    """
    Returns image adjusted for facial detection.
    
    video -- source video to blur
    events -- list of blurring events
    """
    #setupWindows()
    print 'rendering video...'
    #very basic implementation
    
    #first restart video
    video.set(cv2.cv.CV_CAP_PROP_POS_AVI_RATIO, 0)
    for event in events:
        #read source video frames
        ret, frame = video.read()
        source_frame = frame
        #draw on each frame
        if event['type'] == 'spawn' or event['type'] == 'move':
            faces = event['faces']
            
            for eachFace in faces:
                eachFaceRect = eachFace
                print eachFaceRect
                cv2.rectangle(frame, (eachFaceRect[0], eachFaceRect[1]), (eachFaceRect[0] + eachFaceRect[2], eachFaceRect[1]+eachFaceRect[3]), (255,100,100), thickness = 1, lineType=8, shift=0)
            
            #eachFaceRect = event['faces']
            #cv2.rectangle(frame, (eachFaceRect[0], eachFaceRect[1]), (eachFaceRect[0] + eachFaceRect[2], eachFaceRect[1]+eachFaceRect[3]), (255,100,100), thickness = 1, lineType=8, shift=0)
        #drawVisualization(source_frame, frame)
        
        #write frame
        writer.write(frame)
    
    writer.release()

def setupWindows():
    cv2.namedWindow('Source', flags=cv2.WINDOW_NORMAL)
    cv2.namedWindow('Render', flags=cv2.WINDOW_NORMAL)

def drawVisualization(source_frame, drawn_frame):
    if cv2.waitKey(25) == 27:
        exit()
    cv2.imshow('Source', source_frame)
    cv2.imshow('Render', drawn_frame)
