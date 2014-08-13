def blurVideo(events, video, blurType='motion'):
    """
    Returns image adjusted for facial detection.
    
    video -- source video to blur
    events -- list of blurring events
    """
    #very basic implementation
    for eachEvent in events:
        #read source video frames
        ret, frame = video.read()
        
        #draw on each frame
        if event['type'] == 'spawn' or event['type'] == 'move':
            faces = event['faces']
            for eachFace in faces:
                eachFaceRect = eachFace
                cv2.rectangle(frame, (eachFaceRect[0], eachFaceRect[1]), (eachFaceRect[0] + eachFaceRect[2], eachFaceRect[1]+eachFaceRect[3]), (255,100,100), thickness = 1, lineType=8, shift=0)
        
        #write frame
        writer.write(frame)
