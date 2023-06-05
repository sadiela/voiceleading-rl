
import random
import itertools
import yaml
import pretty_midi

# pretty_midi.note_number_to_name(note_number) CHECK DICTS!

bass_range = list(range(40,61))
tenor_range = list(range(48,68)) 
alto_range = list(range(55,75)) 
soprano_range = list(range(60,80)) # FINAL INDICE NOT INCLUDED!

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

pitches_in_triads_major = {
    1: [notesets[0], notesets[4], notesets[7]], # CEG
    2: [notesets[2], notesets[5], notesets[9]], # DFA
    3: [notesets[4], notesets[7], notesets[11]], # EGB
    4: [notesets[5], notesets[9], notesets[0]], # FAC
    5: [notesets[7], notesets[11], notesets[2]], # GBD
    6: [notesets[9], notesets[0], notesets[4]], # ACE
    7: [notesets[11], notesets[2], notesets[5]], # BDF
}

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

pitches_in_sevenths_major = {
    2: [notesets[2], notesets[5], notesets[9], notesets[0]], # DFAC
    4: [notesets[5], notesets[9], notesets[0], notesets[4]], # FACE
    5: [notesets[7], notesets[11], notesets[2], notesets[5]], # GBDF
    7: [notesets[11], notesets[2], notesets[5], notesets[9]], # BDFA
}

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
        print(i)
        if(set(note_list).issubset(set(notes_in_chords[i]))):
            print("Found the chord!")
            return i

    # now i have list of pitches (unique)... determine the chord!


def determine_chord_validity(cur_combo, root):
    # takes SORTED note list
    if cur_combo[0] in root:
        if cur_combo[0] in bass_range and cur_combo[1] in tenor_range and cur_combo[2] in alto_range and cur_combo[3] in soprano_range:
            if cur_combo[2] - cur_combo[1] <= 12 and cur_combo[3] - cur_combo[2] <= 12:
                return True
    return False


def gen_seventh_options(chord_num, inc=False):
    chord_options = []
    root, third, fifth, seventh = pitches_in_sevenths_major[chord_num]

    if inc==False:
        for r in root: 
            for t in third: 
                for f in fifth:
                    for s in seventh: 
                        cur_combo = [r,t,f,s]
                        cur_combo.sort()
                        if cur_combo not in chord_options and determine_chord_validity(cur_combo, root):
                            chord_options.append(cur_combo)
    else:  # INCOMPLETE 7ths!
        for r in root: 
            for r2 in root: 
                for t in third: 
                    for s in seventh: 
                        cur_combo = [r,r2,t,s]
                        cur_combo.sort()
                        if cur_combo not in chord_options and determine_chord_validity(cur_combo, root):
                            chord_options.append(cur_combo)
    return chord_options

def gen_triad_options(chord_num, double_note=1):
    chord_options = []
    root, third, fifth = pitches_in_triads_major[chord_num] # need one of each, but they can be in any position besides the root
    #print(root, third, fifth)

    if double_note == 1:
        for r in root: # doubled root 
            for r2 in root: 
                for t in third:
                    for f in fifth: 
                        cur_combo = [r, r2, t, f]
                        cur_combo.sort()
                        if cur_combo not in chord_options and determine_chord_validity(cur_combo, root):
                            chord_options.append(cur_combo)

    elif double_note == 3:
        for r in root: # doubled fifth
            for t1 in third:
                for t2 in third: 
                    for f in fifth: 
                        cur_combo = [r, t1, t2, f]
                        cur_combo.sort()
                        if cur_combo not in chord_options and determine_chord_validity(cur_combo, root):
                            chord_options.append(cur_combo)

    elif double_note == 5:
        for r in root: # doubled fifth
            for t in third:
                for f1 in fifth: 
                    for f2 in fifth: 
                        cur_combo = [r, t, f1, f2]
                        cur_combo.sort()
                        if cur_combo not in chord_options and determine_chord_validity(cur_combo, root):
                            chord_options.append(cur_combo)

    # DIMINISHED HARMONIES NEED DOUBLED 3RDS
    return chord_options

