
import yaml 
import numpy as np
import random
from tqdm import tqdm
from MIDI_conversion import *
from voice_leading_rules import *
import pickle
from datetime import datetime
import glob


def flipCoin(p):
  r = random.random()
  return r < p 

class Qlearner():
    def __init__(self, alpha=0.1, gamma=.9, epsilon_init=0.5, epsilon_end=0.0, epochs=10000):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon_init = epsilon_init 
        self.epsilon_end = epsilon_end
        self.Qvalues = 0 # some matrix

        with open('./dictionaries/chord_dict_3.yaml', 'r') as file:
            self.chord_dict = yaml.safe_load(file)

        with open('./dictionaries/state_dict_3.yaml', 'r') as file:
            self.state_indices = yaml.safe_load(file)

        self.numStates = len(self.state_indices.keys())
        #print("NUMSTATES:", self.numStates)

        self.Qvalues = np.zeros((self.numStates,self.numStates))

    def saveModel(self, epochs, rewards): # saved model is just a matrix of the Q values :)
        data = {
            "Q": self.Qvalues,
            "epochs": epochs,
            "rewards": rewards
        }

        modelpath = './models/'+ self.model_name + datetime.today().strftime("%m_%d") + '_' + str(epochs) + '.p'

        with open(modelpath, 'wb') as f:
            pickle.dump(data, f)
        #np.save(modelpath, self.Qvalues)

    def loadModel(self, modelpath):
        with open(modelpath, 'rb') as f: 
            data = pickle.load(f)
        self.Qvalues = data['Q']
        return data['rewards'], data['epochs']
        #self.Qvalues = np.load(modelpath)
    
    def prepModel(self, model_name):
        epoch_rewards, completed_epochs = [],0
        path_form = './models/' + model_name + '*.p'
        list_of_files = glob.glob(path_form) # * means all if need specific format then *.csv
        if len(list_of_files) !=0:
            latest_file = max(list_of_files, key=os.path.getctime)
            print(latest_file)
            epoch_rewards, completed_epochs = self.loadModel(latest_file)
        
        self.model_name = model_name
        return epoch_rewards, completed_epochs, latest_file
    
    def getQValue(self, state, next_state):
        return self.Qvalues[(state,next_state)]
    
    def calculateRewards(self, state, next_state):
        # for this model, don't care about harmonic progression rewards
        # i is starting state, j is next state
        cur_start = self.state_indices[state]
        cur_end = self.state_indices[next_state]
        return self.rewardFunction(cur_start, cur_end)

    '''def getPolicy(self, state):
        action, val = self.computeActionValuesFromQValues(state)
        return action'''

    def getValue(self, state):
        return self.computeValueFromQValues(state)
    
    def getLegalActions(self, context=None):
        return list(range(0,self.numStates))
    
    def computeActionValuesFromQValues(self, state, legal_actions): 
        ### DO SOME ERROR CHECKING
        if len(legal_actions)==0:
            return None, 0.0
        action_val_pairs = [] 
        for next_action in legal_actions: 
            curQ = self.getQValue(state, next_action)
            action_val_pairs.append((next_action, curQ))
        action_val_pairs.sort(key=lambda x: x[1], reverse=True)
        #print(action_val_pairs[0:5])
        #input("Continue...")
        return action_val_pairs[0]
    
    def getAction(self, state=None, context=-2, best=False, rand=False): # Set rand = TRUE for baseline comparison
        #print("Context", context, state)
        if context==-1:
            print("NO LEGAL MOVE")
            return None 
        legal_actions = self.getLegalActions(context)
        if rand == True: # USE FOR BASELINE!!!!
            return random.choice(legal_actions)
        if state is None:
            return random.choice(legal_actions) # choose initial state randomly
        else:
            best_action, _ = self.computeActionValuesFromQValues(state, legal_actions)
            if best:
                return best_action
            else: 
                if flipCoin(self.epsilon): # epsilon-greedy!
                    return random.choice(legal_actions) # this includes the best action... is that what i want? 
                else: 
                    return best_action
                
    def update(self, state, action, reward, context=None):
        cur_qval=self.getQValue(state,action)
        legal_actions = self.getLegalActions(context=context) # context can be multiple notes for harmonization model? 
        _, next_best_qval = self.computeActionValuesFromQValues(state=action, legal_actions=legal_actions)
        self.Qvalues[(state, action)] = cur_qval + self.alpha*(reward + self.gamma*next_best_qval - cur_qval)
 
