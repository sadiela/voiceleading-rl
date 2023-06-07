
'''
This script sets up the state dictionaries for use by 
the RL tonal music models. 
'''
import yaml
import pretty_midi
import sys

'''
Vocabulary:
- Note: one of the 12 distinct tones in tonal music
- Pitch: A specific note-octave pairing (more than 12 of them! 128 in midi world)
- Triad: A chord consisting of three distinct pitches
- 7th chord: A chord consisting of 7 distinct pitches
- Incomplete chord: 
'''


# Ranges typical of 4-part choral music. These can be changed 
# at the user's discretion
bass_range = list(range(40,61))
tenor_range = list(range(48,68)) 
alto_range = list(range(55,75)) 
soprano_range = list(range(60,80)) # FINAL INDEX NOT INCLUDED!

# These are lists of all pitches of a certain note within
# the specified range (40-80 for us)
# VERIFIED!
notesets = [[], # Cs     0 (0,2,4,5,7,9,11)
            [], # C#Df   1
            [], # D      2
            [], # D#Ef   3
            [], # E      4
            [], # F      5
            [], # F#Gf   6
            [], # G      7
            [], # G#Af   8
            [], # A      9
            [], # A# Bf  10
            []] # B      11

for note in range(bass_range[0], soprano_range[-1]+1):
    notesets[note%12].append(note)

# list of notes that occur in each chord in C major
# 0 = C, 2 = D, etc. 
notes_in_chords = {
    1: [0,4,7],
    2: [2,5,9],
    3: [4,7,11],
    4: [5,9,0],
    5: [7,11,2],
    6: [9,0,4],
    7: [11,2,5],
    8: [2,5,9,0], # 2 7th
    9: [5,9,0,4], # 4 7th 
    10: [7,11,2,5], # 5 7th 
    11: [11,2,5,9] # 7 7th
}

# lists of possible roots, thirds, and fifths for each 
# triad in C major
pitches_in_triads_major = {
    1: [notesets[0], notesets[4], notesets[7]], # CEG
    2: [notesets[2], notesets[5], notesets[9]], # DFA
    3: [notesets[4], notesets[7], notesets[11]], # EGB
    4: [notesets[5], notesets[9], notesets[0]], # FAC
    5: [notesets[7], notesets[11], notesets[2]], # GBD
    6: [notesets[9], notesets[0], notesets[4]], # ACE
    7: [notesets[11], notesets[2], notesets[5]], # BDF
}

pitches_in_sevenths_major = {
    2: [notesets[2], notesets[5], notesets[9], notesets[0]], # DFAC
    4: [notesets[5], notesets[9], notesets[0], notesets[4]], # FACE
    5: [notesets[7], notesets[11], notesets[2], notesets[5]], # GBDF
    7: [notesets[11], notesets[2], notesets[5], notesets[9]], # BDFA
}

def is_complete(voicing, chord): 
    unique_notes = [] 
    for pitch in voicing: 
        cur_note = pitch%12
        if cur_note not in unique_notes:
            unique_notes.append(cur_note)
    if chord < 8:
        return False if len(unique_notes) < 3 else True
    else: 
        return False if len(unique_notes) < 4 else True

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

def determine_chord_validity(cur_combo): #, root):
    # takes SORTED note list
    #if cur_combo[0] in root: #forces root position
    if cur_combo[0] in bass_range and cur_combo[1] in tenor_range and cur_combo[2] in alto_range and cur_combo[3] in soprano_range:
        if cur_combo[2] - cur_combo[1] <= 12 and cur_combo[3] - cur_combo[2] <= 12:
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


if __name__ == "__main__":
    '''
    Verify noteset indices are what we expect
    for c in notesets[0]: # cs 
        print(pretty_midi.note_number_to_name(c))
    for cs in notesets[1]: # cs 
        print(pretty_midi.note_number_to_name(cs))'''

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

    with open("./dictionaries/chord_dict_2.yaml", 'w') as outfile:
        yaml.dump(chord_dict, outfile, default_flow_style=False)

    with open("./dictionaries/state_dict_2.yaml", 'w') as outfile:
        yaml.dump(state_dict, outfile, default_flow_style=False)

    for key in chord_dict:
        print("KEY")
        for idx in chord_dict[key]:
            inverse_chord_dict[idx] = key

    with open("./dictionaries/inverse_chord_dict_2.yaml", 'w') as outfile:
        yaml.dump(inverse_chord_dict, outfile, default_flow_style=False)

    