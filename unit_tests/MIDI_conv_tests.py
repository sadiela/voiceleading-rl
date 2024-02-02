import sys
sys.path.append('../final_project')
from MIDI_conversion import *

### SOME UNIT TESTS! ### Call from parent directory

with open('./dictionaries/state_dict_3.yaml', 'r') as file:
            state_indices = yaml.safe_load(file)


def test_state_seq_to_MIDI():
    state_seq = [7,1161,2329,1218,936,2562,9-1] # chords: 1,4,9,5,4,10,1
    path = state_seq_to_MIDI(state_seq, state_indices, './unit_tests/test_results/', desired_fstub='stateseq_test')
    midi_to_wav(path,path[:-3]+'wav')

def test_melody_to_MIDI(): 
    melody1 = [[72, 74],[76,77],[76],[72],[-1]]
    notes1, path1 = melody_to_MIDI(melody1, note_length=0.5, save=True, path='./unit_tests/test_results/mel_test1.mid')
    midi_to_wav(path1,path1[:-3]+'wav')

    melody2 = [[76,74,76,74],[74],[72],[74],[76,76],[76,76,76],[76],[-1]]
    notes1, path2 = melody_to_MIDI(melody2, note_length=1, save=True, path='./unit_tests/test_results/mel_test2.mid')
    midi_to_wav(path2,path2[:-3]+'wav')


if __name__ == "__main__":
    test_state_seq_to_MIDI()
    #test_melody_to_MIDI()
