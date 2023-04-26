import random
import yaml
import numpy as np 

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

        with open('voicing_state_dict.yaml', 'r') as file:
            self.state_dict = yaml.safe_load(file)

        with open('voicing_state_indices.yaml', 'r') as file:
            self.state_indices = yaml.safe_load(file)

        self.Qvalues = np.zeros((148,148))
        self.reward_matrix = np.zeros((148,148)) # there are 148 chord states
        # NEED TO UPDATE REWARDS MATRIX!
        

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
          Returns max_action Q(state,next_state)
          where the max is over options for next_state.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        if next_chord not in self.state_dict.keys():
            return 0.0
        next_states = self.state_dict[next_chord]
        #print("ACTIONS:", actions)
        if next_states == None or len(next_states) == 0:
            #print("NO LEGAL ACTIONS! (CVFQV)\n", state)
            #input("continue...")
            return 0.0
        
        action_val_pairs = []
        for next_state in next_states:
            curQ = self.getQValue(state, next_state)
            action_val_pairs.append((next_state, curQ))
        # sort list of tuples
        action_val_pairs.sort(key = lambda x: x[1], reverse=True) 
        return action_val_pairs[0][1] # chose max value

    def computeActionFromQValues(self, state, next_chord):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        if next_chord not in self.state_dict.keys():
            print("NO LEGAL ACTIONS")
            return None
        next_states = self.state_dict[next_chord]
        if next_states == None or len(next_states) == 0:
            return None
        
        action_val_pairs = []
        for next_state in next_states:
            curQ = self.getQValue(state, next_state)
            action_val_pairs.append((next_state, curQ))
        # sort list of tuples
        action_val_pairs.sort(key = lambda x: x[1], reverse=True) 

        return action_val_pairs[0][0]

    def getAction(self, next_chord, state=None): # first time won't have a state
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """
        print(next_chord)
        if next_chord == -1:
            print("NO LEGAL MOVE!")
            return None
        legal_actions = self.state_dict[next_chord]
        if state is None: ### INITIAL STATE, CHOOSE RANDOMLY? OR CHOOSE ONE WITH HIGHEST Q VAL ###
            return random.choice(legal_actions)
        else: 
            best_action = self.computeActionFromQValues(state, next_chord)
            if flipCoin(self.epsilon):
                return random.choice(legal_actions) # this includes the best action... is that what i want? 
            else: 
                return best_action

    def update(self, state, next_state, reward, next_chord):
        """
          The parent class calls this to observe a
          state = action => next_state and reward transition.
          You should do your Q-Value update here
        """
        cur_qval = self.getQValue(state, next_state)
        # HAVE A Q VAL FOR EACH STATE-STATE PAIR
        next_best_qval = self.computeValueFromQValues(next_state, next_chord)
        # Will just be 0 if terminal
        self.Qvalues[(state, next_state)] = cur_qval + self.alpha*(reward + self.gamma*next_best_qval - cur_qval)

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)
    

###  TRAINING LOOP ###
agent = QLearningAgent()
all_epochs = []
all_penalties = []
chord_progression = [1, 4, 5, 1, -1]
for i in range(1,10):
    epochs, penalties, reward = 0,0,0
    done = False
    for i, c in enumerate(chord_progression):
        if chord_progression[i+1] == -1: # DONE WITH LOOP!
            break
        if i == 0:
            # choose starting state
            cur_state = agent.getAction(chord_progression[i])

        # choose an action
        chosen_action = agent.getAction(chord_progression[i+1], cur_state)
        # peform the chosen action and transition to the next state
        next_state = chosen_action

        # receive reward
        reward = agent.reward_matrix[cur_state, next_state]
        
        # update q_val
        agent.update(cur_state, next_state, reward, chord_progression[i+2])

        # if new state is terminal, go back to 1
        # else, go to 2