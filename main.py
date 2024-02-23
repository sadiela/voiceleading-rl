from MIDI_conversion import *
from voice_leading_rules import *
import matplotlib.pyplot as plt
from models.models import *
import os 
import glob
#melody_harmonization_model import *
#from models.free_model import *
#from models.voicing_model import *
import yaml
from datetime import datetime

DATESTR = datetime.today().strftime("%m_%d")
CHECKPOINT = 500


def plotRewards(data, type, savepath):
    plt.plot(data)
    plt.xlabel("Training Epoch")
    plt.ylabel("Reward")
    plt.title(type + ": Total Reward over Epoch")
    plt.savefig(savepath,bbox_inches="tight")
    plt.clf() 

def harmonizationTraining(n_epochs):
    with open('./data/jsb_major_melodies.yaml', 'r') as file:
            all_melodies = yaml.safe_load(file)
    train_melodies = all_melodies['train'] #[[[76,74],[74],[72],[74],[76,76],[76],[76],[-1]]]
    test_melodies = all_melodies['test']

    harmonization_agent = HarmonizationModel(gamma=0.95, alpha=0.1, checkpoint=CHECKPOINT)
    rewards, completed_epochs = harmonization_agent.prepModel('./models/harmmodel_*.p')

    # handle out-of-range melodies!
    harmonization_epoch_rewards = harmonization_agent.trainAgent(train_melodies, num_epochs=n_epochs-completed_epochs, epoch_rewards=rewards)
    harmonization_agent.saveModel('./models/harmmodel_fulldata_' + DATESTR + '.p', n_epochs, harmonization_epoch_rewards)

    plotRewards(harmonization_epoch_rewards, 'HARMONIZATION', './results/harmonization_results/training_reward_' + DATESTR +'.png')

    all_voicings, all_rewards = harmonization_agent.evalAgent(test_melodies[2], 5, fname="harmonization" + DATESTR, synth=True)
    rand_voicings, rand_rewards = harmonization_agent.evalAgent(test_melodies[2], 5, fname="baseline_harmonization" + DATESTR, synth=True, rand=True)

def voicingTraining(n_epochs):
    with open('./data/jsb_major_chord_progs.yaml', 'r') as file:
        chord_progressions = yaml.safe_load(file)
    train_progs = chord_progressions['train'] #[[[76,74],[74],[72],[74],[76,76],[76],[76],[-1]]]
    test_progs = chord_progressions['test']

    voicing_agent = VoicingModel(checkpoint=CHECKPOINT)
    rewards, completed_epochs = voicing_agent.prepModel('./models/voicemodel_*.p')

    voicing_epoch_rewards = voicing_agent.trainAgent(train_progs, num_epochs=n_epochs-completed_epochs, epoch_rewards=rewards)
    voicing_agent.saveModel('./models/voicemodel'+DATESTR+'.p',n_epochs, voicing_epoch_rewards)

    plotRewards(voicing_epoch_rewards, 'VOICING', './results/voicing_results/training_reward_' + DATESTR +'.png')

    all_voicings, all_rewards = voicing_agent.evalAgent(test_progs[3], 5, fname="voicing", synth=True)
    rand_voicings, rand_rewards = voicing_agent.evalAgent(test_progs[3], 5, fname="baseline_voicing" + DATESTR, synth=True, rand=True)

def freeTraining(n_epochs):
    free_agent = FreeModel(checkpoint=CHECKPOINT)
    rewards, completed_epochs = free_agent.prepModel('./models/voicemodel_*.p')

    free_epoch_rewards = free_agent.trainAgent(num_epochs=n_epochs-completed_epochs, epoch_rewards=rewards)
    free_agent.saveModel('./models/freemodel'+DATESTR+'.p',n_epochs,free_epoch_rewards)

    plotRewards(free_epoch_rewards, 'FREE', './results/free_results/training_reward_' + DATESTR + '.png')

    free_progs, free_rewards = free_agent.evalAgent(num_generations=10, length=12, fname="free_trial"+ DATESTR, synth=True)
    rand_voicings, rand_rewards = free_agent.evalAgent(num_generations=10, length=12, fname="baseline_free" + DATESTR, synth=True, rand=True)

if __name__ == "__main__":
    ###########################
    ### HARMONIZATION MODEL ###
    ###########################
    n_epochs = 8000

    #print("Start harmonization training loop")
    #harmonizationTraining(n_epochs)

    print("Start voicing training loop")
    voicingTraining(n_epochs)

    #print("Start free training loop")
    #freeTraining(n_epochs)
