
'''
This script sets up the state dictionaries for use by 
the RL tonal music models. 
'''
import yaml
import pretty_midi
import sys
from chord_constants import *

'''
Vocabulary:
- Note: one of the 12 distinct tones in tonal music
- Pitch: A specific note-octave pairing (more than 12 of them! 128 in midi world)
- Triad: A chord consisting of three distinct pitches
- 7th chord: A chord consisting of 7 distinct pitches
- Incomplete chord: 
'''

########################################################
# RULES THAT ARE NOT DEPENDENT ON PREVIOUS STATE!
def doubled_leading_tone(next_state):
    leading_tone_count = 0 
    for note in next_state:
        if note%12 == 11:
            leading_tone_count += 1
    if leading_tone_count > 1:
        return 1
    return 0

def dim_triad_first_inversion(next_state):  # WILL ONLY WORK FOR MAJOR
    chord = determine_chord_from_voicing(next_state)
    inversion = determine_inversion(next_state, chord)
    if chord == 7: # diminished 7th 
        if inversion != 1:
            return 1
    return 0

def check_inv_triad_complete(next_state): 
    # INVERTED TRIADS SHOULD BE COMPLETE!
    # Return true if NOT complete
    chord = determine_chord_from_voicing(next_state)
    inversion = determine_inversion(next_state, chord)
    if inversion == 1: 
        if not is_complete(next_state, chord):
            return 1
    return 0

def second_inversion_triad_doubling(next_state): 
    # return true if INCORRECT doubling
    chord = determine_chord_from_voicing(next_state)
    inversion = determine_inversion(next_state, chord)
    if inversion == 2 and chord < 8:
        # 5th should be doubled
        fifth = notes_in_chords[chord][2]
        num_fifths = 0
        for pitch in next_state:
            if pitch%12 == fifth:
                num_fifths += 1
        if num_fifths >=2:
            return 0
        else:
            return 1
    return 0
########################################################

def is_complete(voicing, chord): 
    unique_notes = [] 
    for pitch in voicing: 
        cur_note = pitch%12
        if cur_note not in unique_notes:
            unique_notes.append(cur_note)
    if chord < 8:
        if len(unique_notes) < 3:
            return False
    else: 
        if len(unique_notes) < 4:
            return False 
    return True

def determine_inversion(voicing, chord): 
    bottom_note = voicing[0]%12
    for i,n in enumerate(notes_in_chords[chord]):
        if bottom_note == n: 
            return i
    # returns 0 for root position, 1 for first inversion, 2 for second, 3 for third (7ths only)

def determine_chord_from_voicing(voicing):
    note_list = []
    for pitch in voicing: 
        note = pitch%12
        if note not in note_list:
            note_list.append(note)
    for i in range(1,12):
        #print(i)
        if set(note_list).issubset(set(notes_in_chords[i])) and notes_in_chords[i][0] in note_list: # has to have root
            return i

    # now i have list of pitches (unique)... determine the chord!

def chord_strings(idx_list, state_dict):
    voicing_list = [state_dict[i] for i in idx_list]
    chord_strings = [chord_and_inversion_string(i) for i in  voicing_list]
    return chord_strings

def chord_and_inversion_string(voicing):
    chord = determine_chord_from_voicing(voicing)
    inv = determine_inversion(voicing, chord)
    chord_str = chord_number_to_string_major[chord]
    if chord < 8:
        return chord_str + inversion_numbers_triad[inv]
    else: 
        return chord_str+inversion_numbers_seventh[inv]

def determine_chord_validity(cur_combo): #, root):
    # takes SORTED note list
    #if cur_combo[0] in root: #forces root position
    if cur_combo[0] in bass_range and cur_combo[1] in tenor_range and cur_combo[2] in alto_range and cur_combo[3] in soprano_range:
        if cur_combo[2] - cur_combo[1] <= 12 and cur_combo[3] - cur_combo[2] <= 12:
            if len(set(cur_combo)) > 2: # need more than 2 distinct notes
                if not (doubled_leading_tone(cur_combo) or dim_triad_first_inversion(cur_combo) or check_inv_triad_complete(cur_combo) or second_inversion_triad_doubling(cur_combo)):
                    return True
    return False

def gen_seventh_options(chord_num):
    chord_options = []
    root, third, fifth, seventh = pitches_in_sevenths_major[chord_num]

    # incomplete
    for r in root: 
        for t in third: 
            for f in fifth:
                for s in seventh: 
                    cur_combo = [r,t,f,s]
                    cur_combo.sort()
                    if cur_combo not in chord_options and determine_chord_validity(cur_combo):
                        chord_options.append(cur_combo)
    # complete
    for r in root: 
        for r2 in root: 
            for t in third: 
                for s in seventh: 
                    cur_combo = [r,r2,t,s]
                    cur_combo.sort()
                    if cur_combo not in chord_options and determine_chord_validity(cur_combo):
                        chord_options.append(cur_combo)
    
    return chord_options

