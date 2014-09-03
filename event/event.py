import numpy
from util.image import isHumanColor

def generateEvents(hyperframes):
    """
    Returns list of blurring events.
    
    hyperframes -- list of hyperframes to generate events from
    """
    BACK_BUFFER_LENGTH = 10
    FORWARD_BUFFER_LENGTH = 10
    DISTANCE_THRESHOLD=200
    
    print 'generating events...'
    events = []
    hyperframes = movingAverage(hyperframes)
    
    #place blank events first
    #for eachHyperframe in hyperframes:
    #    events.append({'faces':[], 'type':'move'})
    
    for i, eachHyperframe in enumerate(hyperframes):
        frameSlice = hyperframes[i-BACK_BUFFER_LENGTH:i+FORWARD_BUFFER_LENGTH]
        goodFaces = []
        if len(eachHyperframe['faces']) > 0:
            for eachFace in eachHyperframe['faces']:
                #look for nearby boxes in time
                for eachBufferFrame in frameSlice:
                    for eachBufferFace in eachBufferFrame['faces']:
                        dist = numpy.linalg.norm(centerOfBox(eachFace)-centerOfBox(eachBufferFace))
                        if dist < DISTANCE_THRESHOLD:
                            #found nearby box in time
                            goodFaces.append(eachFace)
                            #spreadFacesOnEvents(1, i, eachFace, events)
        events.append({'faces':goodFaces, 'type':'move'})
    print 'events generated'
    return events
    
def generateSimpleEvents(hyperframes):
    events = []
    for i, eachHyperframe in enumerate(hyperframes):
        events.append({'faces':eachHyperframe['faces'], 'type':'move'})
    return events

def spreadAllFacesOnEvents(spread, events):
    import copy
    eventsCopy = copy.deepcopy(events)
    for i, event in enumerate(eventsCopy):
        for eachFace in eventsCopy[i]['faces']:
            spreadFaceOnEvents(spread, i, eachFace, events)

def spreadFaceOnEvents(spread, index, face, events):
    #print 'spreading event for frame %i, face: %s' % (index, face)
    spreadEvents = [{'faces':[], 'type':'move'} for x in range(0, len(events))]
    for i in range(index-spread,index+spread+1):
        if i < 0:
            continue
        if i >= len(events):
            continue
        if face in events[i]['faces']:
            #print 'face %s already exists in event %i: %s' % (face, i, events[i]['faces'])
            pass
        else:
            #print 'face %s is not in event %i\'s faces %s' % (face, i, events[i]['faces'])
            spreadEvents[i]['faces'].append(face)
    combineEventsFaces(spreadEvents, events)

def combineEventsFaces(events, otherEvents):
    #print 'combining %s and %s' % (events, otherEvents)

    for i, eachEvent in enumerate(events):
        for eachFace in eachEvent['faces']:
            if eachFace not in otherEvents[i]['faces']:
                otherEvents[i]['faces'].append(eachFace)
    #print 'combined: %s' % otherEvents


def ratioOfHyperframeSlice(frameSlice):
    
    goodCount = 0
    for eachFrame in frameSlice:
        if len(eachFrame['faces']) > 0:
            goodCount = goodCount + 1
    
    return goodCount/len(frameSlice)

def movingAverage(hyperframes):
    """
    Applies moving average filter to hyperframe data to remove false positives.
    
    hyperframes -- array of hyperframe data
    """
    
    BACK_BUFFER_LENGTH = 2
    FORWARD_BUFFER_LENGTH = 2
    RATIO_THRESHOLD = .3
    filteredHyperframes = []

    for i, eachHyperframe in enumerate(hyperframes):
        #skip first frames
        if i < BACK_BUFFER_LENGTH:
            filteredHyperframes.append(eachHyperframe)
        #skip last frames
        if (len(hyperframes) - i) < FORWARD_BUFFER_LENGTH:
            filteredHyperframes.append(eachHyperframe)
        #compile frame slice
        frameSlice = hyperframes[i-BACK_BUFFER_LENGTH:i+FORWARD_BUFFER_LENGTH]
        
        ratio = ratioOfHyperframeSlice(hyperframes)
        
        if len(eachHyperframe['faces']) == 1:
            if ratio > RATIO_THRESHOLD:
                filteredHyperframes.append(eachHyperframe)
            else:
                blankHyperframe = {'frameNumber':i, 'faces':[]}
                filteredHyperframes.append(blankHyperframe)
        elif len(eachHyperframe['faces']) > 1:
            #add this later
            filteredHyperframes.append(eachHyperframe)
        else:
            #zero faces
            filteredHyperframes.append(eachHyperframe)
    
    return filteredHyperframes
    
def centerOfBox(box):
    """
    Returns center point [x,y] of box
    
    box -- bounding box [x,y,w,h]
    """
    x = box[0]
    y = box[1]
    w = box[2]
    h = box[3]
    
    px = x + w / 2
    py = y + h / 2
    return numpy.array((int(px), int(py)))

def closestBox(box, candidates):
    """
    Returns the closest bounding box out of the candidates to the provided box
    
    box -- box to find the closest to
    candidates -- array of boxes to compare to
    """
    
    #first guess that its the first one (why not?)
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        return None
    
    boxCenter = centerOfBox(box)
    closest = candidates[0]
    #some large distance to start
    kingDistance = 99999999999
    for i, eachCandidate in enumerate(candidates):
        if i == 0:
            #already handled
            continue
        candidateCenter = centerOfBox(eachCandidate)
        dist = numpy.linalg.norm(centerOfBox-candidateCenter)
        if dist < kingDistance:
            kingDistance = dist
            closest = eachCandidate
    
    return closest