# Class freelancer inherits EMP
class VoicingModel(Qlearner):
    def __init__(self, alpha=0.1, gamma=0.6,  checkpoint=500, resultsdir='./results/voicing_results/'):
        super().__init__(alpha, gamma)
        self.results_dir = resultsdir
        self.rewardFunction = voice_leading_reward_function
        self.checkpoint = checkpoint
    
    def getLegalActions(self, context=None):
        if context==None:
            print("ERROR, CHORD NOT PROVIDED")
            sys.exit(-1)
        if context == -1: 
            return []
        return self.chord_dict[context]
                
    def trainAgent(self, chord_progressions, num_epochs=1000, epoch_rewards=[]):
        self.alpha_steps = [self.alpha*np.log(step) for step in np.linspace(np.e, 1, num_epochs)]
        print("CHECKPOINT", self.checkpoint)
        for i in tqdm(range(len(epoch_rewards)+1,num_epochs)):
            # will start close to epsilon_init and move closer to epsilon_end as i increases
            epoch_reward = 0
            self.alpha = self.alpha_steps[i]
            self.epsilon = (self.epsilon_init-self.epsilon_end)*((num_epochs - i)/num_epochs) + self.epsilon_end
            if i%self.checkpoint == 0:
                print("epoch:", i, epoch_reward)
                self.saveModel(i, epoch_rewards)
            for chord_prog in chord_progressions:
                for j, c in enumerate(chord_prog):
                    if chord_prog[j+1] == -1: # DONE WITH LOOP!
                        break
                    if j == 0:
                        # choose starting state
                        cur_state = self.getAction(context=chord_prog[j])
                    # choose an action
                    chosen_action = self.getAction(state=cur_state, context=chord_prog[j+1])
                    next_state = chosen_action # peform the chosen action and transition to the next state

                    # receive reward
                    reward,_,_,_,_,_,_,_ = self.calculateRewards(cur_state, next_state)
                    epoch_reward += reward
                    # update q_val
                    self.update(cur_state, next_state, reward, context=chord_prog[j+2])
                    cur_state=next_state

            epoch_rewards.append(epoch_reward)
        return epoch_rewards   

    def evalAgent(self, chord_progression, num_voicings, fname=None, synth=False, rand=False): # set rand=True for random baseline!
        all_voicings = []
        all_rewards = [] 
        for i in range(num_voicings): # create num_voicings voicings for the given chord progression!
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
                    cur_state = self.getAction(context=chord_progression[j], best=True, rand=rand)
                    state_list.append(cur_state)

                # choose an action (i.e., the next state)
                chosen_action = self.getAction(state=cur_state, context=chord_progression[j+1], best=True, rand=rand)
                
                next_state = chosen_action
                state_list.append(next_state)

                reward, vc, p58, il, d58, lt, ct, sev = self.calculateRewards(cur_state, chosen_action)
                num_voice_crossings += vc
                num_parallels += p58
                num_illegal_leaps += il  
                num_direct += d58
                
                total_reward += reward
                cur_state=next_state

            all_rewards.append(total_reward)

            print("Total reward and sequence:", total_reward, state_list, chord_strings(state_list, self.state_indices))
            if state_list not in all_voicings:
                state_seq_to_MIDI(state_list, self.state_indices, self.results_dir, desired_fstub=fname)                
                all_voicings.append(state_list)
                all_rewards.append(total_reward)
            else:
                print("Already saved voicing")
            print("Num voice crossings:", num_voice_crossings, "\nNum parallels:", num_parallels, "\nNum illegal leaps:", num_illegal_leaps, "\nNum direct fifths/octaves", num_direct)
            # EVALUATE STATE LIST

        if synth:
            midis_to_wavs(self.results_dir)

        return all_voicings, all_rewards 

    def fullEvalAgent(self, chord_progs, fname=None, synth=False, rand=False): # set rand=True to compare to random baseline 
        all_voicings = []
        all_vl_rewards = []
        all_vc = []
        all_parallels = []
        all_illegal_leaps = []
        all_direct = []
        all_lt = [] 
        all_ct = [] 
        all_sev = [] 
        for prog in chord_progs:
            state_list = []
            cur_vl_reward = 0
            num_voice_crossings = 0
            num_parallels = 0
            num_illegal_leaps = 0
            num_direct = 0
            num_lt = 0
            num_ct = 0 
            num_sev = 0
            for j, c in enumerate(prog):
                if prog[j+1] == -1: # DONE WITH LOOP!
                    break
                if j == 0: # choose starting state
                    cur_state = self.getAction(context=prog[j], best=True, rand=rand)
                    state_list.append(cur_state)

                # choose an action (i.e., the next state)
                chosen_action = self.getAction(state=cur_state, context=prog[j+1], best=True, rand=rand)
                
                next_state = chosen_action
                state_list.append(next_state)

                vl_reward, vc, p58, il, d58, lt, ct, sev = self.calculateRewards(cur_state, chosen_action)
                cur_vl_reward += vl_reward
                num_voice_crossings += vc
                num_parallels += p58
                num_illegal_leaps += il  
                num_direct += d58
                num_lt += lt 
                num_ct += ct 
                num_sev += sev
                cur_state=next_state
            
            all_voicings.append(state_list)
            
            all_vl_rewards.append(cur_vl_reward)
            all_vc.append(num_voice_crossings)
            all_parallels.append(num_parallels)
            all_illegal_leaps.append(num_illegal_leaps)
            all_direct.append(num_direct)
            all_lt.append(num_lt)
            all_ct.append(num_ct)
            all_sev.append(num_sev)

            #state_seq_with_melody_to_MIDI(melody, state_list, self.state_indices, self.results_dir, desired_fstub=fname)
        #if synth:
        #    midis_to_wavs(self.results_dir)

        return sum(all_vl_rewards), sum(all_vc), sum(all_parallels), sum(all_illegal_leaps), sum(all_direct), sum(all_lt), sum(all_ct), sum(all_sev), all_voicings   


