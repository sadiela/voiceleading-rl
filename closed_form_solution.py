### Load in the state dictionaries ###
import random
import yaml
import numpy as np 
from MIDI_conversion import *
from voice_leading_rules import *
import copy
import pretty_midi

def get_transition_options(cur_state, next_chord, adjacency_mat, chord_dict):
    next_state_options = []
    next_chord_states = chord_dict[next_chord]
    #print("TOTAL NUMBER OF LEGAL PATHS:", sum(adjacency_mat[cur_state,min(next_chord_states):max(next_chord_states)]))
    for state in next_chord_states: 
        if adjacency_mat[cur_state, state] == 1:
            next_state_options.append(state)
    return next_state_options

def get_progression_options(progression, adjacency_mat, chord_dict):
    progression_options = []
    first_chord_options = chord_dict[progression[0]] # all potential start points
    for chord in first_chord_options:
        progression_options.append([chord])
    print(progression_options)
    for i, chord in enumerate(progression):
        print(i, chord)
        if i != 0:
            old_options = copy.deepcopy(progression_options)
            progression_options = []
            for prog in old_options:
                # chord is the next chord
                transition_choices = get_transition_options(prog[-1], chord, adjacency_mat, chord_dict)
                if len(transition_choices) == 0:
                    print("NO LEGAL PROGRESSIONS FROM THIS STARTING POINT:", prog[-1], chord)
                else: 
                    for choice in transition_choices:
                        new_prog = copy.deepcopy(prog)
                        new_prog.append(choice)
                        if new_prog not in progression_options:
                            progression_options.append(new_prog)
                        else:
                            print("DUPLICATE PROGRESSION")
            #print(len(progression_options))
            #input("CONTINUE...")
    return progression_options

def calc_adjacency_matrix(numStates, inverse_chord_dict, state_indices):
    rewards = np.zeros((numStates,numStates))
    adjaceny_matrix = np.zeros((numStates,numStates))

    num_legal_transitions = 0
    for i in range(numStates):
        for j in range(numStates):
            cur_reward, _,_,_,_ = calculateRewards(i,j)
            if cur_reward == 0:
                if inverse_chord_dict[i] != inverse_chord_dict[j]:
                    print(state_indices[i],state_indices[j])
                    num_legal_transitions += 1
                    adjaceny_matrix[i,j] = 1
                    rewards[i,j] = cur_reward
                else:
                    print("No transition between two states that are the same chord")

    # save rewards matrix
    np.save('closed_form_rewards.npy', rewards)
    np.save('closed_form_adjacency_mat.npy', adjaceny_matrix)
    print(rewards)
    print("LEGAL TRANSITIONS:", num_legal_transitions)
    return adjaceny_matrix

def calculateRewards(state, next_state):
    # i is starting state, j is next state
    cur_start = state_indices[state]
    cur_end = state_indices[next_state]
    # negative reward for voice crossing
    voice_cross = voice_crossing(cur_start, cur_end)
    # negative reward for parallel 5ths/octaves
    p58 = parallel_fifths_and_octaves(cur_start, cur_end)
    ill = illegal_leaps(cur_start, cur_end)
    d58 = direct_fifths_octaves(cur_start, cur_end)
    reward = -.2*voice_cross + -.1*p58 + -.2*ill + -.1*d58

    return reward, voice_cross, p58, ill, d58

if __name__ == "__main__":
    numStates = 148
    with open('chord_dict.yaml', 'r') as file:
        chord_dict = yaml.safe_load(file)

    with open('voicing_state_indices.yaml', 'r') as file:
        state_indices = yaml.safe_load(file)

    with open('inverse_chord_dict.yaml', 'r') as file:
        inverse_chord_dict = yaml.safe_load(file)

    adjacency_matrix = calc_adjacency_matrix(numStates, inverse_chord_dict, state_indices)

    cur_state = 5
    next_chord = 3
    print("ONE TRANSITION")
    print(get_transition_options(cur_state, next_chord, adjacency_matrix, chord_dict))

    progression = [1,6,4,2]
    progression2 = [2,7,5,1]
    progression3 = [1,2,5,1]
    print("PROGRESSION:")
    progression_options = get_progression_options(progression, adjacency_matrix, chord_dict)
    progression_options_2 = get_progression_options(progression2, adjacency_matrix, chord_dict)
    progression_options_3 = get_progression_options(progression3, adjacency_matrix, chord_dict)
    print(len(progression_options), len(progression_options_2), len(progression_options_3))
    '''print(progression_options[0])

    for chord in progression_options[0]:
        print("CHORD:", chord)
        chord_notes = state_indices[chord]
        print(chord_notes)
        for note in chord_notes: 
            print(pretty_midi.note_number_to_name(note))'''
