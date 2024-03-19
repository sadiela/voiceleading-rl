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
from tqdm import tqdm

DATESTR = datetime.today().strftime("%m_%d")
CHECKPOINT = 500


def plotRewards(data, type, savepath):
    plt.plot(data)
    plt.xlabel("Training Epoch")
    plt.ylabel("Reward")
    plt.title(type + ": Total Reward over Epoch")
    plt.savefig(savepath,bbox_inches="tight")
    plt.clf() 

def bachEval():
    with open('./data/jsb_major_orig_voicings.yaml', 'r') as file:
        voicings = yaml.safe_load(file)
    test_voicings = voicings['test']

    vc_total = 0
    p58_total = 0
    il_total = 0
    d58_total = 0
    lt_total = 0
    ct_total = 0 
    sev_total = 0
    vl_reward_total = 0 
    hp_reward_total = 0

    for voicing in tqdm(test_voicings):
        for i in range(len(voicing)-1):
            vl_reward, harm_prog_reward, vc,p58,il,d58,lt,ct,sev = harmonization_reward_function(voicing[i], voicing[i+1])
            vl_reward_total += vl_reward
            hp_reward_total += harm_prog_reward 
            vc_total += vc 
            p58_total += p58 
            il_total += il
            d58_total += d58
            lt_total += lt 
            ct_total += ct 
            sev_total += sev

    print("ORIG BACH")
    print("VL reward:", vl_reward_total, "\nHP reward:", hp_reward_total)
    print("VCs:", vc_total, "\nP58s:", p58_total, "\nILs:", il_total, "\nD58s:", d58_total)
    print("LTs:", lt_total, "\nCTs:", ct_total, "\nSevs:", sev_total)
    return vl_reward_total, hp_reward_total, vc_total, p58_total, il_total, d58_total

def harmonizationEval():
    with open('./data/jsb_major_melodies.yaml', 'r') as file:
            all_melodies = yaml.safe_load(file)
    test_melodies = all_melodies['test']

    harmonization_agent = HarmonizationModel() # don't care about training hyperparameters
    _, _ = harmonization_agent.prepModel('./models/harmmodel_*.p') # load in most recent model

    # FOR RANDOM!
    print("RAND HARMONIZATION EVAL!", len(test_melodies))
    vl_rewards, hp_rewards, all_vc, all_parallels, all_illegal_leaps, all_direct, all_lt, all_ct, all_sev, all_harmonizations = harmonization_agent.fullEvalAgent(test_melodies, fname="full_random_harmonization" + DATESTR, synth=True, rand=True)

    # SAVE HARMONIZATIONS!
    with open('./results/for_table/random_harmonizatons.yaml', 'w') as outfile:
        yaml.dump(all_harmonizations, outfile, default_flow_style=False)
    #print(sum(vl_rewards), sum(all_vc), sum(all_parallels), sum(all_illegal_leaps), sum(all_direct))

    print("VL reward:", vl_rewards, "\nHP reward:", hp_rewards)
    print("VCs:", all_vc, "\nP58s:", all_parallels, "\nILs:", all_illegal_leaps, "\nD58s:", all_direct)
    print("LTs:", all_lt, "\nCTs:", all_ct, "\nSevs:", all_sev)

    print("MODEL HARMONIZATION EVAL!", len(test_melodies))
    vl_rewards, hp_rewards, all_vc, all_parallels, all_illegal_leaps, all_direct, all_lt, all_ct, all_sev, all_harmonizations = harmonization_agent.fullEvalAgent(test_melodies, fname="full_harmonization" + DATESTR, synth=True, rand=False)

    # SAVE HARMONIZATIONS!
    with open('./results/for_table/model_harmonizatons.yaml', 'w') as outfile:
        yaml.dump(all_harmonizations, outfile, default_flow_style=False)
    #print(sum(vl_rewards), sum(all_vc), sum(all_parallels), sum(all_illegal_leaps), sum(all_direct))

    print("VL reward:", vl_rewards, "\nHP reward:", hp_rewards)
    print("VCs:", all_vc, "\nP58s:", all_parallels, "\nILs:", all_illegal_leaps, "\nD58s:", all_direct)
    print("LTs:", all_lt, "\nCTs:", all_ct, "\nSevs:", all_sev)

