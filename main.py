from MIDI_conversion import *
from voice_leading_rules import *
import matplotlib.pyplot as plt
from models.melody_harmonization_model import *
#from models.free_model import *
from models.voicing_model import *


def train_melody_harm(): 
    ###  TRAINING LOOP ###
    melody_progression = [72,74,72,76,79,-1]
    agent = MelodyHarmonization()
    melodies = [melody_progression]

    epoch_rewards = []
    print("TRAINING")
    for i in range(1,1000):
        epoch_reward = 0
        for melody in melodies:
            for j, c in enumerate(melody):
                if melody[j+1] == -1: # DONE WITH LOOP!
                    break
                if j == 0:
                    # choose starting state
                    cur_state = agent.getAction(melody[j])

                # choose an action
                chosen_action = agent.getAction(melody[j+1], cur_state)
                # peform the chosen action and transition to the next state
                next_state = chosen_action

                # receive reward
                reward, _,_,_,_ = agent.calculateRewards(cur_state, next_state)
                epoch_reward += reward
                
                # update q_val
                agent.update(cur_state, next_state, reward, melody[j+2])
        
        print(epoch_reward)
        epoch_rewards.append(epoch_reward)

    return agent

    '''plt.plot(eval_rewards)
    plt.title("Total Reward over Epoch")
    plt.show()

    plt.plot(epoch_rewards)
    plt.xlabel("Training Epoch")
    plt.ylabel("Reward")
    plt.title("Total Reward over Epoch")
    plt.show()'''


if __name__ == "__main__":
    # TEST EACH MODEL 
    # MELODY HARMONIZATION
    mel_agent = train_melody_harm()
    # VOICING

    # FREE