class HarmonizationModel(Qlearner):
    def __init__(self, alpha=0.1, gamma=0.6,  checkpoint=500, resultsdir='./results/harmonization_results/', ):
        super().__init__(alpha, gamma)
        self.results_dir = resultsdir
        self.rewardFunction = harmonization_reward_function # specify reward function in constructor
        self.checkpoint = checkpoint

    def getLegalActions(self,context=None):
        if context==None:
            print("ERROR, MELODY NOT PROVIDED")
        legal_chords = []
        min_context = min(context)
        for chord in self.state_indices.keys():
            if self.state_indices[chord][-1] in context and self.state_indices[chord][2] < min_context: #== context: 
                legal_chords.append(chord)
        return legal_chords

    def trainAgent(self, melodies, num_epochs=1000, epoch_rewards=[]):
        self.alpha_steps = [self.alpha*np.log(step) for step in np.linspace(np.e, 1, num_epochs)]
        for i in tqdm(range(len(epoch_rewards)+1,num_epochs)):
            epoch_reward=0
            self.alpha = self.alpha_steps[i]
            self.epsilon = (self.epsilon_init-self.epsilon_end)*((num_epochs - i)/num_epochs) + self.epsilon_end
            for melody in melodies:
                for j, c in enumerate(melody):
                    if melody[j+1][0] == -1: # DONE WITH LOOP!
                        break
                    if j == 0:
                        # choose starting state
                        cur_state = self.getAction(context=melody[j]) # THESE SHOULD BE LISTS!!!
                    # choose an action
                    chosen_action = self.getAction(state=cur_state, context=melody[j+1])
                    next_state = chosen_action # peform the chosen action and transition to the next state

                    # receive reward
                    
                    vl_reward, harm_prog_reward, _,_,_,_,_,_,_ = self.calculateRewards(cur_state, next_state)
                    epoch_reward += (vl_reward + harm_prog_reward)
                    # update q_val
                    self.update(cur_state, next_state, vl_reward + harm_prog_reward, context=melody[j+2])
                    cur_state=next_state
            
            if i%self.checkpoint == 0:
                print("epoch:", i, epoch_reward)
                self.saveModel(i, epoch_rewards)

            epoch_rewards.append(epoch_reward)
        return epoch_rewards
    
    def getHarmonization(self, melody):
        harmonization = [] 
        for j, c in enumerate(melody):
            if melody[j+1][0] == -1: # DONE WITH LOOP!
                    break
            if j == 0: # choose starting state
                cur_state = self.getAction(context=melody[j], best=True)
                harmonization.append(cur_state)

            chosen_action = self.getAction(state=cur_state, context=melody[j+1], best=True, rand=False)
                
            next_state = chosen_action
            harmonization.append(next_state)

            cur_state=next_state       

        return harmonization         

    
    def evalAgent(self, melody, num_voicings, fname=None, synth=False, rand=False): # set rand=True to compare to random baseline 
        all_voicings = []
        all_rewards = []
        for i in range(num_voicings):
            state_list = []
            total_reward = 0
            num_voice_crossings = 0
            num_parallels = 0
            num_illegal_leaps = 0
            num_direct = 0
            for j, c in enumerate(melody): # MELODY NEEDS TO BE LIST OF LISTS!
                if melody[j+1][0] == -1: # DONE WITH LOOP!
                    break
                if j == 0: # choose starting state
                    cur_state = self.getAction(context=melody[j], best=True, rand=rand)
                    state_list.append(cur_state)

                # choose an action (i.e., the next state)
                chosen_action = self.getAction(state=cur_state, context=melody[j+1], best=True, rand=rand)
                
                next_state = chosen_action
                state_list.append(next_state)

                vl_reward, harm_prog_reward, vc, p58, il, d58, lt, ct, sev = self.calculateRewards(cur_state, chosen_action)
                total_reward += vl_reward + harm_prog_reward
                num_voice_crossings += vc
                num_parallels += p58
                num_illegal_leaps += il  
                num_direct += d58
                
                total_reward += vl_reward + harm_prog_reward
                cur_state=next_state


            print("Total reward and sequence:", total_reward, state_list, chord_strings(state_list, self.state_indices))
            if state_list not in all_voicings:
                state_seq_with_melody_to_MIDI(melody, state_list, self.state_indices, self.results_dir, desired_fstub=fname)
                all_voicings.append(state_list)
                all_rewards.append(total_reward)
            else:
                print("Already saved harmonization")
            print("Num voice crossings:", num_voice_crossings, "\nNum parallels:", num_parallels, "\nNum illegal leaps:", num_illegal_leaps, "\nNum direct fifths/octaves", num_direct)
            # EVALUATE STATE LIST

        # saves the melody as a MIDI # 
        fname = get_free_filename('melody', '.mid', directory=self.results_dir)
        melody_to_MIDI(melody, note_length=1, save=True, path=fname)

        if synth:
            midis_to_wavs(self.results_dir)

        return all_voicings, all_rewards   

    def fullEvalAgent(self, melodies, fname=None, synth=False, rand=False): # set rand=True to compare to random baseline 
        all_harms = []
        all_vl_rewards = []
        all_hp_rewards = []
        all_vc = []
        all_parallels = []
        all_illegal_leaps = []
        all_direct = []
        all_lt = [] 
        all_ct = [] 
        all_sev = [] 
        for melody in melodies:
            state_list = []
            cur_vl_reward = 0
            cur_hp_reward = 0
            num_voice_crossings = 0
            num_parallels = 0
            num_illegal_leaps = 0
            num_direct = 0
            num_lt = 0 
            num_ct = 0
            num_sev = 0 
            for j, c in enumerate(melody): # MELODY NEEDS TO BE LIST OF LISTS!
                if melody[j+1][0] == -1: # DONE WITH LOOP!
                    break
                if j == 0: # choose starting state
                    cur_state = self.getAction(context=melody[j], best=True, rand=rand)
                    state_list.append(cur_state)

                # choose an action (i.e., the next state)
                chosen_action = self.getAction(state=cur_state, context=melody[j+1], best=True, rand=rand)
                
                next_state = chosen_action
                state_list.append(next_state)

                vl_reward, hp_reward, vc, p58, il, d58, lt, ct, sev = self.calculateRewards(cur_state, chosen_action)
                cur_vl_reward += vl_reward
                cur_hp_reward += hp_reward
                num_voice_crossings += vc
                num_parallels += p58
                num_illegal_leaps += il  
                num_direct += d58
                num_lt += lt 
                num_ct += ct 
                num_sev += sev
                
                cur_state=next_state
            
            all_harms.append(state_list)
            
            all_vl_rewards.append(cur_vl_reward)
            all_hp_rewards.append(cur_hp_reward)
            all_vc.append(num_voice_crossings)
            all_parallels.append(num_parallels)
            all_illegal_leaps.append(num_illegal_leaps)
            all_direct.append(num_direct)
            all_lt.append(num_lt)
            all_ct.append(num_ct)
            all_sev.append(num_sev)

            #state_seq_with_melody_to_MIDI(melody, state_list, self.state_indices, self.results_dir, desired_fstub=fname)
        #if synth:
        #    midis_to_wavs(self.results_dir)

        return sum(all_vl_rewards), sum(all_hp_rewards), sum(all_vc), sum(all_parallels), sum(all_illegal_leaps), sum(all_direct), sum(all_lt), sum(all_ct), sum(all_sev), all_harms   