def voicingEval():
    with open('./data/jsb_major_chord_progs.yaml', 'r') as file:
            all_progs = yaml.safe_load(file)
    test_progs = all_progs['test']

    voicing_agent = VoicingModel()
    _,_ = voicing_agent.prepModel('./models/voicingmodel_*.p')

    print("RAND VOICING EVAL!", len(test_progs))
    vl_rewards, all_vc, all_parallels, all_illegal_leaps, all_direct, all_lt, all_ct, all_sev, all_voicings = voicing_agent.fullEvalAgent(test_progs, fname="full_random_voicing"+DATESTR, synth=True, rand=True)

    with open('./results/for_table/random_voicings.yaml', 'w') as outfile:
        yaml.dump(all_voicings, outfile, default_flow_style=False)

    print("VL reward:", vl_rewards)
    print("VCs:", all_vc, "\nP58s:", all_parallels, "\nILs:", all_illegal_leaps, "\nD58s:", all_direct)
    print("LTs:", all_lt, "\nCTs:", all_ct, "\nSevs:", all_sev)

    print("MODEL VOICING EVAL!", len(test_progs))
    vl_rewards, all_vc, all_parallels, all_illegal_leaps, all_direct, all_lt, all_ct, all_sev, all_voicings = voicing_agent.fullEvalAgent(test_progs, fname="full_voicing"+DATESTR, synth=True, rand=False)

    with open('./results/for_table/model_voicings.yaml', 'w') as outfile:
        yaml.dump(all_voicings, outfile, default_flow_style=False)

    print("VL reward:", vl_rewards)
    print("VCs:", all_vc, "\nP58s:", all_parallels, "\nILs:", all_illegal_leaps, "\nD58s:", all_direct)
    print("LTs:", all_lt, "\nCTs:", all_ct, "\nSevs:", all_sev)

def harmonizationTraining(n_epochs):
    with open('./data/jsb_major_melodies.yaml', 'r') as file:
            all_melodies = yaml.safe_load(file)
    train_melodies = all_melodies['train'] #[[[76,74],[74],[72],[74],[76,76],[76],[76],[-1]]]
    test_melodies = all_melodies['test']

    harmonization_agent = HarmonizationModel(gamma=0.95, alpha=0.1, checkpoint=CHECKPOINT) # defile model
    rewards, completed_epochs = harmonization_agent.prepModel('./models/harmmodel_*.p')

    # handle out-of-range melodies!
    harmonization_epoch_rewards = harmonization_agent.trainAgent(train_melodies, num_epochs=n_epochs-completed_epochs, epoch_rewards=rewards)
    harmonization_agent.saveModel('./models/harmmodel_fulldata_' + DATESTR + '.p', n_epochs, harmonization_epoch_rewards)

    plotRewards(harmonization_epoch_rewards, 'HARMONIZATION', './results/harmonization_results/training_reward_' + DATESTR +'.png')

    all_voicings, all_rewards = harmonization_agent.evalAgent(test_melodies[2], 5, fname="harmonization" + DATESTR, synth=True)
    rand_voicings, rand_rewards = harmonization_agent.evalAgent(test_melodies[2], 5, fname="baseline_harmonization" + DATESTR, synth=True, rand=True)

def voicingTraining(n_epochs, train=True):
    with open('./data/jsb_major_chord_progs.yaml', 'r') as file:
        chord_progressions = yaml.safe_load(file)
    train_progs = chord_progressions['train'] #[[[76,74],[74],[72],[74],[76,76],[76],[76],[-1]]]
    test_progs = chord_progressions['test']


    voicing_agent = VoicingModel(checkpoint=CHECKPOINT)
    rewards, completed_epochs = voicing_agent.prepModel('./models/voicemodel_*.p')

    if train: 
        voicing_epoch_rewards = voicing_agent.trainAgent(train_progs, num_epochs=n_epochs-completed_epochs, epoch_rewards=rewards)
        voicing_agent.saveModel('./models/voicemodel'+DATESTR+'.p',n_epochs, voicing_epoch_rewards)

        plotRewards(voicing_epoch_rewards, 'VOICING', './results/voicing_results/training_reward_' + DATESTR +'.png')

    for prog in test_progs: 
        if len(prog) > 10:
            all_voicings, all_rewards = voicing_agent.evalAgent(prog, 5, fname="voicing", synth=True)
            rand_voicings, rand_rewards = voicing_agent.evalAgent(prog, 5, fname="baseline_voicing" + DATESTR, synth=True, rand=True)
            break

def freeTraining(n_epochs):
    free_agent = FreeModel(checkpoint=5000)
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
    n_epochs = 100000

    bachEval()
    harmonizationEval()
    voicingEval()

    sys.exit(0)

    #print("Start harmonization training loop")
    #harmonizationTraining(n_epochs)

    #print("Start voicing training loop")
    #voicingTraining(n_epochs, train=False)

    print("Start free training loop")
    freeTraining(n_epochs)
