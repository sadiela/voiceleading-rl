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
import librosa
from datetime import datetime
from scipy.io.wavfile import write
import pandas as pd

def crop_wav(wavpath, length=15, sr=16000): 
    data, sr = librosa.load(wavpath, sr=sr)
    print(len(data), data)
    trimmed = data[:sr*length]
    print(len(trimmed))
    write(wavpath.split('.')[0] + '_trimmed.wav', sr,  trimmed)

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

def state_seq_to_MIDI(state_seq, state_indices, dir, desired_fstub='seqmid', note_dur=1): 
    desired_filename = get_free_filename(desired_fstub, '.mid', directory=dir)
    # Create a PrettyMIDI object
    midi_obj = pretty_midi.PrettyMIDI() # init tempo is 120, so a quarter note is 0.5 sec
    # Create an Instrument instance for a cello instrument
    piano = pretty_midi.Instrument(program=1)
    for i, state in enumerate(state_seq): 
        notes = state_indices[state]
        for note in notes: 
            # Create a Note instance, starting at 0s and ending at 1s
            note_obj = pretty_midi.Note(
                velocity=100, pitch=note, start=note_dur*i, end=note_dur*(i+1))
            piano.notes.append(note_obj)
    midi_obj.instruments.append(piano)
    midi_obj.write(desired_filename)
    return desired_filename

def state_seq_to_MIDI_durations(state_seq, dur_seq, state_indices, dir, desired_fstub='seqmid', note_dur=1): 
    desired_filename = get_free_filename(desired_fstub, '.mid', directory=dir)
    # Create a PrettyMIDI object
    midi_obj = pretty_midi.PrettyMIDI() # init tempo is 120, so a quarter note is 0.5 sec
    # Create an Instrument instance for a cello instrument
    piano = pretty_midi.Instrument(program=1)
    cur_time = 0
    for state, dur in zip(state_seq[:-1], dur_seq): 
        notes = state_indices[state]
        for note in notes: 
            # Create a Note instance, starting at 0s and ending at 1s
            note_obj = pretty_midi.Note(
                velocity=100, pitch=note, start=cur_time*note_dur, end=cur_time + note_dur*int(dur))
            piano.notes.append(note_obj)
        cur_time += dur
    midi_obj.instruments.append(piano)
    midi_obj.write(desired_filename)
    return desired_filename, midi_obj

def one_part_note_list(part, note_dur = 1):
    notes = []
    cur_note = -1
    cur_length = 0
    for i, note in enumerate(part):
        if i == 0:
            cur_note = note
        if i == len(part) - 1:
            if note != cur_note: 
                note_obj = pretty_midi.Note(
                    velocity=100, pitch=cur_note, start=(i-cur_length)*note_dur, end=i*note_dur)
                notes.append(note_obj)
                note_obj = pretty_midi.Note(
                    velocity=100, pitch=note, start=i*note_dur, end=(i+1)*note_dur)
                notes.append(note_obj)
            else: 
                note_obj = pretty_midi.Note(
                    velocity=100, pitch=note, start=(i-cur_length)*note_dur, end=(i+1)*note_dur)
                notes.append(note_obj)
            break
        if note != cur_note: # end previous note 
            note_obj = pretty_midi.Note(
                velocity=100, pitch=cur_note, start=(i-cur_length)*note_dur, end=i*note_dur)
            notes.append(note_obj)
            cur_note = note
            cur_length = 1
        else: # note is continuing
            cur_length += 1
    return notes

def state_seq_to_MIDI_better(state_seq, state_indices, dir, desired_fstub):
    desired_fname = get_free_filename(desired_fstub, '.mid', directory=dir)
    midi_obj = pretty_midi.PrettyMIDI() # init tempo is 120, so a quarter note is 0.5 sec
    piano = pretty_midi.Instrument(program=1)

    sop = []
    alt = [] 
    ten = [] 
    bas = []

    for state in state_seq:
        if type(state) is not list: 
            notes = state_indices[state]
        else: 
            notes = state
        bas.append(notes[0])
        ten.append(notes[1])
        alt.append(notes[2])
        sop.append(notes[3])

    sop_notes = one_part_note_list(sop)
    alt_notes = one_part_note_list(alt)
    ten_notes = one_part_note_list(ten)
    bas_notes = one_part_note_list(bas)

    piano.notes = piano.notes + sop_notes + alt_notes + ten_notes + bas_notes

    midi_obj.instruments.append(piano)
    midi_obj.write(desired_fname)
    return desired_fname, midi_obj


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

    melody_notes, _ = melody_to_MIDI(melody)
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