class FreeModel(Qlearner): # uses default getLegalActions
    def __init__(self, alpha=0.1, gamma=0.6, checkpoint=500, resultsdir='./results/free_results/'):
        super().__init__(alpha, gamma)
        self.results_dir = resultsdir
        self.rewardFunction = harmonization_reward_function
        self.checkpoint = checkpoint

    def trainAgent(self, num_epochs=5000, epoch_rewards=[], voicings=None):
        self.alpha_steps = [self.alpha*np.log(step) for step in np.linspace(np.e, 1, num_epochs)]
        # voicings are passed in just to provide episodes/episode lengths consistent with other model runs
        for i in tqdm(range(len(epoch_rewards)+1,num_epochs)):
            epoch_reward=0
            self.alpha = self.alpha_steps[i]
            self.epsilon = (self.epsilon_init-self.epsilon_end)*((num_epochs - i)/num_epochs) + self.epsilon_end
            if i%self.checkpoint == 0:
                print("epoch:", i, epoch_reward)
                self.saveModel(i, epoch_rewards)
            for v in voicings: 
                for j in range(len(v)):
                    if j == 0:
                        cur_state = self.getAction()

                    chosen_action = self.getAction(state=cur_state)
                    next_state = chosen_action
                    
                    # vl_reward, harm_prog_reward, vc,p58,il,d58
                    vl_reward, harm_prog_reward, _,_,_,_,_,_,_ = self.calculateRewards(cur_state, chosen_action)
                    epoch_reward += vl_reward + harm_prog_reward

                    self.update(cur_state, next_state, vl_reward + harm_prog_reward, context=None)
                    cur_state=next_state
            epoch_rewards.append(epoch_reward)
        return epoch_rewards
    
    def evalAgent(self, num_generations=3, length=10, fname=None, synth=False, rand=False): # set rand=True to compare to random baseline 
        all_generations = []
        all_rewards = []
        print(num_generations)
        for i in range(num_generations):
            print("GENERATION:", i)
            state_list = []
            total_reward = 0
            num_voice_crossings = 0
            num_parallels = 0
            num_illegal_leaps = 0
            num_direct = 0
            for i in range(length-1):
                if i == 0: # choose starting state
                    cur_state = self.getAction(rand=rand)
                    state_list.append(cur_state)

                # choose an action (i.e., the next state)
                chosen_action = self.getAction(state=cur_state, best=True, rand=rand)
                
                next_state = chosen_action
                state_list.append(next_state)

                vl_reward, harm_prog_reward, vc,p58,il,d58 = self.calculateRewards(cur_state, chosen_action)
                num_voice_crossings += vc
                num_parallels += p58
                num_illegal_leaps += il  
                num_direct += d58
                
                total_reward += vl_reward + harm_prog_reward
                cur_state=next_state

            print("Total reward and sequence:", total_reward, state_list, chord_strings(state_list, self.state_indices))
            if state_list not in all_generations:
                state_seq_to_MIDI(state_list, self.state_indices, self.results_dir, desired_fstub=fname)
                all_generations.append(state_list)
                all_rewards.append(total_reward)
            else:
                print("Already saved voicing")
            print("Num voice crossings:", num_voice_crossings, "\nNum parallels:", num_parallels, "\nNum illegal leaps:", num_illegal_leaps, "\nNum direct fifths/octaves", num_direct)
            # EVALUATE STATE LIST

        if synth:
            midis_to_wavs(self.results_dir)

        return all_generations, all_rewards
    
    def fullEvalAgent(self, voicings, fname=None, synth=False, rand=False): # set rand=True to compare to random baseline 
        all_comps = []
        all_vl_rewards = []
        all_hp_rewards = []
        all_vc = []
        all_parallels = []
        all_illegal_leaps = []
        all_direct = []
        all_lt = [] 
        all_ct = [] 
        all_sev = [] 
        for v in voicings:
            state_list = []
            cur_vl_reward = 0
            cur_hp_reward = 0
            num_voice_crossings = 0
            num_parallels = 0
            num_illegal_leaps = 0
            num_direct = 0
            num_lt = 0
            num_ct = 0 
            num_sev = 0
            for i in range(len(v)):
                if i == 0: # choose starting state
                    cur_state = self.getAction(rand=rand)
                    state_list.append(cur_state)

                # choose an action (i.e., the next state)
                chosen_action = self.getAction(state=cur_state, best=True, rand=rand)
                
                next_state = chosen_action
                state_list.append(next_state)

                vl_reward, hp_reward, vc, p58, il, d58, lt, ct, sev = self.calculateRewards(cur_state, next_state)
                cur_vl_reward += vl_reward
                cur_hp_reward += hp_reward
                num_voice_crossings += vc
                num_parallels += p58
                num_illegal_leaps += il  
                num_direct += d58
                num_lt += lt 
                num_ct += ct 
                num_sev += sev
                cur_state=next_state
            
            all_comps.append(state_list)
            
            all_vl_rewards.append(cur_vl_reward)
            all_hp_rewards.append(cur_hp_reward)
            all_vc.append(num_voice_crossings)
            all_parallels.append(num_parallels)
            all_illegal_leaps.append(num_illegal_leaps)
            all_direct.append(num_direct)
            all_lt.append(num_lt)
            all_ct.append(num_ct)
            all_sev.append(num_sev)

        return sum(all_vl_rewards), sum(all_hp_rewards), sum(all_vc), sum(all_parallels), sum(all_illegal_leaps), sum(all_direct), sum(all_lt), sum(all_ct), sum(all_sev), all_comps   



        