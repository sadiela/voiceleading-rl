from MIDI_conversion import *
from voice_leading_rules import *
import matplotlib.pyplot as plt
from models.models import *
#melody_harmonization_model import *
#from models.free_model import *
#from models.voicing_model import *


if __name__ == "__main__":
    ###########################
    ### HARMONIZATION MODEL ###
    ###########################
    harmonization_agent = HarmonizationModel()
    melodies = [[[76,74],[74],[72],[74],[76,76],[76],[76],[-1]]]

    harmonization_epoch_rewards = harmonization_agent.trainAgent(melodies, num_epochs=5000)

    '''plt.plot(harmonization_epoch_rewards)
    plt.xlabel("Training Epoch")
    plt.ylabel("Reward")
    plt.title("HARMONIZATION: Total Reward over Epoch")
    plt.savefig('./results/harmonization_results/training_reward_.png',bbox_inches="tight")
    plt.clf()'''
    #plt.show()

    all_voicings, all_rewards = harmonization_agent.evalAgent(melodies[0], 5, fname="harmonization", synth=True)

    sys.exit(0)

    #####################
    ### VOICING MODEL ###
    #####################
    voicing_agent = VoicingModel()
    chord_progressions = [
        [1,5,6,1,3,6,10,1,7,3,5,6,10,1,3,5,6,11,3,5,1,6,10,1,3,5,6,2,10,1,-1],
        [1, 4, 5, 1, -1],[1, 6, 2, 5, 1, -1],
        [1, 4, 7, 3, 6, 2, 5, 1, -1],[1, 6, 4, 2, 7, 5, 1,-1],
        [1,2,-1], [1,3,-1],[1,4,-1],[1,5,-1],[1,7,-1],[2,5,-1],
        [3,5,-1],[4,5,-1],[6,5,-1],[7,5,-1]]
    
    voicing_epoch_rewards = voicing_agent.trainAgent(chord_progressions, num_epochs=30000)

    plt.plot(voicing_epoch_rewards)
    plt.xlabel("Training Epoch")
    plt.ylabel("Reward")
    plt.title("VOICING: Total Reward over Epoch")
    plt.savefig('./results/voicing_results/training_reward_.png',bbox_inches="tight")
    plt.clf()
    #plt.show()

    ex_prog = [1,3,6,10,1,-1]
    all_voicings, all_rewards = voicing_agent.evalAgent(ex_prog, 10, fname="voicing", synth=True)

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
    harmonization_agent.saveModel('./models/harmmodel2.npy')
    voicing_agent.saveModel('./models/voicemodel2.npy')