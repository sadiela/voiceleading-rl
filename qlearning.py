import random
import yaml
import numpy as np 
from MIDI_conversion import *
from voice_leading_rules import *

results_dir = './results/'

def flipCoin(p):
  r = random.random()
  return r < p 

class QLearningAgent():
    """
      Q-Learning Agent
      Functions you should fill in:
        - computeValueFromQValues
        - computeActionFromQValues
        - getQValue
        - getAction
        - update
    """
    def __init__(self):
        self.alpha = 0.1
        self.gamma = 0.6
        self.epsilon = 0.1
        self.Qvalues = 0 # some matrix
        self.numStates = 148

        with open('voicing_state_dict.yaml', 'r') as file:
            self.state_dict = yaml.safe_load(file)

        with open('voicing_state_indices.yaml', 'r') as file:
            self.state_indices = yaml.safe_load(file)

        self.Qvalues = np.zeros((self.numStates,self.numStates))
        
    def calculateRewards(self, state, next_state):
        reward = 0
        # i is starting state, j is next state
        cur_start = self.state_indices[state]
        cur_end = self.state_indices[next_state]
        # negative reward for voice crossing
        voice_cross = voice_crossing(cur_start, cur_end)
        # negative reward for parallel 5ths/octaves
        p58 = parallel_fifths_and_octaves(cur_start, cur_end)

        ill = illegal_leaps(cur_start, cur_end)

        d58 = direct_fifths_octaves(cur_start, cur_end)

        return -.2*voice_cross + -.1*p58 + -.2*ill + -.1*d58, voice_cross, p58, ill, d58

    def getQValue(self, state, next_state):
        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        "*** YOUR CODE HERE ***"
        return self.Qvalues[(state,next_state)] # do I have to do something to handle when we've never sean a state? 
        #util.raiseNotDefined()


    def computeValueFromQValues(self, state, next_chord):
        """
          Returns max_action Q(state,action)
          where the max is over options for action.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        if next_chord not in self.state_dict.keys(): # no legal actions
            return 0.0
        next_actions = self.state_dict[next_chord]
        #print("ACTIONS:", actions)
        if next_actions == None or len(next_actions) == 0: # no legal actions
            return 0.0
        
        action_val_pairs = []
        for next_action in next_actions:
            curQ = self.getQValue(state, next_action)
            action_val_pairs.append((next_action, curQ))
        # sort list of tuples
        action_val_pairs.sort(key = lambda x: x[1], reverse=True) 
        return action_val_pairs[0][1] # chose max value

    def computeActionFromQValues(self, state, next_chord):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
          The legal actions are determined by the next_chord argument
        """
        if next_chord not in self.state_dict.keys():
            print("NO LEGAL ACTIONS")
            return None
        next_actions = self.state_dict[next_chord]
        if next_actions == None or len(next_actions) == 0:
            return None
        
        action_val_pairs = []
        for next_action in next_actions:
            curQ = self.getQValue(state, next_action) # which transition gives highest q? 
            action_val_pairs.append((next_action, curQ))
        # sort list of tuples
        action_val_pairs.sort(key = lambda x: x[1], reverse=True) 

        return action_val_pairs[0][0]

    def getAction(self, next_chord, state=None, best=False): # first time won't have a state
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
          Legal actions are determined by next_chord
        """
        #print(next_chord)
        if next_chord == -1:
            print("NO LEGAL MOVE!")
            return None
        legal_actions = self.state_dict[next_chord]
        if state is None: ### INITIAL STATE, CHOOSE RANDOMLY? OR CHOOSE ONE WITH HIGHEST Q VAL ###
            return random.choice(legal_actions)
        else: 
            best_action = self.computeActionFromQValues(state, next_chord)
            if best==True:
                return best_action
            else: 
                if flipCoin(self.epsilon):
                    return random.choice(legal_actions) # this includes the best action... is that what i want? 
                else: 
                    return best_action

    def update(self, state, action, reward, next_chord):
        """
          The parent class calls this to observe a
          state = action => next_state and reward transition.
          You should do your Q-Value update here
        """
        cur_qval = self.getQValue(state, action)
        # HAVE A Q VAL FOR EACH STATE-STATE PAIR
        next_best_qval = self.computeValueFromQValues(action, next_chord)
        # Will just be 0 if terminal
        self.Qvalues[(state, action)] = cur_qval + self.alpha*(reward + self.gamma*next_best_qval - cur_qval)

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)
    
    def evalAgent(self, chord_progression, num_voicings, fname=None, synth=False):
        all_voicings = []
        for i in range(num_voicings):
            print("VOICING:", i)
            state_list = []
            total_reward = 0
            num_voice_crossings = 0
            num_parallels = 0
            num_illegal_leaps = 0
            num_direct = 0
            for j, c in enumerate(chord_progression):
                if chord_progression[j+1] == -1: # DONE WITH LOOP!
                    break
                if j == 0: # choose starting state
                    cur_state = self.getAction(chord_progression[j], best=True)
                    state_list.append(cur_state)

                # choose an action (i.e., the next state)
                chosen_action = self.getAction(chord_progression[j+1], cur_state, best=True)
                
                next_state = chosen_action
                state_list.append(next_state)

                reward, vc,p58,il,d58 = self.calculateRewards(cur_state, chosen_action)
                num_voice_crossings += vc
                num_parallels += p58
                num_illegal_leaps += il  
                num_direct += d58
                
                total_reward += reward

            print("Total reward and sequence:", total_reward, state_list)
            if state_list not in all_voicings:
                state_seq_to_MIDI(state_list, self.state_indices, desired_fstub=fname)
                all_voicings.append(state_list)
            else:
                print("Already saved voicing")
            print("Num voice crossings:", num_voice_crossings, "\nNum parallels:", num_parallels, "\nNum illegal leaps:", num_illegal_leaps, "\nNum direct fifths/octaves", num_direct)
            # EVALUATE STATE LIST

        if synth:
            midis_to_wavs(results_dir)


###  TRAINING LOOP ###
agent = QLearningAgent()
all_epochs = []
all_penalties = []
chord_progressions = [
    [1, 4, 5, 1, -1],
    [1, 6, 2, 5, 1, -1],
    [1, 4, 7, 3, 6, 2, 5, 1, -1],
    [1, 6, 4, 2, 7, 5, 1,-1]
                    ]
for chord_prog in chord_progressions:
    for i in range(1,10000):
        epoch_reward = 0
        for j, c in enumerate(chord_prog):
            if chord_prog[j+1] == -1: # DONE WITH LOOP!
                break
            if j == 0:
                # choose starting state
                cur_state = agent.getAction(chord_prog[j])

            # choose an action
            chosen_action = agent.getAction(chord_prog[j+1], cur_state)
            # peform the chosen action and transition to the next state
            next_state = chosen_action

            # receive reward
            reward, _,_,_,_ = agent.calculateRewards(cur_state, next_state)
            epoch_reward += reward
            
            # update q_val
            agent.update(cur_state, next_state, reward, chord_prog[j+2])

        if i % 1000 == 0:
            print("Reward for epoch", i, ":", epoch_reward)
print(np.sum(agent.Qvalues))

print("EVALUATING")
# EVALUATE
chord_progression = [1, 4, 5, 1, -1] 


falling_fifths = [1, 4, 7, 3, 6, 2, 5, 1, -1]
falling_thirds = [1,6,4,2,7,5,1,-1]
agent.evalAgent(falling_thirds, 5, synth=True, fname='falling_thirds')