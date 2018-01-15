
import json
import numpy as np
import copy
# import xlsxwriter
import matplotlib.pyplot as plt
import os
import sys
import time

FOLDER_DATA = 'kaggle2/'


#### DEFINE CONSTRAIN HERE ###
MINLEN = 0.0 # duration
MAXLEN = 30.0 
MIN_INSTANCES = 40 # instance of sound per category



# this the result of the mapping from FS sounds to ASO.
# 268k sounds with basic metadata and their corresponding ASO id.
# useful to get the duration of every sound
try:
    with open(FOLDER_DATA + 'json/FS_sounds_ASO_postIQA.json') as data_file:
        data_duration = json.load(data_file)
except:
    raise Exception('CHOOSE A MAPPING FILE AND ADD IT TO ' + FOLDER_DATA +'json/ FOLDER (THE FILE INCLUDE DURATION INFORMATION NEEDED)')



# load json with votes, to select only PP and PNP
try:
    with open(FOLDER_DATA + 'json/votes_sounds_annotations.json') as data_file:
        data_votes = json.load(data_file)
except:
    raise Exception('ADD THE FILE CONTAINING THE VOTES (list of dict "value", "freesound_sound_id", "node_id") AND ADD IT TO THE FOLDER ' + FOLDER_DATA +'json/')

#
#
# try:
# # load json with ontology, to map aso_ids to understandable category names
#     with open(FOLDER_DATA + 'json/ontology.json') as data_file:
#          data_onto = json.load(data_file)
# except:
#     raise Exception('ADD AN ONTOLOGY JSON FILE TO THE FOLDER ' + FOLDER_DATA +'json/')

# all_ids of the sounds that compose the dataset (before any kind of filtering in post-pro) 9281
# durations are in the range [0:30], and only PP and PNP are considered
with open(FOLDER_DATA + 'all_ids.json') as data_file:
    all_ids = json.load(data_file)

# all_ids of the sounds that compose the DEVELOPMENT dataset (before any kind of filtering in post-pro)
# durations are in the range [0:30], and only PP and PNP are considered
with open(FOLDER_DATA + 'dataset_dev.json') as data_file:
    dataset_dev = json.load(data_file)


# all_ids of the sounds that compose the EVALUATION dataset (before any kind of filtering in post-pro)
# durations are in the range [0:30], and only PP and PNP are considered
with open(FOLDER_DATA + 'dataset_eval.json') as data_file:
    dataset_eval = json.load(data_file)



# --------------------------------------functions for plotting---------------------------------

def plot_histogram(x,bins,fig_title):
    # plot histogram given an array x
    plt.figure()
    n, bins, patches = plt.hist(x, bins=bins, facecolor='blue', alpha=0.75, histtype='bar', ec='black')
    plt.xlabel('seconds')
    plt.ylabel('# of sounds')
    plt.title(fig_title)
    # plt.axis([40, 160, 0, 0.03])
    plt.grid(True)
    plt.show()
    # fig says there are 1.4k sounds shorter than 1s, but in the proposal we say many more



# --------------------------------------end functions for plotting---------------------------------

# --histogram of clip durations for all clips
durations = list()
for id in all_ids:
    # get and append clip duration
    durations.append(data_duration[str(id)]['duration'])

fig_title = 'all initial clips: ' + str(len(durations))
bins = [0, 1, 2, 3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
plot_histogram(durations,bins,fig_title)




# -- histogram of clip durations for all clips of DEVELOPMENT set
durations_dev = list()
start_time = time.time()

for cat in dataset_dev:
    for id in cat['sound_ids']:
        durations_dev.append(data_duration[str(id)]['duration'])

fig_title = 'all clips from DEV set: ' + str(len(durations_dev))
plot_histogram(durations_dev,30,fig_title)

elapsed_time = time.time() - start_time
print('elapsed_time is: ' + str(elapsed_time))




# -- histogram of clip durations for all clips of DEVELOPMENT set
durations_eval = list()

for cat in dataset_eval:
    for id in cat['sound_ids']:
        durations_eval.append(data_duration[str(id)]['duration'])

fig_title = 'all clips from EVAL set: ' + str(len(durations_eval))
plot_histogram(durations_eval,30,fig_title)




# -- histogram of clip durations for all clips validated as PP
# NOTE: considering only one vote in each sound. this is not correct, as around 2% of sounds have multiple (2) labels.
# In those cases, I only consider the first vote that is found. Since this is 2%, for preliminary results it is ok
durations_PP = list()
start_time = time.time()
for id in all_ids:
    # is this sound voted as PP
    for v in data_votes:
        if id in v.values():
            vote = v['value']
            if vote == 1.0:
                # get and append clip duration
                durations_PP.append(data_duration[str(id)]['duration'])
            break

fig_title = 'all initial 9281 clips -- only PP'
plot_histogram(durations_PP,30,fig_title)


elapsed_time = time.time() - start_time
print(elapsed_time)


#
# # -- histogram of clip durations for all clips validated as PNP
# # NOTE: considering only one vote in each sound. this is not correct, as around 2% of sounds have multiple (2) labels.
# # In those cases, I only consider the first vote that is found. Since this is 2%, for preliminary results it is ok
durations_PNP = list()
start_time = time.time()
for id in all_ids:
    # is this sound voted as PNP
    for v in data_votes:
        if id in v.values():
            vote = v['value']
            if vote == 0.5:
                # get and append clip duration
                durations_PNP.append(data_duration[str(id)]['duration'])
            break

fig_title = 'all initial 9281 clips -- only PNP'
plot_histogram(durations_PNP,30,fig_title)


elapsed_time = time.time() - start_time
print(elapsed_time)







# # GET ANNOTATIONS WITH VOTES 0.5 (PNP) or 1.0 (PP)
# for v in data_votes:
#     # apply duration filter
#     if data_duration[str(v['freesound_sound_id'])]['duration']<=MAXLEN and data_duration[str(v['freesound_sound_id'])]['duration']>=MINLEN:
#         # apply PRESENCE filter
#         if v['value']>0.4:
#             result[v['node_id']].add(v['freesound_sound_id'])
#










a=9






# # GET ANNOTATIONS WITH VOTES 0.5 (PNP) or 1.0 (PP)
# for v in data_votes:
#     # apply duration filter
#     if data_duration[str(v['freesound_sound_id'])]['duration']<=MAXLEN and data_duration[str(v['freesound_sound_id'])]['duration']>=MINLEN:
#         # apply PRESENCE filter
#         if v['value']>0.4:
#             result[v['node_id']].add(v['freesound_sound_id'])