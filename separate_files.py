import random
import os
import numpy as np
import shutil
import write_midi
from convert_clean import *

ROOT_PATH = '/Users/greenuuh/Desktop/'
MUSIC_STYLE = "Pop"
test_path = 'MIDI/' + MUSIC_STYLE + '/' + MUSIC_STYLE + '_test/'
this_converter_path = os.path.join(ROOT_PATH, test_path + 'converter')
this_cleaner_path = os.path.join(ROOT_PATH, test_path+ 'cleaner')
test_ratio = 0.1

def get_bar_piano_roll(piano_roll):
    if int(piano_roll.shape[0] % 64) is not 0:
        if LAST_BAR_MODE == 'fill':
            piano_roll = np.concatenate((piano_roll, np.zeros((64 - piano_roll.shape[0] % 64, 128))), axis=0)
        elif LAST_BAR_MODE == 'remove':
            piano_roll = np.delete(piano_roll,  np.s_[-int(piano_roll.shape[0] % 64):], axis=0)
    piano_roll = piano_roll.reshape(-1, 64, 128)
    return piano_roll


def to_binary(bars, threshold=0.0):
    """Turn velocity value into boolean"""
    track_is_max = tf.equal(bars, tf.reduce_max(bars, axis=-1, keep_dims=True))
    track_pass_threshold = (bars > threshold)
    out_track = tf.logical_and(track_is_max, track_pass_threshold)
    return out_track

def divideSet():
	if not os.path.exists(os.path.join(ROOT_PATH, test_path + 'origin_midi')):
	    os.makedirs(os.path.join(ROOT_PATH, test_path + 'origin_midi'))
	l = [f for f in os.listdir(os.path.join(ROOT_PATH, 'MIDI/' + MUSIC_STYLE + '/' + MUSIC_STYLE + '_midi'))]
	print(l)
	idx = np.random.choice(len(l), int(test_ratio * len(l)), replace=False)
	print(len(idx))
	for i in idx:
	    shutil.move(os.path.join(ROOT_PATH, 'MIDI/' + MUSIC_STYLE + '/' + MUSIC_STYLE + '_midi', l[i]),
	                os.path.join(ROOT_PATH, test_path + 'origin_midi', l[i]))

def convert_clean():
    """Main function of the converter"""
    midi_paths = get_midi_path(os.path.join(ROOT_PATH, 'MIDI/' + MUSIC_STYLE +'/' + MUSIC_STYLE + '_test/origin_midi'))
    midi_dict = {}
    kv_pairs = [converter(midi_path) for midi_path in midi_paths]
    for kv_pair in kv_pairs:
        if kv_pair is not None:
            midi_dict[kv_pair[0]] = kv_pair[1]

    with open(os.path.join(ROOT_PATH, test_path + 'midis.json'), 'w') as outfile:
        json.dump(midi_dict, outfile)

    print("[Done] {} files out of {} have been successfully converted".format(len(midi_dict), len(midi_paths)))

    with open(os.path.join(ROOT_PATH, test_path + 'midis.json')) as infile:
        midi_dict = json.load(infile)
    count = 0
    make_sure_path_exists(this_cleaner_path)
    midi_dict_clean = {}
    for key in midi_dict:
        if midi_filter(midi_dict[key]):
            midi_dict_clean[key] = midi_dict[key]
            count += 1
            shutil.copyfile(os.path.join(this_converter_path, key + '.npz'),
                            os.path.join(this_cleaner_path, key + '.npz'))

    with open(os.path.join(ROOT_PATH, test_path + 'midis_clean.json'), 'w') as outfile:
        json.dump(midi_dict_clean, outfile)

    print("[Done] {} files out of {} have been successfully cleaned".format(count, len(midi_dict)))

def copyCleanerMidi():
	if not os.path.exists(os.path.join(ROOT_PATH, test_path + 'cleaner_midi')):
	    os.makedirs(os.path.join(ROOT_PATH, test_path + 'cleaner_midi'))
	l = [f for f in os.listdir(os.path.join(ROOT_PATH, test_path + 'cleaner'))]
	print(l)
	print(len(l))
	for i in l:
	    shutil.copy(os.path.join(ROOT_PATH, test_path + 'origin_midi', os.path.splitext(i)[0] + '.mid'),
	                os.path.join(ROOT_PATH, test_path + 'cleaner_midi', os.path.splitext(i)[0] + '.mid'))