def midi_to_wav(midi_path,wav_path=None):
    if wav_path == None:
        wav_path = midi_path[:-3] + 'wav'
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

def gen_result_midis(state_seqs, durations, state_indices, res_folder, fstub):
    for seq,durs in zip(state_seqs, durations): 
        new_mid, new_pm = state_seq_to_MIDI_durations(seq, durs, state_indices, res_folder, fstub)
        midi_to_wav(new_mid)

def gen_harmonization_csv():
    melodies, randoms, qs, doodles, bachs = [],[],[],[],[]
    base_melody_url = 'https://harmonization-mturk.s3.us-east-2.amazonaws.com/melody-'
    base_random_url = 'https://harmonization-mturk.s3.us-east-2.amazonaws.com/random-'
    base_q_url = 'https://harmonization-mturk.s3.us-east-2.amazonaws.com/mod-'
    base_doodle_url = 'https://harmonization-mturk.s3.us-east-2.amazonaws.com/doodle-'
    base_bach_url = 'https://harmonization-mturk.s3.us-east-2.amazonaws.com/bach-'
    indices = [0,2,4,17, 18, 19, 25, 26, 27, 28, 31, 40, 41, 43, 46, 47, 51, 53, 59, 60, 63, 64, 66, 67, 70, 74, 79, 86, 99, 100, 109, 112, 117, 119, 120, 121, 122, 145, 157, 158, 159, 160, 171, 176, 179, 183, 186, 189, 192, 204, 205, 223, 239, 244, 245, 247, 248, 258, 259, 263, 270, 273, 275, 276, 280, 283, 284, 285, 287, 296, 303, 305, 308, 311, 313, 314, 315, 317, 319, 322, 323, 328, 329, 330, 332, 333, 335, 336, 341, 342, 346, 349, 350, 352, 359, 360, 361, 363, 366, 368, 370, 373]
    for index in indices: 
        cur_melody_url = base_melody_url + str(index) + '.wav'
        cur_random_url = base_random_url + str(index) + '.wav'
        cur_q_url = base_q_url + str(index) + '.wav'
        cur_doodle_url = base_doodle_url + str(index) + '.wav'
        cur_bach_url = base_bach_url + str(index) + '.wav'
        melodies.append(cur_melody_url)
        randoms.append(cur_random_url)
        qs.append(cur_q_url)
        doodles.append(cur_doodle_url)
        bachs.append(cur_bach_url)

    d = {'melody_url': melodies, 
         'random_url': randoms,
         'q_url': qs,
         'doodle_url': doodles,
         'bach_url': bachs}
    df = pd.DataFrame(data=d)
    df.to_csv('./results/mechanicalturk_csvs/input.csv', index=False)  


def voicings_to_MIDI_durations(voicing_seq, dur_seq, dir, desired_fstub='seqmid', note_dur=1): 
    desired_filename = get_free_filename(desired_fstub, '.mid', directory=dir)
    # Create a PrettyMIDI object
    midi_obj = pretty_midi.PrettyMIDI() # init tempo is 120, so a quarter note is 0.5 sec
    # Create an Instrument instance for a cello instrument
    piano = pretty_midi.Instrument(program=1)
    cur_time = 0
    for notes, dur in zip(voicing_seq, dur_seq): 
        for note in notes: 
            # Create a Note instance, starting at 0s and ending at 1s
            note_obj = pretty_midi.Note(
                velocity=100, pitch=note, start=cur_time*note_dur, end=cur_time + note_dur*int(dur))
            piano.notes.append(note_obj)
        cur_time += dur
    midi_obj.instruments.append(piano)
    midi_obj.write(desired_filename)
    return desired_filename, midi_obj

def melodies_to_MIDI_durations(mel_seq, dur_seq, dir, desired_fstub='seqmid', note_dur=1): 
    desired_filename = get_free_filename(desired_fstub, '.mid', directory=dir)
    # Create a PrettyMIDI object
    midi_obj = pretty_midi.PrettyMIDI() # init tempo is 120, so a quarter note is 0.5 sec
    # Create an Instrument instance for a cello instrument
    piano = pretty_midi.Instrument(program=1)
    cur_time = 0
    for notes, dur in zip(mel_seq, dur_seq):
        if len(notes)==1:
            if notes[0] == -1 : 
                break
            note_obj = pretty_midi.Note(
                velocity=100, pitch=notes[0], start=cur_time*note_dur, end=cur_time + note_dur*int(dur))
            piano.notes.append(note_obj)
        else:
            print("ERROR: too many melody notes")
            sys.exit()
        cur_time += dur
    midi_obj.instruments.append(piano)
    midi_obj.write(desired_filename)
    return desired_filename, midi_obj

