### Load in the state dictionaries ###
import random
import yaml
import numpy as np 
from MIDI_conversion import *
from voice_leading_rules import *

numStates = 148
with open('voicing_state_dict.yaml', 'r') as file:
    state_dict = yaml.safe_load(file)

with open('voicing_state_indices.yaml', 'r') as file:
    state_indices = yaml.safe_load(file)

def calculateRewards(self, state, next_state):
    reward = 0
    # i is starting state, j is next state
    cur_start = state_indices[state]
    cur_end = state_indices[next_state]
    # negative reward for voice crossing
    voice_cross = voice_crossing(cur_start, cur_end)
    # negative reward for parallel 5ths/octaves
    p58 = parallel_fifths_and_octaves(cur_start, cur_end)

    ill = illegal_leaps(cur_start, cur_end)

    d58 = direct_fifths_octaves(cur_start, cur_end)

    return -.2*voice_cross + -.1*p58 + -.2*ill + -.1*d58, voice_cross, p58, ill, d58

rewards = np.zeros((numStates,numStates))

for i in range(numStates):
    for j in range(numStates):
        rewards[i,j] = calculateRewards(i,j)

# save rewards matrix
np.save(rewards, 'closed_form_rewards.npy')
