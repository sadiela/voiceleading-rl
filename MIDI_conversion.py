import pretty_midi
import yaml
from midi2audio import FluidSynth
import os
from pathlib import Path

def get_free_filename(stub, suffix='', date=False):
    directory = Path('./results/')
    # Create unique file/directory 
    counter = 0
    while True:
        if date:
            file_candidate = '{}/{}-{}-{}{}'.format(str(directory), stub, datetime.today().strftime('%Y-%m-%d'), counter, suffix)
        else: 
            file_candidate = '{}/{}-{}{}'.format(str(directory), stub, counter, suffix)
        if Path(file_candidate).exists():
            #print("file exists")
            counter += 1
        else:  # No match found
            #print("no file")
            if suffix=='.p':
                print("will create pickle file")
            elif suffix:
                Path(file_candidate).touch()
            else:
                Path(file_candidate).mkdir()
            return file_candidate

def state_seq_to_MIDI(state_seq, state_indices, desired_filename=None): 
    if desired_filename is None: 
        desired_filename = get_free_filename('seqmid', '.mid')
    # Create a PrettyMIDI object
    midi_obj = pretty_midi.PrettyMIDI() # init tempo is 120, so a quarter note is 0.5 sec
    # Create an Instrument instance for a cello instrument
    piano = pretty_midi.Instrument(program=1)
    # Iterate over note names, which will be converted to note number later
    for i, state in enumerate(state_seq): 
        notes = state_indices[state]
        #print(notes)
        for note in notes: 
            # Create a Note instance, starting at 0s and ending at 1s
            note_obj = pretty_midi.Note(
                velocity=100, pitch=note, start=1*i, end=1*i+1)
            # Add it to our cello instrument
            piano.notes.append(note_obj)
    # Add the cello instrument to the PrettyMIDI object
    midi_obj.instruments.append(piano)
    # Write out the MIDI data
    midi_obj.write(desired_filename)

def midi_to_wav(midi_path,wav_path):
    #print("CONVERTING")
    # using the default sound font in 44100 Hz sample rate
    fs = FluidSynth()
    fs.midi_to_audio(midi_path, wav_path)

def midis_to_wavs(midi_dir, wav_dir=None):
    print("Converting!")
    if wav_dir == None: 
        wav_dir = midi_dir
    midi_dir_list = os.listdir(midi_dir)
    midi_list = [f for f in midi_dir_list if f[-3:] == 'mid']
    for midi in midi_list: 
        print("MIDI", midi)
        midi_to_wav(str(midi_dir) + '/' + midi, str(wav_dir) +'/' + midi[:-3]+'wav')


if __name__ == "__main__":

    with open('voicing_state_indices.yaml', 'r') as file:
        state_indices = yaml.safe_load(file)   

    seq = [20, 74, 99, 9, 74, 99, 9, 122, 34, 99, 9]

    results_dir = './results/'
    desired_fname = './results/state_to_midi_test.mid'

    state_seq_to_MIDI(seq, desired_fname, state_indices)
    midis_to_wavs(results_dir)