if __name__ == "__main__":
    for c in notesets[0]: # cs 
        print(pretty_midi.note_number_to_name(c))

    input("Continue...")
    '''
    print("Bs:")
    for b in Bs: 
        print(pretty_midi.note_number_to_name(b))

    print("Cs:")
    for c in Cs: 
        print(pretty_midi.note_number_to_name(c))

    print("Ds:")
    for d in Ds: 
        print(pretty_midi.note_number_to_name(d))

    print("Es:")
    for e in Es: 
        print(pretty_midi.note_number_to_name(e))

    print("Fs:")
    for f in Fs: 
        print(pretty_midi.note_number_to_name(f))

    print("Gs:")
    for g in Gs: 
        print(pretty_midi.note_number_to_name(g))'''

    triad_1_options = gen_triad_options(1) + gen_triad_options(1, double_note=5)
    triad_1_options.sort()
    triad_1_options = list(chord_1_options for chord_1_options,_ in itertools.groupby(triad_1_options))

    triad_2_options = gen_triad_options(2) + gen_triad_options(2, double_note=5)
    triad_2_options.sort()
    triad_2_options = list(chord_2_options for chord_2_options,_ in itertools.groupby(triad_2_options))

    triad_3_options = gen_triad_options(3) + gen_triad_options(3, double_note=3) # CAN'T DOUBLE 5th B/C ITS A LEADING TONE!
    triad_3_options.sort()
    triad_3_options = list(chord_3_options for chord_3_options,_ in itertools.groupby(triad_3_options))

    triad_4_options = gen_triad_options(4) + gen_triad_options(4, double_note=5)
    triad_4_options.sort()
    triad_4_options = list(chord_4_options for chord_4_options,_ in itertools.groupby(triad_4_options))

    triad_5_options = gen_triad_options(5) + gen_triad_options(5, double_note=5)
    triad_5_options.sort()
    triad_5_options = list(chord_5_options for chord_5_options,_ in itertools.groupby(triad_5_options))

    triad_6_options = gen_triad_options(6) + gen_triad_options(6, double_note=5)
    triad_6_options.sort()
    triad_6_options = list(chord_6_options for chord_6_options,_ in itertools.groupby(triad_6_options))

    triad_7_options = gen_triad_options(7, double_note=3) # DIMINISHED! Double the third

    all_triad_options = [triad_1_options, triad_2_options, triad_3_options, triad_4_options, triad_5_options, triad_6_options, triad_7_options]

    chord_dict = {}
    state_dict = {}

    index = 0
    for chord_options in all_triad_options:
        for c_opt in chord_options:
            state_dict[index] = c_opt
            index+=1

    for i, chord_options in enumerate(all_triad_options):
        chord_dict[i+1] = []
        for j, c_opt in enumerate(chord_options):
            key = next(key for key, value in state_dict.items() if value == c_opt)
            #print(i, j, c_opt)
            name = "chord_" + str(i+1) + '_' + str(j)
            chord_dict[i+1].append(key)

    with open("voicing_state_dict.yaml", 'w') as outfile:
        yaml.dump(chord_dict, outfile, default_flow_style=False)
    with open("chord_dict.yaml", 'w') as outfile:
        yaml.dump(chord_dict, outfile, default_flow_style=False)

    with open("voicing_state_indices.yaml", 'w') as outfile:
        yaml.dump(state_dict, outfile, default_flow_style=False)
    with open("state_dict.yaml", 'w') as outfile:
        yaml.dump(state_dict, outfile, default_flow_style=False)

    inverse_chord_dict = {}
    for key in chord_dict:
        print("KEY")
        for idx in chord_dict[key]:
            print("IDX:", idx)
            inverse_chord_dict[idx] = key

    with open("inverse_chord_dict.yaml", 'w') as outfile:
        yaml.dump(inverse_chord_dict, outfile, default_flow_style=False)

    