def lowPassFilter(hyperframes):
    """
    Returns list of hyperframe data (video metadata) passed through low pass filter.
    
    hyperframes -- list of hyperframe data
    """
    
    return hyperframes

def erode(hyperframes):
    """
    Very simple erosion function for list of hyperframe data.  Returns eroded list.
    
    inputList -- list of hyperframes to erode
    """
    '''
    outputList = []
    for i, eachListItem in enumerate(inputList):
        try:
            prevItem = inputList[i-1]
            nextItem = inputList[i+1]
        except Exception as e:
            outputList.append(eachListItem)
        if eachListItem == prevItem or eachListItem == nextItem:
            outputList.append(eachListItem)
            continue
        else:
            outputList.append(prevItem)
    '''
    
    outputList = []
    for i, eachHyperframe in enumerate(hyperframes):
        try:
            prevFrame = hyperframes[i-1]
            nextFrame = hyperframes[i+1]
        except Exception as e:
            outputList.append(eachHyperframe)
        if len(eachHyperframe['faces']) == len(prevFrame['faces']) or len(eachHyperframe['faces']) == len(nextFrame['faces']):
            outputList.append(eachHyperframe)
            continue
        else:
            outputList.append(prevFrame)
    
    return outputList
