import pandas as pd
import os
import yaml
import numpy as np

'''
305 training chorales, ~80 test chorales

dur = major, moll = minor
H = B,
B = Bflat
'''

chord_dict = {

}

major_shift_amounts = {
    'C': 0,
    'C#': -1,
    'Db': -1,
    'D': -2,
    'D#':-3,
    'Eb':-3,
    'E':-4,
    'F':-5,
    'F#':-6,
    'Gb':-6,
    'G':5,
    'G#':4,
    'Ab':4,
    'A':3,
    'A#':2,
    'Bb':2,
    'B':1,
}

# 0 C 1 C#/Db 2 D 3 D#/Eb 4 E 5 F 
# 6 F#/Gb 7 G 8 G#/Ab 9 A 10 A#/Bb 11 B


def key_estimate(chorale):
    # Chorale is a list of lists of 4 pitches representing chords
    note_counts = {}
    for chord in chorale: 
        for note in chord: 
            cur_note = note%12
            if cur_note in note_counts.keys():
                note_counts[cur_note] +=1
            else: 
                note_counts[cur_note] =1
    sorted_notecounts = {k: v for k, v in sorted(note_counts.items(), key=lambda item: item[1])}
    print(note_counts)

def get_key_info(key_data_dir): 
    chorale_keys_major = {}
    chorale_keys_minor = {}

    for chorale in os.listdir(key_data_dir):
        chorale_number = chorale[3:6]
        chorale_file = open(key_data_dir+chorale, 'r')
        chorale_text = chorale_file.readlines()
        key_info = chorale_text[2][9:-1]
        letter, mode = key_info.split('-')
        print(chorale_number, letter, mode)
        if letter == "B":
            letter = "Bb"
        elif letter == "H":
            letter = "B"
        if mode == 'dur':
            chorale_keys_major[chorale_number] = {}
            chorale_keys_major[chorale_number]['key'] = letter
        else:
            chorale_keys_minor[chorale_number] = {}
            chorale_keys_minor[chorale_number]['key'] = letter

    # save key info 
    with open("chorale_keys_min.yaml","w") as file: 
        yaml.dump(chorale_keys_minor,file)

    with open("chorale_keys_maj.yaml","w") as file: 
        yaml.dump(chorale_keys_major,file)

if __name__ == "__main__":
    key_data_dir = '/Users/sadiela/Documents/phd/courses/courses_spring_2023/ec700reinforcementlearning/final_project/data/bach_chorales_keys/'
    #get_key_info(key_data_dir)

    with open('chorale_keys_maj.yaml', 'r') as file:
        chorale_keys_maj = yaml.safe_load(file)
    
    maj_chorales = list(chorale_keys_maj.keys())

    # Transpose data
    training_data_dir = '/Users/sadiela/Documents/phd/courses/courses_spring_2023/ec700reinforcementlearning/final_project/data/jsb_chorales/train/'
    training_data_c_dir = '/Users/sadiela/Documents/phd/courses/courses_spring_2023/ec700reinforcementlearning/final_project/data/jsb_chorales_c/train/'
    min_values = np.array([128,128,128,128])
    max_values = np.array([0,0,0,0])
    for chorale in os.listdir(training_data_dir):
        chorale_num = str(chorale[8:11])
        if chorale_num in maj_chorales:
            cur_chord_sequence = []
            key = chorale_keys_maj[chorale_num]['key']
            print(chorale, key, "MAJOR, shift amount:", major_shift_amounts[key])
            arr = pd.read_csv(training_data_dir + chorale).to_numpy()
            unique_chords = np.array(arr[0,:]).reshape(1,4)
            if key == "C":
                # open CSV file
                arr = np.flip(arr, 1) + major_shift_amounts[key] # flip so it goes b t a s
                print(np.unique(arr%12))
                previous = np.array(arr[0,:]).reshape(1,4)
                print("SHAPE:", previous.shape)
                for i in range(arr.shape[0]):
                    if not np.array_equal(arr[i,:], previous):
                        unique_chords = np.concatenate((unique_chords, arr[i,:].reshape(1,4)), axis=0)
                        print("CHORDS", unique_chords),
                        print(np.unique(arr[i,:]%12))
                        input("Continue...")
                    previous = arr[i,:]
                input("Finished song")
                
                min_values = np.minimum(min_values, arr.min(axis=0))
                max_values = np.maximum(max_values,arr.max(axis=0))
                print(min_values, max_values)

    '''
    # step 1: load data
    data_path = '/Users/sadiela/Documents/phd/courses/courses_spring_2023/ec700reinforcementlearning/final_project/data/bach_choral_set_dataset.csv'
    df = pd.read_csv(data_path)

    # step 2: split into separate dfs based on choral_ID
    chorales=df['choral_ID'].unique().tolist() # 60 total chorales
    #print(chorales, len(chorales))

    chorale_dict = {elem : pd.DataFrame() for elem in chorales}

    for key in chorale_dict.keys():
        chorale_dict[key] = df[:][df.choral_ID == key]

    #print(chorale_dict['000106b_'])

    # step 3: for each chorale, determine the key
    pitch_dict = {
        1:'C',
        2:'C#/Db',
        3:'D',
        4:'D#/Eb',
        5:'E',
        6:'F',
        7:'F#/Gb',
        8:'G',
        9:'G#/Ab',
        10:'A',
        11:'A#/Bb',
        12:'B',
    }

    for key in chorale_dict.keys():
        cur_df = chorale_dict[key] 
        pitch_dict = {}
        for i in range(1,13):
            col_name = "pitch_" + str(i)
            val_counts = cur_df[col_name].value_counts()
            print(col_name)
            if (cur_df[col_name]=="YES").any():
                pitch_dict[i] = val_counts['YES']
        print("PITCHLIST:", pitch_dict) #, len(pitch_list))
        input("Continue")
    '''