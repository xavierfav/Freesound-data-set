
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

# all_ids of the sounds that compose the DEVELOPMENT dataset (after filtering in post-pro)
# durations are in the range [0:30], and only PP and PNP are considered
with open(FOLDER_DATA + 'dataset_dev_filter.json') as data_file:
    dataset_dev_filter = json.load(data_file)

# all_ids of the sounds that compose the EVALUATION dataset (before any kind of filtering in post-pro)
# durations are in the range [0:30], and only PP and PNP are considered
with open(FOLDER_DATA + 'dataset_eval.json') as data_file:
    dataset_eval = json.load(data_file)

# all_ids of the sounds that compose the EVALUATION dataset (after filtering in post-pro)
# durations are in the range [0:30], and only PP and PNP are considered
with open(FOLDER_DATA + 'dataset_eval_filter.json') as data_file:
    dataset_eval_filter = json.load(data_file)


# --------------------------------------functions for plotting---------------------------------
# turn interactive mode on
plt.ion()

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
    # plt.pause(0.001)
    # fig says there are 1.4k sounds shorter than 1s, but in the proposal we say many more



# --------------------------------------end functions for plotting---------------------------------

# # --histogram of clip durations for all clips. contains a few categories that will be filtered out later. just an approximation
# durations = list()
# for id in all_ids:
#     # get and append clip duration
#     durations.append(data_duration[str(id)]['duration'])
#
# fig_title = 'all initial clips: ' + str(len(durations))
bins1 = [0, 1, 2, 3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
# plot_histogram(durations,bins1,fig_title)
#
bins10 = [0, 10, 20, 30]
# plot_histogram(durations,bins10,fig_title)
#
#
#
#
#
# # -- histogram of clip durations for all clips of DEVELOPMENT set before filtering---
# # durations_dev = list()
# #
# # for cat in dataset_dev:
# #     for id in cat['sound_ids']:
# #         durations_dev.append(data_duration[str(id)]['duration'])
# #
# # fig_title = 'all clips from DEV set before filtering: ' + str(len(durations_dev))
# # plot_histogram(durations_dev,bins1,fig_title)
# #
# # plot_histogram(durations_dev,bins10,fig_title)
#
# # -- histogram of clip durations for all clips of DEVELOPMENT set after filtering----
# durations_dev_filter = list()
#
# for cat in dataset_dev_filter:
#     for id in cat['sound_ids']:
#         durations_dev_filter.append(data_duration[str(id)]['duration'])
#
# fig_title = 'all clips from DEV set after filtering: ' + str(len(durations_dev_filter))
# plot_histogram(durations_dev_filter,bins1,fig_title)
#
# plot_histogram(durations_dev_filter,bins10,fig_title)
#
#
#
#
#
#
# # -- histogram of clip durations for all clips of EVALUATION set before filtering---
# # durations_eval = list()
# #
# # for cat in dataset_eval:
# #     for id in cat['sound_ids']:
# #         durations_eval.append(data_duration[str(id)]['duration'])
# #
# # fig_title = 'all clips from EVAL set before filtering: ' + str(len(durations_eval))
# # plot_histogram(durations_eval,bins1,fig_title)
# # plot_histogram(durations_eval,bins10,fig_title)
#
# # -- histogram of clip durations for all clips of EVALUATION set after filtering----
# durations_eval_filter = list()
#
# for cat in dataset_eval_filter:
#     for id in cat['sound_ids']:
#         durations_eval_filter.append(data_duration[str(id)]['duration'])
#
# fig_title = 'all clips from EVAL set after filtering: ' + str(len(durations_eval_filter))
# plot_histogram(durations_eval_filter,bins1,fig_title)
# plot_histogram(durations_eval_filter,bins10,fig_title)
#
#
#
#
#
#
#
#
#
#
#
#
# # -- histogram of clip durations for all clips validated as PP
# # NOTE: considering only one vote in each sound. this is not correct, as around 2% of sounds have multiple (2) labels.
# # In those cases, I only consider the first vote that is found. Since this is 2%, for preliminary results it is ok
# # durations_PP = list()
# # start_time = time.time()
# # for id in all_ids:
# #     # is this sound voted as PP
# #     for v in data_votes:
# #         if id in v.values():
# #             vote = v['value']
# #             if vote == 1.0:
# #                 # get and append clip duration
# #                 durations_PP.append(data_duration[str(id)]['duration'])
# #             break
# #
# # fig_title = 'all initial 9281 clips -- only PP'
# # plot_histogram(durations_PP,30,fig_title)
# #
# #
# # elapsed_time = time.time() - start_time
# # print(elapsed_time)
#
#



durations_PP = list()
# start_time = time.time()

sounds_voted_PP = [v['freesound_sound_id'] for v in data_votes if v['value'] ==1.0]
sounds_voted_PP_counted_only_once = set(sounds_voted_PP)
sounds_voted_PP_more_than_once = set([x for x in sounds_voted_PP if sounds_voted_PP.count(x) > 1])

print 'sounds voted as PP counted only once: ' + str(len(sounds_voted_PP_counted_only_once))
print 'sounds voted as PP more than once: ' + str(len(sounds_voted_PP_more_than_once))
print 'annotations validated as PP: ' + str(len(sounds_voted_PP))
print 'nothing is matching the paper, or between variables...'

for id in all_ids:
    # is this sound voted as PP
    if id in sounds_voted_PP_counted_only_once:
        # get and append clip duration
        durations_PP.append(data_duration[str(id)]['duration'])


fig_title = 'of all initial 9281 clips -- only PP: ' + str(len(durations_PP))
plot_histogram(durations_PP,bins1,fig_title)
plot_histogram(durations_PP,bins10,fig_title)

# elapsed_time2 = time.time() - start_time
# print(elapsed_time2)





#TOO LONG
# # -- histogram of clip durations for all clips validated as PNP
# # NOTE: considering only one vote in each sound. this is not correct, as around 2% of sounds have multiple (2) labels.
# # # In those cases, I only consider the first vote that is found. Since this is 2%, for preliminary results it is ok
# durations_PNP = list()
# start_time = time.time()
# for id in all_ids:
#     # is this sound voted as PNP
#     for v in data_votes:
#         if id in v.values():
#             vote = v['value']
#             if vote == 0.5:
#                 # get and append clip duration
#                 durations_PNP.append(data_duration[str(id)]['duration'])
#             break
#
# fig_title = 'all initial 9281 clips -- only PNP'
# plot_histogram(durations_PNP,30,fig_title)
#
#
# elapsed_time = time.time() - start_time
# print(elapsed_time)


durations_PNP = list()
# start_time = time.time()

sounds_voted_PNP = [v['freesound_sound_id'] for v in data_votes if v['value'] ==0.5]

sounds_voted_PNP_counted_only_once = set(sounds_voted_PNP)
sounds_voted_PNP_more_than_once = set([x for x in sounds_voted_PNP if sounds_voted_PNP.count(x) > 1])

print 'sounds voted as PNP counted only once: ' + str(len(sounds_voted_PNP_counted_only_once))
print 'sounds voted as PNP more than once: ' + str(len(sounds_voted_PNP_more_than_once))
print 'annotations validated as PNP: ' + str(len(sounds_voted_PNP))
print 'nothing is matching the paper, or between variables...'


for id in all_ids:
    # is this sound voted as PP
    if id in sounds_voted_PNP_counted_only_once:
        # get and append clip duration
        durations_PNP.append(data_duration[str(id)]['duration'])


fig_title = 'of all initial 9281 clips -- only PNP: ' + str(len(durations_PNP))
plot_histogram(durations_PNP,bins1,fig_title)
plot_histogram(durations_PNP,bins10,fig_title)

# elapsed_time2 = time.time() - start_time
# print(elapsed_time2)

# NOTE_ PP + PNP are more than original files:
# they must be the number of labels, but how?



# ------------------------------box plots

data = [durations_PP, durations_PNP]
# multiple box plots on one figure

fig = plt.figure()
ax = fig.add_subplot(111)
ax.boxplot(data)
ax.set_xticklabels(['PP', 'PNP'])
plt.ylabel('seconds')
plt.title('review input data. make sure it is ok')
plt.show()


a=9






# # GET ANNOTATIONS WITH VOTES 0.5 (PNP) or 1.0 (PP)
# for v in data_votes:
#     # apply duration filter
#     if data_duration[str(v['freesound_sound_id'])]['duration']<=MAXLEN and data_duration[str(v['freesound_sound_id'])]['duration']>=MINLEN:
#         # apply PRESENCE filter
#         if v['value']>0.4:
#             result[v['node_id']].add(v['freesound_sound_id'])