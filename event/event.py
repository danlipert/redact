def generateEvents(hyperframes):
    """
    Returns list of blurring events.
    
    hyperframes -- list of hyperframes to generate events from
    """
    events = []
    BACK_BUFFER_LENGTH = 10
    FORWARD_BUFFER_LENGTH = 10
    for i, eachHyperframe in enumerate(hyperframes):
        try:
            frameBuffer = hyperframes[i-BACK_BUFFER_LENGTH:i+FORWARD_BUFFER_LENGTH]
        except Exception as e:
            events.append('none')
        event = {'faces':eachHyperframe['faces'], 'type':'move'}
        events.append(event)
        
    return events

