import pretty_midi
import yaml
from midi2audio import FluidSynth
import os
from pathlib import Path

def get_free_filename(stub, suffix='', directory='./results/', date=False):
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

def state_seq_to_MIDI(state_seq, state_indices, dir, desired_fstub='seqmid'): 
    desired_filename = get_free_filename(desired_fstub, '.mid', directory=dir)
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
    print("MIDI DIR:", midi_dir)
    print("Converting!")
    if wav_dir == None: 
        wav_dir = midi_dir
    midi_dir_list = os.listdir(midi_dir)
    midi_list = [f for f in midi_dir_list if f[-3:] == 'mid']
    for midi in midi_list: 
        print("MIDI", midi)
        midi_to_wav(str(midi_dir) +'/'+ midi, str(wav_dir) +'/'+ midi[:-3]+'wav')

if __name__ == "__main__":
    midis_to_wavs('./results/free_results/')

    '''
    - 52
    - 53
    - 60
    - 69
    '''