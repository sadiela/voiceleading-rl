

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

def parallel_fifths_and_octaves(state, next_state):
    # two parts separated by a p5 or p8 move to 
    # new pitch classes separated by the same interval 
    num_parallels = 0
    p5 = 7
    p8 = 12
    bass_tenor_intervals = [state[1]-state[0], next_state[1]-next_state[0]]
    bass_alto_intervals = [state[2]-state[0], next_state[2]-next_state[0]]
    bass_soprano_intervals = [state[3]-state[0], next_state[3]-next_state[0]]
    tenor_alto_intervals = [state[2]-state[1], next_state[2]-next_state[1]]
    tenor_soprano_intervals = [state[3]-state[1], next_state[3]-next_state[1]]
    alto_soprano_intervals = [state[3]-state[2], next_state[3]-next_state[2]]
    # CHECK EVERY PAIR 
    # Get intervals for each pair
    all_intervals = [bass_tenor_intervals, bass_alto_intervals, bass_soprano_intervals, tenor_alto_intervals, tenor_soprano_intervals, alto_soprano_intervals]
    print(all_intervals)
    for interval in all_intervals:
        if interval[0] == interval[1] and interval[0] !=0: # don't care if we don't see movement or if no parallel motion
            if interval[0]%12 == 7 and interval[1]%12 == 7:
                print("PARALLEL 5TH")
                num_parallels+=1
            elif interval[0]%12 ==0 and interval[1]%12 == 0:
                print("PARALLEL 8VE")
                num_parallels += 1
    return num_parallels

if __name__ == "__main__":
    state = [47,54,62,71]
    next_state = [54,61,61,70]
    parallel_fifths_and_octaves(state, next_state)

    state = [47,62,66,71]
    next_state = [54,61,70,78]
    parallel_fifths_and_octaves(state, next_state)