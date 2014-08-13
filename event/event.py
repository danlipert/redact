def generateEvents(hyperframes):
    """
    Returns list of blurring events.
    
    hyperframes -- list of hyperframes to generate events from
    """
    print 'generating events...'
    events = []
    BACK_BUFFER_LENGTH = 10
    FORWARD_BUFFER_LENGTH = 10
    for i, eachHyperframe in enumerate(hyperframes):
        try:
            frameBuffer = hyperframes[i-BACK_BUFFER_LENGTH:i+FORWARD_BUFFER_LENGTH]
        except Exception as e:
            events.append('none')
            continue
        if len(eachHyperframe['faces']) > 0:
            event = {'faces':eachHyperframe['faces'], 'type':'move'}
        else:
            event = {'faces':[], 'type':'none'}
        print event
        events.append(event)
        
    print 'events generated'
    return events

