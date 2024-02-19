
from state_space_def import * 
from pretty_midi import note_name_to_number

ILL_LEAP =  0.1417
VC =  0.1397
PERF58 = 0.0402
DIR58 = 0.1383
ILL_CT = 0.1293
ILL_LT_RES = 0.128
ILL_7_APP = 0.1428
ILL_7_RES = 0.14

def illegal_leaps(state, next_state): 
    # returns number of instances of an illegal leap 
    bass_interval = abs(next_state[0] - state[0]) # BASS FIRST!!!
    tenor_interval = abs(next_state[1] - state[1])
    alto_interval = abs(next_state[2] - state[2])
    soprano_interval = abs(next_state[3] - state[3])
    num_leaps = 0

    all_intervals = [bass_interval, tenor_interval, alto_interval, soprano_interval]

    for interval in all_intervals:
        if interval > 12 or interval==6 or interval == 11:
            num_leaps += 1
    return num_leaps

def voice_crossing(state,next_state):
    # returns number of instances of voice crossing
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

def parallel_fifths_octaves(state, next_state):
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
    for interval in all_intervals:
        if interval[0] == interval[1] and interval[0] !=0: # don't care if we don't see movement or if no parallel motion
            if interval[0]%12 == 7: # already know they're equal and positive... and abs(interval[1])%12 == 7:
                num_parallels+=1
            elif interval[0]%12 ==0: # and interval[1]%12 == 0:
                num_parallels += 1
    return num_parallels

def direct_fifths_octaves(state, next_state):
    num_d58 = 0
    bass_interval = state[0] - next_state[0]
    tenor_interval = state[1] - next_state[1]
    alto_interval = state[2] - next_state[2]
    soprano_interval = state[3] - next_state[3]
    bass_soprano_interval_2 = next_state[3]-next_state[0]
    bass_tenor_interval_2 = next_state[1]-next_state[0]
    tenor_alto_interval_2 = next_state[2]-next_state[1]
    alto_soprano_interval_2 = next_state[3]-next_state[2]
    # BASS SOP
    if bass_interval != 0 and soprano_interval != 0 and (bass_interval * soprano_interval) > 0 and abs(soprano_interval) > 2:
        # they move in the same direction, leap in the soprano part
        if bass_soprano_interval_2%12 == 0: # move into an octave
            num_d58 += 1
        elif bass_soprano_interval_2%12 == 7: # move into a fifth
            num_d58 += 1
    # BASS TENOR
    if bass_interval != 0 and tenor_interval != 0 and (bass_interval * tenor_interval) > 0 and abs(tenor_interval) > 2:
        # they move in the same direction, leap in the soprano part
        if bass_tenor_interval_2%12 == 0: # move into an octave
            num_d58 += 1
        elif bass_tenor_interval_2%12 == 7: # move into a fifth
            num_d58 += 1
    # TENOR ALTO
    if tenor_interval != 0 and alto_interval != 0 and (tenor_interval * alto_interval) > 0 and abs(alto_interval) > 2:
        # they move in the same direction, leap in the soprano part
        if tenor_alto_interval_2%12 == 0: # move into an octave
            num_d58 += 1
        elif tenor_alto_interval_2%12 == 7: # move into a fifth
            num_d58 += 1
    # ALTO SOP
    if alto_interval != 0 and soprano_interval != 0 and (alto_interval * soprano_interval) > 0 and abs(soprano_interval) > 2:
        # they move in the same direction, leap in the soprano part
        if alto_soprano_interval_2%12 == 0: # move into an octave
            num_d58 += 1
        elif alto_soprano_interval_2%12 == 7: # move into a fifth
            num_d58 += 1    
    return num_d58

def illegal_common_tones(state, next_state):
    # return true if there are three illegal common tones or 4 common tones 
    num_common_tones = 0
    for i in range(4):
        if state[i] == next_state[i]:
            num_common_tones += 1
    if num_common_tones == 3: 
        if state[0] == next_state[0]:
            return 1
        else:
            return 0 # bass arpeggiation!
    elif num_common_tones == 4:
        return 1
    return 0

def leading_tone_resolution(state, next_state): 
    # IMPORTANT IN THE OUTER VOICE!
    # find leading tone:
    for i, note in enumerate(state): 
        if note%12 == 11: # LEADING TONE! Should resolve up by step
            resolution_note = next_state[i]
            res_step = resolution_note - note 
            if not (res_step == 1 or res_step == 2): 
                if i == 0 or i == 3:
                    return 1
                return 0
    return 0

