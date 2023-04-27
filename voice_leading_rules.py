

def voice_crossing(state,next_state):
    num_crosses = 0
    # assumes state, next_state are LISTS!
    # voice cross between bass and tenor
    if state[0] > next_state[1] or state[1] < next_state[0]:
        num_crosses += 1
    # between tenor and alto
    if state[1] > next_state[2] or state[2] < next_state[1]:
        num_crosses += 1
    # between alto and soprano:
    if state[2] > next_state[3] or state[3] < next_state[2]:
        num_crosses += 1
    return num_crosses

def parallel_fifths(state, next_state):
    # CHECK EVERY PAIR 
    # [0,1]
    # [0,2]
    # [0,3]
    # [1,2]
    # [1,3]
    # [2,3]
    # Get intervals for each pair
    bass_interval = abs(state[0] - next_state[0]) 
    tenor_interval = abs(state[1] - next_state[1]) 
    alto_interval = abs(state[2] - next_state[2]) 
    soprano_interval = abs(state[3] - next_state[3]) 
    intervals = [bass_interval, tenor_interval, alto_interval, soprano_interval]
    if intervals.count(12) >= 2:
        return True
    return False
