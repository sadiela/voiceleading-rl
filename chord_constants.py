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