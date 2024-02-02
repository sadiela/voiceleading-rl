# Ranges typical of 4-part choral music. These can be changed 
# at the user's discretion
# TRAINING DATA RANGES:
# MINS: [31 43 50 55] 
# MAXES: [67 74 79 84]
# [55, 84] [50, 79] [43, 74] [31, 67] # satb
bass_range = list(range(31,68))
tenor_range = list(range(43,75)) 
alto_range = list(range(50,80)) 
soprano_range = list(range(55,85)) # FINAL INDEX NOT INCLUDED!

# These are lists of all pitches of a certain note within
# the specified range (40-80 for us)
# VERIFIED!
notesets = [[], # Cs     0 (0,2,4,5,7,9,11)
            [], # C#Db   1
            [], # D      2
            [], # D#Eb   3
            [], # E      4
            [], # F      5
            [], # F#Gb   6
            [], # G      7
            [], # G#Ab   8
            [], # A      9
            [], # A# Bb  10
            []] # B      11

for note in range(bass_range[0], soprano_range[-1]+1):
    notesets[note%12].append(note)

# list of notes that occur in each chord in C major
# 0 = C, 2 = D, etc. 
notes_in_chords = {
    1: [0,4,7], # C
    2: [2,5,9], # d
    3: [4,7,11], # e
    4: [5,9,0], # F
    5: [7,11,2], # G
    6: [9,0,4], # a
    7: [11,2,5], # b
    8: [2,5,9,0], # 2 7th
    9: [5,9,0,4], # 4 7th 
    10: [7,11,2,5], # 5 7th 
    11: [11,2,5,9] # 7 7th
}

chord_number_to_string_major = {
    1: "I",
    2: "ii",
    3: "iii",
    4: "IV",
    5: "V", 
    6: "vi",
    7: "vii(dim)",
    8: "ii",
    9: "IV",
    10: "V", 
    11: "vii(dim)"
}

inversion_numbers_triad = {
    0: "",
    1: "6",
    2: "6/4"
}
    
inversion_numbers_seventh = {
    0: "7",
    1: "6/5",
    2: "4/3",
    3: "4/2"
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

# notes in the scale of each major/minor key
notes_in_keys = {
    #        C D E F G A B
    "C/a":    [0,2,4,5,7,9,11], # C!
    "G/e":    [0,2,4,6,7,9,11], #  F#
    "D/b":    [1,2,4,6,7,9,11], # +C#
    "A/f#":    [1,2,4,6,8,9,11], # +G#
    "E/c#":    [1,3,4,6,8,9,11], # +D#
    "B-Cb/g#": [1,3,4,6,8,10,11], # +A#
    "Gb-F#/eb":[1,3,5,6,8,10,11], # +E#
    "Db-C#/bb":[0,1,3,5,6,8,10], # +B#
    "Ab/f":   [0,1,3,5,7,8,10], # +Db
    "Eb/c":   [0,2,3,5,7,8,10], # +Ab
    "Bb/g":   [0,2,3,5,7,9,10], # +Eb 
    "F/d":    [0,2,4,5,7,9,10]  # +Bb
}

maj_min_tonics = {
    #        C D E F G A B
    "C/a":  {'maj': [0,4,7],'min': [0,4,9]}, # ACE
    "G/e":  {'maj': [2,7,11],'min': [4,7,11]},  # EGB
    "D/b":  {'maj': [2,6,9],'min': [2,6,11]},  # +C#
    "A/f#":   {'maj': [1,4,9],'min': [1,6,9]}, # +G#
    "E/c#":    {'maj': [4,8,11],'min': [1,4,8]}, # +D#
    "B-Cb/g#": {'maj': [3,6,11],'min': [3,8,11]}, # +A#
    "Gb-F#/eb":{'maj': [1,6,10], 'min': [3,6,10]}, # +E#
    "Db-C#/bb":{'maj': [1,5,8], 'min': [1,5,10]}, # +B#
    "Ab/f":   {'maj': [0,3,8], 'min': [0,5,8]} , # +Db
    "Eb/c":   {'maj': [3,7,10], 'min': [0,3,7]} , # +Ab
    "Bb/g":   {'maj': [2,5,10], 'min': [2,7,10]},# +Eb 
    "F/d":    {'maj': [0,5,9], 'min': [2,5,9]}   # +Bb
}

key_shift_amount = { # move the least amount possible, so sometimes add, sometimes subtract
    "C/a":      0, # C!
    "G/e":      5, #  F# 
    "D/b":      -2, # +C#
    "A/f#":     3, # +G#
    "E/c#":     -4, # +D#
    "B-Cb/g#":  1, # +A#
    "Gb-F#/eb": -6, # +E#
    "Db-C#/bb": -1,#-1, # +B# 
    "Ab/f":     4, # +Db
    "Eb/c":     -3, # +Ab
    "Bb/g":     2, # +Eb 
    "F/d":      -5   # +Bb
}