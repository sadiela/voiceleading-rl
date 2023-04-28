
import random
import itertools
import yaml
import pretty_midi

# pretty_midi.note_number_to_name(note_number) CHECK DICTS!


bass_range = list(range(40,61))
tenor_range = list(range(48,68)) 
alto_range = list(range(55,75)) 
soprano_range = list(range(60,80)) # FINAL INDICE NOT INCLUDED!

As = list(range(45, 80, 12)) 
Bs = list(range(47, 80, 12)) 
Cs = list(range(48, 80, 12)) 
Ds = list(range(50, 80, 12)) 
Es = list(range(40, 80, 12)) 
Fs = list(range(41, 80, 12)) 
Gs = list(range(43, 80, 12)) 

notes_in_chords = {
    1: [Cs, Es, Gs],
    2: [Ds, Fs, As],
    3: [Es, Gs, Bs],
    4: [Fs, As, Cs],
    5: [Gs, Bs, Ds],
    6: [As, Cs, Es],
    7: [Bs, Ds, Fs]
}

def determine_chord_validity(cur_combo, root):
    # takes SORTED note list
    if cur_combo[0] in root:
        if cur_combo[0] in bass_range and cur_combo[1] in tenor_range and cur_combo[2] in alto_range and cur_combo[3] in soprano_range:
            if cur_combo[2] - cur_combo[1] <= 12 and cur_combo[3] - cur_combo[2] <= 12:
                return True
    return False


def gen_triad_options(chord_num, double_note=1):
    chord_options = []
    root, third, fifth = notes_in_chords[chord_num] # need one of each, but they can be in any position besides the root
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
    print("As:")
    for a in As: 
        print(pretty_midi.note_number_to_name(a))

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
        print(pretty_midi.note_number_to_name(g))

    chord_1_options = gen_triad_options(1) + gen_triad_options(1, double_note=5)
    chord_1_options.sort()
    chord_1_options = list(chord_1_options for chord_1_options,_ in itertools.groupby(chord_1_options))

    chord_2_options = gen_triad_options(2) + gen_triad_options(2, double_note=5)
    chord_2_options.sort()
    chord_2_options = list(chord_2_options for chord_2_options,_ in itertools.groupby(chord_2_options))

    chord_3_options = gen_triad_options(3) + gen_triad_options(3, double_note=5)
    chord_3_options.sort()
    chord_3_options = list(chord_3_options for chord_3_options,_ in itertools.groupby(chord_3_options))

    chord_4_options = gen_triad_options(4) + gen_triad_options(4, double_note=5)
    chord_4_options.sort()
    chord_4_options = list(chord_4_options for chord_4_options,_ in itertools.groupby(chord_4_options))

    chord_5_options = gen_triad_options(5) + gen_triad_options(5, double_note=5)
    chord_5_options.sort()
    chord_5_options = list(chord_5_options for chord_5_options,_ in itertools.groupby(chord_5_options))

    chord_6_options = gen_triad_options(6) + gen_triad_options(6, double_note=5)
    chord_6_options.sort()
    chord_6_options = list(chord_6_options for chord_6_options,_ in itertools.groupby(chord_6_options))

    chord_7_options = gen_triad_options(7, double_note=3) # DIMINISHED! Double the third

    all_chord_options = [chord_1_options, chord_2_options, chord_3_options, chord_4_options, chord_5_options, chord_6_options, chord_7_options]

    state_dict = {}
    state_indices = {}

    index = 0
    for chord_options in all_chord_options:
        for c_opt in chord_options:
            state_indices[index] = c_opt
            index+=1

    for i, chord_options in enumerate(all_chord_options):
        state_dict[i+1] = []
        for j, c_opt in enumerate(chord_options):
            key = next(key for key, value in state_indices.items() if value == c_opt)
            #print(i, j, c_opt)
            name = "chord_" + str(i+1) + '_' + str(j)
            state_dict[i+1].append(key)

    with open("voicing_state_dict.yaml", 'w') as outfile:
        yaml.dump(state_dict, outfile, default_flow_style=False)

    with open("voicing_state_indices.yaml", 'w') as outfile:
        yaml.dump(state_indices, outfile, default_flow_style=False)