def gen_triad_options(chord_num):
    chord_options = []
    root, third, fifth = pitches_in_triads_major[chord_num] # need one of each, but they can be in any position besides the root

    # incomplete 
    for r in root: # doubled root 
        for r2 in root: 
            for r3 in root:
                for t in third: 
                    cur_combo = [r, r2, r3, t]
                    cur_combo.sort()
                    if cur_combo not in chord_options and determine_chord_validity(cur_combo):
                        chord_options.append(cur_combo) 

    # root doubled
    for r in root: # doubled root 
        for r2 in root: 
            for t in third:
                for f in fifth: 
                    cur_combo = [r, r2, t, f]
                    cur_combo.sort()
                    if cur_combo not in chord_options and determine_chord_validity(cur_combo):
                        chord_options.append(cur_combo)

    # third doubled
    for r in root: # doubled fifth
        for t1 in third:
            for t2 in third: 
                for f in fifth: 
                    cur_combo = [r, t1, t2, f]
                    cur_combo.sort()
                    if cur_combo not in chord_options and determine_chord_validity(cur_combo):
                        chord_options.append(cur_combo)

    # fifth doubled
    for r in root: # doubled fifth
        for t in third:
            for f1 in fifth: 
                for f2 in fifth: 
                    cur_combo = [r, t, f1, f2]
                    cur_combo.sort()
                    if cur_combo not in chord_options and determine_chord_validity(cur_combo):
                        chord_options.append(cur_combo)

    # DIMINISHED HARMONIES NEED DOUBLED 3RDS
    return chord_options

def gen_all_chords():
    # get it 
    triad_1_options = gen_triad_options(1) 
    triad_2_options = gen_triad_options(2)
    triad_3_options = gen_triad_options(3) # CAN'T DOUBLE 5th B/C ITS A LEADING TONE!
    triad_4_options = gen_triad_options(4)
    triad_5_options = gen_triad_options(5)
    triad_6_options = gen_triad_options(6)
    triad_7_options = gen_triad_options(7) # DIMINISHED! Double the third
    seventh_2_options = gen_seventh_options(2)
    seventh_4_options = gen_seventh_options(4)
    seventh_5_options = gen_seventh_options(5)
    seventh_7_options = gen_seventh_options(7)

    all_chord_options = [triad_1_options, triad_2_options, 
                         triad_3_options, triad_4_options, 
                         triad_5_options, triad_6_options, 
                         triad_7_options, seventh_2_options,
                         seventh_4_options, seventh_5_options,
                         seventh_7_options]

    return all_chord_options

def generate_chord_dictionaries():
    all_chord_options = gen_all_chords()

    '''
    # make sure the chords are what we expect
    total_states = 0 
    for i, voicing_options in enumerate(all_chord_options):
        print("Chord number:", i+1)
        total_states += len(voicing_options)
        print("Cur total states:", total_states)
        for c_opt in voicing_options:
            chord = determine_chord_from_voicing(c_opt)
            assert chord == i+1
    print(total_states)''' 

    chord_dict = {}
    inverse_chord_dict = {}
    state_dict = {}   

    # create state dictionary, chord dictionary (indices mapped to )
    index = 0 
    for i, voicing_options in enumerate(all_chord_options):
        chord_dict[i+1] = []
        for c_opt in voicing_options:
            state_dict[index] = c_opt
            chord_dict[i+1].append(index)
            index += 1


    # save dictionaries to yaml files # 
    with open("./dictionaries/chord_dict_3.yaml", 'w') as outfile:
        yaml.dump(chord_dict, outfile, default_flow_style=False)

    with open("./dictionaries/state_dict_3.yaml", 'w') as outfile:
        yaml.dump(state_dict, outfile, default_flow_style=False)

    for key in chord_dict:
        for idx in chord_dict[key]:
            inverse_chord_dict[idx] = key

    print(len(inverse_chord_dict.keys())) # 1917 chords

    with open("./dictionaries/inverse_chord_dict_3.yaml", 'w') as outfile:
        yaml.dump(inverse_chord_dict, outfile, default_flow_style=False)



if __name__ == "__main__":
    # load state dict
    generate_chord_dictionaries()
    '''
    with open('./dictionaries/state_dict_2.yaml', 'r') as file:
        state_dict = yaml.safe_load(file)

    print(len(state_dict.keys()))
    input("Continue...")
    idx_list = [19, 240, 592, 943, 2]
    voicing_list = [state_dict[i] for i in idx_list]
    print("VOICINGS", voicing_list)
    chord_strings = [chord_and_inversion_string(i) for i in  voicing_list]
    print("CHORD STRINGS:", chord_strings)

    Verify noteset indices are what we expect
    for c in notesets[0]: # cs 
        print(pretty_midi.note_number_to_name(c))
    for cs in notesets[1]: # cs 
        print(pretty_midi.note_number_to_name(cs))'''
    