def save_midis(bars, file_path, tempo=80.0):
    padded_bars = np.concatenate((np.zeros((bars.shape[0], bars.shape[1], 24, bars.shape[3])), bars,
                                  np.zeros((bars.shape[0], bars.shape[1], 20, bars.shape[3]))), axis=2)
    pause = np.zeros((bars.shape[0], 64, 128, bars.shape[3]))
    images_with_pause = padded_bars
    images_with_pause = images_with_pause.reshape(-1, 64, padded_bars.shape[2], padded_bars.shape[3])
    images_with_pause_list = []
    for ch_idx in range(padded_bars.shape[3]):
        images_with_pause_list.append(images_with_pause[:, :, :, ch_idx].reshape(images_with_pause.shape[0],
                                                                                 images_with_pause.shape[1],
                                                                                 images_with_pause.shape[2]))
    # write_midi.write_piano_rolls_to_midi(images_with_pause_list, program_nums=[33, 0, 25, 49, 0],
    #                                      is_drum=[False, True, False, False, False], filename=file_path, tempo=80.0)
    write_midi.write_piano_rolls_to_midi(images_with_pause_list, program_nums=[0], is_drum=[False], filename=file_path,
                                         tempo=tempo, beat_resolution=4)

def mergeAndCrop():
	if not os.path.exists(os.path.join(ROOT_PATH, test_path + 'cleaner_midi_gen')):
	    os.makedirs(os.path.join(ROOT_PATH, test_path + 'cleaner_midi_gen'))
	if not os.path.exists(os.path.join(ROOT_PATH, test_path + 'cleaner_npy')):
	    os.makedirs(os.path.join(ROOT_PATH, test_path + 'cleaner_npy'))
	l = [f for f in os.listdir(os.path.join(ROOT_PATH, test_path + 'cleaner_midi'))]
	print(l)
	count = 0
	for i in range(len(l)):
	    try:
	        multitrack = Multitrack(beat_resolution=4, name=os.path.splitext(l[i])[0])
	        x = pretty_midi.PrettyMIDI(os.path.join(ROOT_PATH, test_path + 'cleaner_midi', l[i]))
	        multitrack.parse_pretty_midi(x)

	        category_list = {'Piano': [], 'Drums': []}
	        program_dict = {'Piano': 0, 'Drums': 0}

	        for idx, track in enumerate(multitrack.tracks):
	            if track.is_drum:
	                category_list['Drums'].append(idx)
	            else:
	                category_list['Piano'].append(idx)
	        tracks = []
	        merged = multitrack[category_list['Piano']].get_merged_pianoroll()
	        print(merged.shape)
	
	        pr = get_bar_piano_roll(merged)
	        print(pr.shape)
	        pr_clip = pr[:, :, 24:108]
	        print(pr_clip.shape)
	        if int(pr_clip.shape[0] % 4) != 0:
	            pr_clip = np.delete(pr_clip, np.s_[-int(pr_clip.shape[0] % 4):], axis=0)
	        pr_re = pr_clip.reshape(-1, 64, 84, 1)
	        print(pr_re.shape)
	        save_midis(pr_re, os.path.join(ROOT_PATH, test_path + 'cleaner_midi_gen', os.path.splitext(l[i])[0] +
	                                       '.mid'))
	        np.save(os.path.join(ROOT_PATH, test_path + 'cleaner_npy', os.path.splitext(l[i])[0] + '.npy'), pr_re)
	    except:
	        count += 1
	        print('Wrong', l[i])
	        continue
	print(count)

def concactArray():
	l = [f for f in os.listdir(os.path.join(ROOT_PATH, test_path + 'cleaner_npy'))]
	print(l)
	train = np.load(os.path.join(ROOT_PATH, test_path + 'cleaner_npy', l[0]))
	print(train.shape, np.max(train))
	for i in range(1, len(l)):
	    print(i, l[i])
	    t = np.load(os.path.join(ROOT_PATH, test_path + 'cleaner_npy', l[i]))
	    train = np.concatenate((train, t), axis=0)
	print(train.shape)
	np.save(os.path.join(ROOT_PATH, test_path + MUSIC_STYLE + '_test_piano.npy'), (train > 0.0))

def dividePhrases():
	if not os.path.exists(os.path.join(ROOT_PATH, test_path + 'phrase_test')):
	    os.makedirs(os.path.join(ROOT_PATH, test_path + 'phrase_test'))
	x = np.load(os.path.join(ROOT_PATH, test_path + MUSIC_STYLE + '_test_piano.npy'))
	print(x.shape)
	count = 0
	for i in range(x.shape[0]):
	    if np.max(x[i]):
	        count += 1
	        np.save(os.path.join(ROOT_PATH, test_path + 'phrase_test/' + MUSIC_STYLE + '_piano_test_{}.npy'.format(i+1)), x[i])
	        print(x[i].shape)
		if count == 11216:
		    break
	print(count)

def main():
	#divideSet()
	convert_clean()
	copyCleanerMidi()
	mergeAndCrop()
	concactArray()
	dividePhrases()



if __name__ == "__main__":
    main()