if __name__ == "__main__":

    gen_harmonization_csv()

    sys.exit(0)

    with open('./dictionaries/state_dict_3.yaml', 'r') as file:
        state_indices = yaml.safe_load(file)

    with open('./data/jsb_maj_melodies.yaml') as file:
        melodies = yaml.safe_load(file)

    with open('./data/jsb_maj_durations.yaml') as file:
        durations = yaml.safe_load(file)

    with open('./data/jsb_maj_orig_voicings.yaml') as file:
        voicings = yaml.safe_load(file)

    melody_dir = './results/human_eval/melodies/'
    for melody, duration in zip(melodies['test'], durations['test']): 
        new_mid, new_pm = melodies_to_MIDI_durations(melody, duration, melody_dir, desired_fstub='melody', note_dur=1)
        midi_to_wav(new_mid)

    sys.exit(0)

    orig_dir = './results/human_eval/bach/'
    for voicing, duration in zip(voicings['test'], durations['test']): 
        new_mid, new_pm = voicings_to_MIDI_durations(voicing, duration, orig_dir, desired_fstub='bach', note_dur=1)
        midi_to_wav(new_mid)
    ### CREATE MIDIS FOR ORIGINAL VOICINGS ### 

    test_durations = durations['test']

    longer_durs = [] 
    for i, durs in enumerate(test_durations):
        if len(durs) > 4 and len(durs) < 8:
            print(len(durs))
            longer_durs.append(i)
    print("NUMBER:", len(longer_durs))
    print(longer_durs)

    '''with open('./data/jsb_major_orig_voicings.yaml', 'r') as file: 
        jsb_voicings = yaml.safe_load(file)

    test_vocs = jsb_voicings['test']
    gen_result_midis(test_vocs, state_indices, './results/human_eval/bach/', 'jsb')
    
    with open('./results/for_table/random_voicings.yaml', 'r') as file: 
        rand_voc_seqs = yaml.safe_load(file)

    with open('./results/for_table/model_voicings.yaml', 'r') as file: 
        mod_voc_seqs = yaml.safe_load(file)

    with open('./results/for_table/random_harmonizations.yaml', 'r') as file: 
        rand_harm_seqs = yaml.safe_load(file)

    with open('./results/for_table/model_harmonizations.yaml', 'r') as file: 
        mod_harm_seqs = yaml.safe_load(file)

    with open('./results/for_table/random_free.yaml', 'r') as file: 
        rand_free_seqs = yaml.safe_load(file)

    with open('./results/for_table/model_free.yaml', 'r') as file: 
        mod_free_seqs = yaml.safe_load(file)'''

    #gen_result_midis(rand_voc_seqs, test_durations, state_indices, './results/human_eval/voicing/', 'random')
    #gen_result_midis(mod_voc_seqs, test_durations, state_indices, './results/human_eval/voicing/', 'mod')
    #gen_result_midis(rand_harm_seqs, test_durations, state_indices, './results/human_eval/harm/', 'random')
    #gen_result_midis(mod_harm_seqs, test_durations, state_indices, './results/human_eval/harm/', 'mod')
    #gen_result_midis(rand_free_seqs, test_durations, state_indices, './results/human_eval/free/', 'random')
    #gen_result_midis(mod_free_seqs, test_durations, state_indices, './results/human_eval/free/', 'mod')

    sys.exit(0)

    '''pianoroll = new_pm.instruments[0].get_piano_roll()
    _, ax = plt.subplots()
    ax  = custom_plot_pianoroll(ax, pianoroll, resolution=2)
    plt.savefig()

    pianoroll = old_pm.instruments[0].get_piano_roll()
    _, ax = plt.subplots()
    ax  = custom_plot_pianoroll(ax, pianoroll, resolution=2)
    plt.show()

    midi_to_wav(new_mid)
    midi_to_wav(old_mid)'''

    # UNIT TEST: melody_to_MIDI #

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