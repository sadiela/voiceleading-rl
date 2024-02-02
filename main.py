from MIDI_conversion import *
from voice_leading_rules import *
import matplotlib.pyplot as plt
from models.models import *
#melody_harmonization_model import *
#from models.free_model import *
#from models.voicing_model import *
import yaml


if __name__ == "__main__":
    ###########################
    ### HARMONIZATION MODEL ###
    ###########################
    harmonization_agent = HarmonizationModel(gamma=0.95)
    with open('./data/jsb_major_melodies.yaml', 'r') as file:
        all_melodies = yaml.safe_load(file)
    train_melodies = all_melodies['train'] #[[[76,74],[74],[72],[74],[76,76],[76],[76],[-1]]]
    test_melodies = all_melodies['test']

    print(len(train_melodies), len(test_melodies))

    # handle out-of-range melodies!
    harmonization_epoch_rewards = harmonization_agent.trainAgent(train_melodies, num_epochs=1000)

    plt.plot(harmonization_epoch_rewards)
    plt.xlabel("Training Epoch")
    plt.ylabel("Reward")
    plt.title("HARMONIZATION: Total Reward over Epoch")
    plt.savefig('./results/harmonization_results/training_reward_.png',bbox_inches="tight")
    plt.clf()

    all_voicings, all_rewards = harmonization_agent.evalAgent(test_melodies[0], 5, fname="harmonization", synth=True)

    harmonization_agent.saveModel('./models/harmmodel_fulldata.npy')

    sys.exit(0)

    #####################
    ### VOICING MODEL ###
    #####################
    voicing_agent = VoicingModel()
    with open('./data/jsb_major_chord_progs.yaml', 'r') as file:
        chord_progressions = yaml.safe_load(file)
    train_progs = chord_progressions['train'] #[[[76,74],[74],[72],[74],[76,76],[76],[76],[-1]]]
    
    voicing_epoch_rewards = voicing_agent.trainAgent(train_progs, num_epochs=30000)

    plt.plot(voicing_epoch_rewards)
    plt.xlabel("Training Epoch")
    plt.ylabel("Reward")
    plt.title("VOICING: Total Reward over Epoch")
    plt.savefig('./results/voicing_results/training_reward_.png',bbox_inches="tight")
    plt.clf()
    #plt.show()

    ex_prog = [1,3,6,10,1,-1]
    all_voicings, all_rewards = voicing_agent.evalAgent(ex_prog, 10, fname="voicing", synth=True)

    voicing_agent.saveModel('./models/voicemodel_fulldata.npy')

    ##################
    ### FREE MODEL ###
    ##################
    free_agent = FreeModel()
    free_epoch_rewards = free_agent.trainAgent(num_epochs=30000)

    plt.plot(free_epoch_rewards)
    plt.xlabel("Training Epoch")
    plt.ylabel("Reward")
    plt.title("FREE: Total Reward over Epoch")
    plt.savefig('./results/free_results/training_reward_.png',bbox_inches="tight")
    plt.clf()
    #plt.show()

    free_progs, free_rewards = free_agent.evalAgent(num_generations=10, fname="free_trial", synth=True)


    print("Saving models:")
    free_agent.saveModel('./models/freemodel2.npy')