def seventh_approach(state, next_state):
    # a 7th must not be approached by descending leap
    # Figure out if the chord is a 7th:
    # chord_1 = determine_chord_from_voicing(state)
    chord_2 = determine_chord_from_voicing(next_state)

    if chord_2 > 7: # second chord is a 7th
        # find the 7th
        for i, note in enumerate(next_state): 
            if note%12 == notes_in_chords[chord_2][-1]: # find the 7th 
                approach_note = state[i]
                seventh_note = next_state[i]
                if approach_note - seventh_note > 2:
                    # approached by descending leap
                    return 1 
    return 0

def seventh_resolve(state,next_state): 
    # A seventh MUST resolve DOWN by step!
    chord_1 = determine_chord_from_voicing(state)

    if chord_1 > 7: # first chord is a 7th
        for i, note in enumerate(next_state): 
            if note%12 == notes_in_chords[chord_1][-1]:
                seventh_note = state[i]
                resolution_note = next_state[i]
                if seventh_note-resolution_note > 2 or seventh_note-resolution_note < 1: 
                    return 1 # did not resolve down by step
    return 0


### FULL REWARD FUNCTION ###
def voice_leading_reward_function(state, next_state): 
    vc = voice_crossing(state, next_state)
        # negative reward for parallel 5ths/octaves
    p58 = parallel_fifths_octaves(state, next_state)

    ill = illegal_leaps(state, next_state)

    d58 = direct_fifths_octaves(state, next_state)

    lt_res = leading_tone_resolution(state, next_state)

    #doubled_lt = doubled_leading_tone(next_state)

    sev_app = seventh_approach(state, next_state)
    sev_res = seventh_resolve(state,next_state)

    # get info about next_state
    next_state_chord = determine_chord_from_voicing(next_state)
    next_state_inv = determine_inversion(next_state, next_state_chord)

    # FOR THESE, TRUE == ILLEGAL! BAD! DOES BREAK A RULE!


    bad_ct = illegal_common_tones(state, next_state)

    #inv_triad_complete = check_inv_triad_complete(next_state)

    #dim_triad_first_inv = dim_triad_first_inversion(next_state)

    #ts_inv_doubling = second_inversion_triad_doubling(next_state)


    return -VC*vc + -PERF58*p58 + -ILL_LEAP*ill + -DIR58*d58 + -ILL_LT_RES*lt_res+ -ILL_CT*bad_ct +  -ILL_7_RES*sev_res+ -ILL_7_APP*sev_app, vc, p58, ill, d58
    #  -.1*doubled_lt + -.05*triad_first_inv -.05*ts_inv_doubling + -.05*dim_t_inv +  -.2*inv_triad_complete +


#######################
# HARMONIC PROG RULES #
#######################
major_harmonic_adjacency_matrix = [
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # I
    [0, 0, 0, 0, 1, -1, 1, 0, 0, 1, 1], # ii
    [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0], # iii
    [1, 1, 0, 0, 1, -1, 1, 1, 0, 1, 1], # IV
    [1, -1, 0, -1, 0, 1, 0, 0, 0, 0, 0], # V
    [0, 1, -1, 1, 0, 0, 0, 1, 1, 0, 0], # vi
    [1, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0], # vii
    [0, 0, 0, 0, 1, -1, 1, 0, 0, 1, 1], # ii7
    [1, 1, 0, 0, 1, -1, 1, 1, 0, 1, 1], # IV7
    [1, -1, 0, -1, 0, 1, 0, 0, 0, 0, 0], # V7
    [1, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0]  # vii7
]

minor_harmonic_adjacency_matrix = [
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # i
    [0, 0, 0, 0, 1, -1, 1, 0, 0, 1, 1], # iidim
    [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0], # III
    [], # 
    [], # 
    [], # vi
    [], # vii
    [], # ii7
    [], # IV7
    [], # V7
    []  # vii7
]

def harmonic_prog_reward_major(state, next_state): 
    chord_1 = determine_chord_from_voicing(state)
    chord_2 = determine_chord_from_voicing(next_state)
    if major_harmonic_adjacency_matrix[chord_1-1][chord_2-1] == 0:
        return -0.3
    elif major_harmonic_adjacency_matrix[chord_1-1][chord_2-1] == -1:
        return -1
    return 0


def harmonic_prog_reward_minor(state, next_state): 
    chord_1 = determine_chord_from_voicing(state)
    chord_2 = determine_chord_from_voicing(next_state)
    if minor_harmonic_adjacency_matrix[chord_1-1][chord_2-1] == 0:
        return -0.3
    elif minor_harmonic_adjacency_matrix[chord_1-1][chord_2-1] == -1:
        return -1
    return 0



def note_names_to_numbers(namelist):
    numbers = []
    for name in namelist:
        numbers.append(note_name_to_number(name))
    return numbers

#### MODEL REWARD FUNCTIONS ####
def harmonization_reward_function(cur_start, cur_end): # for major 
    vl_reward, vc,p58,il,d58 =  voice_leading_reward_function(cur_start, cur_end)
    harm_prog_reward = harmonic_prog_reward_major(cur_start, cur_end)
    return vl_reward + harm_prog_reward, vc,p58,il,d58



