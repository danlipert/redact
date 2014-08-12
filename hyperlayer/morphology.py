def lowPassFilter(hyperframes):
    """
    Returns list of hyperframe data (video metadata) passed through low pass filter.
    
    hyperframes -- list of hyperframe data
    """
    
    pass

def erode(inputList):
    """
    Very simple erosion function for list of discrete data.  Returns eroded list.
    
    inputList -- list of data to erode
    """
    
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
    return outputList
