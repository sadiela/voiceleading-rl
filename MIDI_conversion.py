import pretty_midi
import yaml
from midi2audio import FluidSynth
import os
from pathlib import Path
import numpy as np
import pretty_midi
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from tqdm import tqdm
from pathlib import Path
from numpy import ndarray
import os
import sys

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
    return desired_filename

def melody_to_MIDI(melody, note_length=1, save=False, path='./melody.mid'): # note length in seconds
    print("MELODY:", melody)
    notes = []
    for i, mel in enumerate(melody):
        if mel[0] == -1: 
            break
        num_mel_notes = len(mel)
        for j, mnote in enumerate(mel): 
            note_obj = pretty_midi.Note(velocity=100, pitch=mnote, 
                                        start=note_length*i + j*(note_length/num_mel_notes), 
                                        end=note_length*i + (j+1)*(note_length/num_mel_notes))
            notes.append(note_obj)
    if save: 
        midi_obj = pretty_midi.PrettyMIDI()
        piano = pretty_midi.Instrument(program=1)
        for mel_note in notes: 
            piano.notes.append(mel_note)
        midi_obj.instruments.append(piano)
        midi_obj.write(path)
        return notes, path
    return notes, None

def state_seq_with_melody_to_MIDI(melody, state_seq, state_indices, directory, desired_fstub='seqmid'):
    desired_filename = get_free_filename(desired_fstub, '.mid', directory=directory)
    # Create a PrettyMIDI object
    midi_obj = pretty_midi.PrettyMIDI() # init tempo is 120, so a quarter note is 0.5 sec
    piano = pretty_midi.Instrument(program=1)

    melody_notes = melody_to_MIDI(melody)
    for mel_note in melody_notes: 
        piano.notes.append(mel_note)

    for i, state in enumerate( state_seq):
        notes = state_indices[state][:3]
        for note in notes: 
            note_obj = pretty_midi.Note(
                velocity=75, pitch=note, start=1*i, end=1*i+1)
            # Add it to our cello instrument
            piano.notes.append(note_obj)

    midi_obj.instruments.append(piano)
    midi_obj.write(desired_filename)

def midi_to_wav(midi_path,wav_path):
    #print("CONVERTING")
    # using the default sound font in 44100 Hz sample rate
    fs = FluidSynth(sound_font="./GeneralUser_GS_v1.471.sf2")
    fs.midi_to_audio(midi_path, wav_path)

def midis_to_wavs(midi_dir, wav_dir=None):
    print("MIDI DIR:", midi_dir, "WAV DIR", wav_dir)
    if wav_dir == None: 
        wav_dir = midi_dir
    midi_dir_list = os.listdir(midi_dir)
    midi_list = [f for f in midi_dir_list if f[-3:] == 'mid']
    for midi in midi_list: 
        print("MIDI", midi)
        midi_to_wav(str(midi_dir) + midi, str(wav_dir) + midi[:-3]+'wav')

def get_fs(tempo, measure_subdivision):
    time_per_quarter_note = 1/ (tempo/60)
    further_div = measure_subdivision/4
    column_spacing = time_per_quarter_note/further_div
    return 1/column_spacing

def custom_plot_pianoroll(
    ax: Axes,           # no default
    pianoroll: ndarray, # no default
    minc: int = -1, maxc: int = 7, resolution: int = 24,
    cmap: str = "Blues", grid_axis: str = "both",
    grid_linestyle: str = ":", grid_linewidth: float = 0.5,
    vmax=1, ymin=None, ymax=None, **kwargs,):

    img = ax.imshow(
        pianoroll,
        cmap=cmap,
        aspect="auto",
        vmin=0,
        vmax=vmax, # if pianoroll.dtype == np.bool_ else 127,
        origin="lower",
        interpolation="none",
        **kwargs,
    )

    ax.set_yticks(np.arange(12*(minc+2), 12*(maxc+3), 12))
    ax.set_yticklabels([f"C{minc+i}" for i in range(maxc-minc+1)], fontsize=12)

    nonzero_row_indices = np.nonzero(np.count_nonzero(pianoroll, axis=1))
    if not ymin:
        ymin = np.min(nonzero_row_indices) - 12
    if not ymax: 
        ymax = np.max(nonzero_row_indices) + 12

    ax.set_ylim([ymin, ymax])
    ax.set_ylabel("Pitch", fontsize=14)

    # Format x-axis
    ax.set_xticks(np.arange(-0.5, pianoroll.shape[1], resolution)) # put labels
    ax.set_xticklabels(np.arange(0, pianoroll.shape[1]//resolution +1, 1), fontsize=12)
    ax.set_xlim([-0.5, pianoroll.shape[1]])
    ax.set_xlabel("Time (beats)", fontsize=14)

    if grid_axis != "off":
        ax.grid(
            axis='x', # or "both"
            color="k",
            linestyle=grid_linestyle,
            linewidth=grid_linewidth,
        )
    return img

def test_different_midi_instruments(pm, res_folder): 
    for i in range(15): 
        print("INSTRUMENT:", pretty_midi.program_to_instrument_name(i))
        new_instr = pretty_midi.PrettyMIDI()
        # Create an Instrument instance for a cello instrument
        instrument = pretty_midi.Instrument(program=i)
        for note in pm.instruments[0].notes:
            # Create a Note instance
            newnote = pretty_midi.Note(
                velocity=note.velocity, pitch=note.pitch, start=note.start, end=note.end)
            # Add it to  instrument
            instrument.notes.append(newnote)
        # Add the instrument to the new pretty_midi object
        new_instr.instruments.append(instrument)
        # Write out the MIDI data
        new_instr.write(res_folder + pretty_midi.program_to_instrument_name(i) + '.mid')

    midis_to_wavs(res_folder)

if __name__ == "__main__":



    # UNIT TEST: melody_to_MIDI #

    sys.exit(0)

    pm = pretty_midi.PrettyMIDI("./results/voicing_results/voicing-1.mid")
    res_folder = "./results/midi_instr/"
    test_different_midi_instruments(pm, res_folder)
    

    midi_path = "./results/voicing_results/voicing-1.mid"
    wav_path = "./results/voicing_results/NEWSOUNDFONT_voicing-1.wav"
    midi_to_wav(midi_path,wav_path)


    # Loading a file on disk using PrettyMidi, and show
    measure_subdiv=1
    tempo = pm.get_tempo_changes()[1][0]
    fs= 4
    print(fs)
    print("Tempo:", tempo)
    pianoroll = pm.instruments[0].get_piano_roll(fs=fs)
    _, ax = plt.subplots()
    ax  = custom_plot_pianoroll(ax, pianoroll, resolution=2)

    ax.figure.set_size_inches(20, 5)
    plt.savefig('./results/voicing_results/voicing-1.png',bbox_inches="tight")


    #midis_to_wavs('./results/free_results/')

    '''
    - 52
    - 53
    - 60
    - 69
    '''