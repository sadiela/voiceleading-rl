from state_space_def import *

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

def harmonic_prog_reward_major(state, next_state): 
    chord_1 = determine_chord_from_voicing(state)
    chord_2 = determine_chord_from_voicing(next_state)
    if major_harmonic_adjacency_matrix[chord_1][chord_2] == 0:
        return 1
    elif major_harmonic_adjacency_matrix[chord_1][chord_2] == -1:
        return 2
    return 0 


def harmonic_prog_reward_minor(state, next_state): 
    chord_1 = determine_chord_from_voicing(state)
    chord_2 = determine_chord_from_voicing(next_state)

    return 0 

if __name__ == "__main__":
    print("Testing harmonic progression rules (major)")
