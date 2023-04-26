


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
    def __init__(self, **args):
        self.Qvalues = util.Counter()

    def getQValue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        "*** YOUR CODE HERE ***"
        return self.Qvalues[(state,action)] # do I have to do something to handle when we've never sean a state? 
        #util.raiseNotDefined()


    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        actions = self.getLegalActions(state)
        #print("ACTIONS:", actions)
        if actions == None or len(actions) == 0:
            #print("NO LEGAL ACTIONS! (CVFQV)\n", state)
            #input("continue...")
            return 0.0
        
        action_val_pairs = []
        for action in actions:
            curQ = self.getQValue(state, action)
            action_val_pairs.append((action, curQ))
        # sort list of tuples
        action_val_pairs.sort(key = lambda x: x[1], reverse=True) 
        return action_val_pairs[0][1]

        #util.raiseNotDefined()

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        "*** YOUR CODE HERE ***"
        legalActions = self.getLegalActions(state) # choose max
        if legalActions == None or len(legalActions) == 0:
            print("NO LEGAL ACTIONS! (CAFQV)\n", state)
            #input("continue...")
            return None
        action_val_pairs = []
        for action in legalActions:
            curQ = self.getQValue(state, action)
            action_val_pairs.append((action, curQ))
        # sort list of tuples
        action_val_pairs.sort(key = lambda x: x[1], reverse=True) 
        #print(action_val_pairs, action_val_pairs[0][0])
        #input("Continue...")
        return action_val_pairs[0][0]

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.

          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """
        # Pick Action
        legalActions = self.getLegalActions(state)
        if legalActions == None or len(legalActions) == 0:
            print("NO LEGAL ACTIONS: GA")
            #input("Continue...")
            return None
        best_action = self.computeActionFromQValues(state)
        if util.flipCoin(self.epsilon):
            return random.choice(legalActions) # this includes the best action... is that what i want? 
        else: 
            return best_action

    def update(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

          NOTE: You should never call this function,
          it will be called on your behalf
        """
        "*** YOUR CODE HERE ***" # should this return?
        cur_qval = self.getQValue(state,action)
        #print("Cur qval", cur_qval)
        next_best_qval = self.computeValueFromQValues(nextState)
        self.Qvalues[(state,action)] = cur_qval + self.alpha*(reward + self.discount*next_best_qval - cur_qval)
        #util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)