if __name__ == "__main__":
    print("Voice leading rules unit tests:") # E2 to G5

    ##################
    ### UNIT TESTS ###
    ##################

    ### ILLEGAL LEAPS ###
    # Avoid augmented intervals (6 half steps)
    print("\n### ILLEGAL LEAP UNIT TESTS ###")
    aug_1 = note_names_to_numbers(["F3","A3","C4","F4"])
    aug_2 = note_names_to_numbers(["G3","D4","G4","B4"]) # AUGMENTED INTERVAL FROM F4 to B4
    num_aug_leaps = illegal_leaps(aug_1, aug_2)
    print("Augmented unit test:", num_aug_leaps)
    # 7ths(11 half steps), 
    sev_1 = note_names_to_numbers(["E3","A3","A3","C4"])
    sev_2 = note_names_to_numbers(["D3","G3","G4","B4"]) # 7th interval from C4 to B4
    num_sev_leaps = illegal_leaps(sev_1, sev_2)
    print("Seventh unit test:", num_sev_leaps)
    
    # and intervals larger than an octave (>12 half steps)
    oct_1 = note_names_to_numbers(["C3","E4","G4","C5"])
    oct_2 = note_names_to_numbers(["D4","F4","A4","D5"])# Jump of more than an octave from C3 to D4
    num_oct_leaps = illegal_leaps(oct_1, oct_2)
    print("Octave unit test:", num_oct_leaps)

    ### VOICE CROSSING ###
    print("\n### VOICE CROSSING UNIT TESTS ###")
    # single crossing 
    cross_1 = note_names_to_numbers(["C3","E3","G3","C4"])
    cross_2 = note_names_to_numbers(["B2","D3","D4","F4"]) # alto crosses above soprano line
    num_crossing = voice_crossing(cross_1,cross_2)
    print("Single voice crossing unit test:", num_crossing)

    multi_cross_1 = note_names_to_numbers(["C3","E3","G3","C4"])
    multi_cross_2 = note_names_to_numbers(["F3","A3","C4","F4"]) # bass crosses above previous tenor line, tenor crosses above previous alto line 
    num_multi_crossing = voice_crossing(multi_cross_1,multi_cross_2)
    print("Multiple voice crossing unit test:", num_multi_crossing)
    
    ### PARALLEL 5ths AND OCTAVES ###
    print("\n### PARALLEL MOTION UNIT TESTS ###")
    pfifths_1 = note_names_to_numbers(["C3","G3","E4","C5"]) 
    pfifths_2 = note_names_to_numbers(["G3","D4","D4","B4"])
    num_pfifths = parallel_fifths_octaves(pfifths_1,pfifths_2)
    print("Parallel 5ths unit test:", num_pfifths)

    pocts_1 = note_names_to_numbers(["C3","E4","G4","C5"])
    pocts_2 = note_names_to_numbers(["G3","D4","B4","G5"])
    num_pocts = parallel_fifths_octaves(pocts_1,pocts_2)
    print("Parallel octaves unit test:", num_pocts)

    ### DIRECT 5ths AND OCTAVES ###
    print("\n### DIRECT MOTION UNIT TESTS ###")
    dfifths_1 = note_names_to_numbers(["E3","G3","E4","C5"]) 
    dfifths_2 = note_names_to_numbers(["D3","D4","F4","A4"])
    num_dfifths = direct_fifths_octaves(dfifths_1,dfifths_2)
    print("Direct 5ths unit test:", num_dfifths)

    docts_1 = note_names_to_numbers(["C3","G3","C4","E4"])
    docts_2 = note_names_to_numbers(["G3","B3","D4","G4"])
    num_docts = direct_fifths_octaves(docts_1,docts_2)
    print("Direct octaves unit test:", num_docts)

    ### THREE COMMON TONES ###
    print("\n### THREE COMMON TONES UNIT TESTS ###")
    # single crossing 
    ctones_1 = note_names_to_numbers(["F3","A3","C4","F4"]) 
    ctones_2 = note_names_to_numbers(["F3","A3","C4","E4"])
    check_illegal_ctones = illegal_common_tones(ctones_1,ctones_2)
    print("Illegal 3ct unit test:", check_illegal_ctones)

    legal_ctones_1 = note_names_to_numbers(["C3","E4","G4","C5"]) 
    legal_ctones_2 = note_names_to_numbers(["E3","E4","G4","C5"])
    check_legal_ctones = illegal_common_tones(legal_ctones_1,legal_ctones_2)
    print("Legal 3ct unit test:", check_legal_ctones)

    ### INVERTED TRIADS COMPLETE ###
    print("\n### COMPLETE 1st INVERSION TRIADS UNIT TESTS ###")
    complete_inv_triad = note_names_to_numbers(["E3","G3","C4","C5"]) 
    check_complete_triad = check_inv_triad_complete(complete_inv_triad)
    print("Complete inverted triad unit test:", check_complete_triad)

    inc_inv_triad = note_names_to_numbers(["E3","C4","C4","C5"]) 
    check_incomplete_triad = check_inv_triad_complete(inc_inv_triad)
    print("Incomplete inverted triad unit test:", check_incomplete_triad)

    ### SECOND INVERSION TRIADS: 5th DOUBLED ###
    print("\n### SECOND INVERSION TRIADS w/ DOUBLED 5ths UNIT TESTS ###")
    doubled_fifths = note_names_to_numbers(["G3","C4","E4","G4"]) 
    check_doubled_fifths = second_inversion_triad_doubling(doubled_fifths)
    print("Second inversion doubled fifths unit test:", check_doubled_fifths)

    no_doubled_fifths = note_names_to_numbers(["G3","C4","E4","C5"]) 
    check_no_doubled_fifths = second_inversion_triad_doubling(no_doubled_fifths)
    print("Second inversion doubled root unit test:", check_no_doubled_fifths)

    ### DOUBLED LEADING TONE ###
    print("\n### DOUBLED LEADING TONE UNIT TESTS ###")
    has_doubled_leading_tone = note_names_to_numbers(["B3","D4","F4","B4"]) 
    check_dl = doubled_leading_tone(has_doubled_leading_tone)
    print("Doubled leading tone unit test:", check_dl)
    assert check_dl == 1

    no_doubled_leading_tone = note_names_to_numbers(["B3","D4","F4","D5"]) 
    check_ndl = doubled_leading_tone(no_doubled_leading_tone)
    print("No doubled leading tone unit test:", check_ndl)
    assert check_ndl == 0

    ### DIMINISHED TRIAD SHOULD BE IN FIRST INVERSION ###
    dim_first_inversion = note_names_to_numbers(["D3","B3","F4","B4"]) 
    check_dim_first = dim_triad_first_inversion(dim_first_inversion)
    print("Diminished triad first inversion unit test:", check_dim_first)
    assert check_dim_first == 0

    dim_root_position = note_names_to_numbers(["B3","D4","F4","D5"]) 
    check_dim_root = dim_triad_first_inversion(dim_root_position)
    print("Diminished triad root position unit test:", check_dim_root)
    assert check_dim_root == 1

    ### LEADING TONE RESOLVES UP TO TONIC ###
    print("\n### LEADING TONE RESOLUTION UNIT TESTS ###")
    chord_with_leading_tone = note_names_to_numbers(["G2","F3","D4","B4"]) 
    resolution = note_names_to_numbers(["C3","E3","C4","C5"])
    resolved_incorrectly = leading_tone_resolution(chord_with_leading_tone, resolution)
    print("Correct leading tone resolution unit test:", resolved_incorrectly)
    assert resolved_incorrectly == 0 # is resolved correctly!

    ### SEVENTH APPROACH ###
    print("\n### APPROACHING THE 7th UNIT TESTS ###")
    approach_chord = note_names_to_numbers(["D3","F3","A3","D4"]) # approach by common tone
    seventh_chord = note_names_to_numbers(["G2","F3","D4","B4"])
    approached_incorrectly = seventh_approach(approach_chord, seventh_chord)
    print("Correct seventh approach unit test:", approached_incorrectly)
    assert approached_incorrectly == 0 # is resolved correctly!

    ### SEVENTH RESOLUTION ###
    print("\n### RESOLVING THE 7th UNIT TESTS ###")
    seventh_chord = note_names_to_numbers(["G2","F3","D4","B4"]) 
    resolution_chord = note_names_to_numbers(["C3","E3","C4","C5"])
    resolved_incorrectly = seventh_resolve(chord_with_leading_tone, resolution)
    print("Correct seventh resolution unit test:", resolved_incorrectly)
    assert resolved_incorrectly == 0 # is resolved correctly!

    ### COMPLETELY LEGAL VOICINGS ###
    # should have 0 reward
    chord1 = note_names_to_numbers(["D3","B3","A4","F5"]) # iii6
    chord2 = note_names_to_numbers(["E3","B3","G4","E5"]) # V6
    chord3 = note_names_to_numbers(["G3","B3","G4","D5"]) # vi
    chord4 = note_names_to_numbers(["E3","C4","G4","C5"]) # V7
    chord5 = note_names_to_numbers(["A2","C4","E4","E5"]) # I

    print(voice_leading_reward_function(chord1, chord2))    
    print(voice_leading_reward_function(chord2, chord3))    
    print(voice_leading_reward_function(chord3, chord4))    
    print(voice_leading_reward_function(chord4, chord5))    

