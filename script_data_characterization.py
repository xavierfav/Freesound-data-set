
import json
import numpy as np
import copy
# import xlsxwriter
import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.get_backend()

# wm = plt.get_current_fig_manager()
# wm.window.attributes('-topmost', 1)
# wm.window.attributes('-topmost', 0)

import os
import sys
import time

FOLDER_DATA = 'kaggle2/'


#### DEFINE CONSTRAIN HERE ###
# MINLEN = 0.0 # duration
# MAXLEN = 30.0
# MIN_INSTANCES = 40 # instance of sound per category



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
try:
# load json with ontology, to map aso_ids to understandable category names
    with open(FOLDER_DATA + 'json/ontology.json') as data_file:
         data_onto = json.load(data_file)
except:
    raise Exception('ADD AN ONTOLOGY JSON FILE TO THE FOLDER ' + FOLDER_DATA +'json/')

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

# correspondence between low level categories and high level categories
with open(FOLDER_DATA + 'merge_categories.json') as data_file:
    merge_categories = json.load(data_file)




# --------------------------------------functions for plotting---------------------------------
# turn interactive mode on
plt.ion()
SPLITFIGS = False
SLAVE_BOXPLOT_DURATIONS = True

def plot_histogram(x,bins,fig_title,axes):
    # plot histogram given an array x
    plt.figure()
    n, bins, patches = plt.hist(x, bins=bins, facecolor='blue', alpha=0.75, histtype='bar', ec='black')
    plt.xlabel('seconds')
    plt.ylabel('# of sounds')
    plt.title(fig_title)
    plt.axis(axes)
    plt.grid(True)
    # plt.pause(0.001)

    # trials to open figures in the back to avoid interrupting
    wm = plt.get_current_fig_manager()
    # wm.window.attributes('-topmost', 1)
    wm.window.attributes('-topmost', 0)
    # get_current_fig_manager().window.attributes('-topmost', 0)
    # fig = gcf()
    # fig.canvas.manager.window.attributes('-topmost', 0)
    # plt.show()


def plot_boxplot(data,x_labels,fig_title,y_label):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # for tick in ax.get_xticklabels():
    #     tick.set_rotation(45)
    plt.xticks(fontsize=8, rotation=45)
    bp = ax.boxplot(data, patch_artist=True)
    ## change color and linewidth of the whiskers
    for whisker in bp['whiskers']:
        whisker.set(color='#7570b3', linewidth=1)

    for flier in bp['fliers']:
        flier.set(marker='.', color='#e7298a', alpha=0.5)

    ## change color and linewidth of the medians
    for median in bp['medians']:
        median.set(color='#ef0707', linewidth=3)

    ax.set_xticklabels(x_labels)
    plt.ylabel(y_label)
    plt.title(fig_title)
    plt.grid(True)
    plt.show()
    # plt.pause(0.001)


def plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda):
    ind = np.arange(len(data_bottom))  # the x locations for the groups
    width = 0.5  # the width of the bars: can also be len(x) sequence
    axes = [-0.5, len(data_bottom), 0, 170]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    p1 = plt.bar(ind, data_bottom, width)
    p2 = plt.bar(ind, data_up, width, bottom=data_bottom)
    plt.xticks(fontsize=8, rotation=45)
    plt.xticks(ind, x_labels)
    plt.ylabel(y_label)
    plt.title(fig_title)
    # plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0]), legenda)
    plt.axis(axes)
    ax.yaxis.grid(True)
    # plt.grid(True)
    plt.show()

bins1 = [0, 1, 2, 3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
axes1 = [0, 30, 0, 1330]
bins10 = [0, 10, 20, 30]
axes10 = [0, 30, 0, 7000]


def recursive_len(item):
    if type(item) == list:
        return sum(recursive_len(subitem) for subitem in item)
    else:
        return 1
# --------------------------------------end functions for plotting---------------------------------
# --------------------------------------end functions for plotting---------------------------------
# --------------------------------------end functions for plotting---------------------------------



# # --histogram of clip durations for all clips. contains a few categories that will be filtered out later. just an approximation
durations = list()
for id in all_ids:
    # get and append clip duration
    durations.append(data_duration[str(id)]['duration'])

fig_title = 'all initial clips: ' + str(len(durations))

plot_histogram(durations, bins1, fig_title, axes1)
plot_histogram(durations, bins10, fig_title, axes10)





# -- histogram of clip durations for all clips of DEVELOPMENT set before filtering---
# durations_dev = list()
#
# for cat in dataset_dev:
#     for id in cat['sound_ids']:
#         durations_dev.append(data_duration[str(id)]['duration'])
#
# fig_title = 'all clips from DEV set before filtering: ' + str(len(durations_dev))
# plot_histogram(durations_dev,bins1,fig_title)
#
# plot_histogram(durations_dev,bins10,fig_title)

# -- histogram of clip durations for all clips of DEVELOPMENT set after filtering----
durations_dev_filter = list()

for cat in dataset_dev_filter:
    for id in cat['sound_ids']:
        durations_dev_filter.append(data_duration[str(id)]['duration'])

fig_title = 'all clips from DEV set after filtering: ' + str(len(durations_dev_filter))
plot_histogram(durations_dev_filter,bins1,fig_title,axes1)

plot_histogram(durations_dev_filter,bins10,fig_title,axes10)






# -- histogram of clip durations for all clips of EVALUATION set before filtering---
# durations_eval = list()
#
# for cat in dataset_eval:
#     for id in cat['sound_ids']:
#         durations_eval.append(data_duration[str(id)]['duration'])
#
# fig_title = 'all clips from EVAL set before filtering: ' + str(len(durations_eval))
# plot_histogram(durations_eval,bins1,fig_title)
# plot_histogram(durations_eval,bins10,fig_title)

# -- histogram of clip durations for all clips of EVALUATION set after filtering----
durations_eval_filter = list()

for cat in dataset_eval_filter:
    for id in cat['sound_ids']:
        durations_eval_filter.append(data_duration[str(id)]['duration'])

fig_title = 'all clips from EVAL set after filtering: ' + str(len(durations_eval_filter))
plot_histogram(durations_eval_filter,bins1,fig_title,axes1)
plot_histogram(durations_eval_filter,bins10,fig_title,axes10)












# -- histogram of clip durations for all clips validated as PP
#TOO LONG
# NOTE: considering only one vote in each sound. this is not correct, as around 2% of sounds have multiple (2) labels.
# In those cases, I only consider the first vote that is found. Since this is 2%, for preliminary results it is ok
# durations_PP = list()
# start_time = time.time()
# for id in all_ids:
#     # is this sound voted as PP
#     for v in data_votes:
#         if id in v.values():
#             vote = v['value']
#             if vote == 1.0:
#                 # get and append clip duration
#                 durations_PP.append(data_duration[str(id)]['duration'])
#             break
#
# fig_title = 'all initial 9281 clips -- only PP'
# plot_histogram(durations_PP,30,fig_title)
#
#
# elapsed_time = time.time() - start_time
# print(elapsed_time)





durations_PP = list()
# start_time = time.time()

sounds_voted_PP = [v['freesound_sound_id'] for v in data_votes if v['value'] ==1.0]
sounds_voted_PP_counted_only_once = set(sounds_voted_PP)
sounds_voted_PP_more_than_once = set([id for id in sounds_voted_PP if sounds_voted_PP.count(id) > 1])

print 'sounds voted as PP counted only once: ' + str(len(sounds_voted_PP_counted_only_once))
print 'sounds voted as PP more than once: ' + str(len(sounds_voted_PP_more_than_once))
print 'annotations validated as PP: ' + str(len(sounds_voted_PP))
print 'nothing is matching the paper, or between variables...'
print ()

for id in all_ids:
    # is this sound voted as PP
    if id in sounds_voted_PP_counted_only_once:
        # get and append clip duration
        durations_PP.append(data_duration[str(id)]['duration'])


fig_title = 'of all initial 9281 clips -- only PP: ' + str(len(durations_PP))
plot_histogram(durations_PP,bins1,fig_title,axes1)
plot_histogram(durations_PP,bins10,fig_title,axes10)

# elapsed_time2 = time.time() - start_time
# print(elapsed_time2)


#
#
#
# #TOO LONG
# # # -- histogram of clip durations for all clips validated as PNP
# # # NOTE: considering only one vote in each sound. this is not correct, as around 2% of sounds have multiple (2) labels.
# # # # In those cases, I only consider the first vote that is found. Since this is 2%, for preliminary results it is ok
# # durations_PNP = list()
# # start_time = time.time()
# # for id in all_ids:
# #     # is this sound voted as PNP
# #     for v in data_votes:
# #         if id in v.values():
# #             vote = v['value']
# #             if vote == 0.5:
# #                 # get and append clip duration
# #                 durations_PNP.append(data_duration[str(id)]['duration'])
# #             break
# #
# # fig_title = 'all initial 9281 clips -- only PNP'
# # plot_histogram(durations_PNP,30,fig_title)
# #
# #
# # elapsed_time = time.time() - start_time
# # print(elapsed_time)
#
#
durations_PNP = list()
# start_time = time.time()

sounds_voted_PNP = [v['freesound_sound_id'] for v in data_votes if v['value'] ==0.5]

sounds_voted_PNP_counted_only_once = set(sounds_voted_PNP)
sounds_voted_PNP_more_than_once = set([id for id in sounds_voted_PNP if sounds_voted_PNP.count(id) > 1])

print 'sounds voted as PNP counted only once: ' + str(len(sounds_voted_PNP_counted_only_once))
print 'sounds voted as PNP more than once: ' + str(len(sounds_voted_PNP_more_than_once))
print 'annotations validated as PNP: ' + str(len(sounds_voted_PNP))
print 'only '  + str(len(sounds_voted_PNP_counted_only_once)) + ' is matching the paper...'
print ()

for id in all_ids:
    # is this sound voted as PP
    if id in sounds_voted_PNP_counted_only_once:
        # get and append clip duration
        durations_PNP.append(data_duration[str(id)]['duration'])


fig_title = 'of all initial 9281 clips -- only PNP: ' + str(len(durations_PNP))
plot_histogram(durations_PNP,bins1,fig_title,axes1)
plot_histogram(durations_PNP,bins10,fig_title,axes10)

# elapsed_time2 = time.time() - start_time
# print(elapsed_time2)

# NOTE_ PP + PNP are more than original files:
# they must be the number of labels, but how?



# sanity check
print 'sounds voted PP + sounds voted PNP should amount :' + str(len(durations))
print 'sounds voted PP: ' + str(len(durations_PP))
print 'sounds voted PNP: ' + str(len(durations_PNP))
print 'sounds voted PP + sounds voted PNP: ' + str(len(durations_PP + durations_PNP))







""" # ------------------------------box plots
# # ------------------------------box plots
# # ------------------------------box plots
# # ------------------------------box plots"""




# ------------------- boxplot number of examples per category in dev / eval
nb_sounds_per_cat_dev = list()
nb_sounds_per_cat_eval = list()

for cat in dataset_dev_filter:
    nb_sounds_per_cat_dev.append(cat['nb_sounds'])

for cat in dataset_eval_filter:
    nb_sounds_per_cat_eval.append(cat['nb_sounds'])

data = [nb_sounds_per_cat_dev, nb_sounds_per_cat_eval]
x_labels = ['dev', 'eval']
fig_title = 'number of clips in categories of dev and eval set'
y_label = '# of audio clips'
plot_boxplot(data,x_labels,fig_title,y_label)






# ------------------- boxplot durations in PP / PNP
data = [durations_PP, durations_PNP]
x_labels = ['PP', 'PNP']
fig_title = 'clip durations in PP and PNP sets. review input data.'
y_label = 'seconds'
plot_boxplot(data,x_labels,fig_title,y_label)





# DEVELOPMENT SET
# DEVELOPMENT SET
# DEVELOPMENT SET

# -- # box plot of clip durations for every low-level category for DEVELOPMENT set after filtering----
names_all_cats_dev = list()
durations_all_cats_dev = list()

for cat in dataset_dev_filter:
    durations_dev_filter_one_cat = list()
    names_all_cats_dev.append(cat['name'])
    for id in cat['sound_ids']:
        durations_dev_filter_one_cat.append(data_duration[str(id)]['duration'])
    durations_all_cats_dev.append(durations_dev_filter_one_cat)


# sort by ascending order by median
medians_cat=list()
for cat in durations_all_cats_dev:
    medians_cat.append(np.median(cat))

idx_durations_all_cats_dev = np.argsort(medians_cat)

durations_all_cats_dev_sorted = list(durations_all_cats_dev[val] for val in idx_durations_all_cats_dev)
names_all_cats_dev_sorted = list(names_all_cats_dev[val] for val in idx_durations_all_cats_dev)

if SPLITFIGS == True:
    data = durations_all_cats_dev_sorted[0:40]
    x_labels = names_all_cats_dev_sorted[0:40]
    fig_title = 'clip durations for every category DEV set 1/3.'
    y_label = 'seconds'
    plot_boxplot(data,x_labels,fig_title,y_label)

    data = durations_all_cats_dev_sorted[40:80]
    x_labels = names_all_cats_dev_sorted[40:80]
    fig_title = 'clip durations for every category DEV set 2/3.'
    plot_boxplot(data,x_labels,fig_title,y_label)

    data = durations_all_cats_dev_sorted[80::]
    x_labels = names_all_cats_dev_sorted[80::]
    fig_title = 'clip durations for every category DEV set 3/3.'
    plot_boxplot(data,x_labels,fig_title,y_label)

data = durations_all_cats_dev_sorted
x_labels = names_all_cats_dev_sorted
fig_title = 'clip durations for every category DEV set -- all 124 categories.'
plot_boxplot(data,x_labels,fig_title,y_label)




# -- # box plot of clip durations for every high-level category for DEVELOPMENT set after filtering----
names_all_cats_high_level = list()
durations_all_cats_high_level_dev = list()

for key, value in merge_categories.iteritems():
    sound_ids_cat_high_level = list()
    durations_dev_filter_one_cat_high_level = list()

    name_cat_high_level = [cat['name'] for cat in data_onto if cat['id'] == key]
    names_all_cats_high_level.extend(name_cat_high_level)
    for aso_id in value: #review
        # sound_ids = [cat['sound_ids'] for cat in dataset_dev_filter if cat['audioset_id'] == aso_id]
        sound_ids_cat_high_level.extend([cat['sound_ids'] for cat in dataset_dev_filter if cat['audioset_id'] == aso_id])
    # merge into one single list of ids
    sound_ids_cat_high_level_merged = list([item for sublist in sound_ids_cat_high_level for item in sublist])

    for id in sound_ids_cat_high_level_merged:
        durations_dev_filter_one_cat_high_level.append(data_duration[str(id)]['duration'])
    durations_all_cats_high_level_dev.append(durations_dev_filter_one_cat_high_level)



# boxplot ascending order by median
medians_cat=list()
for cat in durations_all_cats_high_level_dev:
    medians_cat.append(np.median(cat))

idx = np.argsort(medians_cat)
durations_all_cats_high_level_dev_sorted = list(durations_all_cats_high_level_dev[val] for val in idx)
names_all_cats_high_level_sorted = list(names_all_cats_high_level[val] for val in idx)


data = durations_all_cats_high_level_dev_sorted
x_labels = names_all_cats_high_level_sorted
fig_title = 'clip durations for every high-level category DEV set -- all 22 categories.'
y_label = 'seconds'
plot_boxplot(data,x_labels,fig_title,y_label)


print 'Number of sounds in DEV set of FSDk-broad: ' + str(recursive_len(durations_all_cats_high_level_dev))
print()






# EVAL SET
# EVAL SET
# EVAL SET

# -- # box plot of clip durations for every low-level category for EVALUATION set after filtering----
names_all_cats_eval = list()
durations_all_cats_eval = list()

for cat in dataset_eval_filter:
    durations_eval_filter_one_cat = list()
    names_all_cats_eval.append(cat['name'])
    for id in cat['sound_ids']:
        durations_eval_filter_one_cat.append(data_duration[str(id)]['duration'])
    durations_all_cats_eval.append(durations_eval_filter_one_cat)


# sort by ascending order by median
medians_cat=list()
for cat in durations_all_cats_eval:
    medians_cat.append(np.median(cat))
idx = np.argsort(medians_cat)
durations_all_cats_eval_sorted = list(durations_all_cats_eval[val] for val in idx)
names_all_cats_eval_sorted = list(names_all_cats_eval[val] for val in idx)


if SPLITFIGS == True:
    data = durations_all_cats_eval_sorted[0:40]
    x_labels = names_all_cats_eval_sorted[0:40]
    fig_title = 'clip durations for every category EVAL set 1/3.'
    y_label = 'seconds'
    plot_boxplot(data,x_labels,fig_title,y_label)

    data = durations_all_cats_eval_sorted[40:80]
    x_labels = names_all_cats_eval_sorted[40:80]
    fig_title = 'clip durations for every category EVAL set 2/3.'
    plot_boxplot(data,x_labels,fig_title,y_label)

    data = durations_all_cats_eval_sorted[80::]
    x_labels = names_all_cats_eval_sorted[80::]
    fig_title = 'clip durations for every category EVAL set 3/3.'
    plot_boxplot(data,x_labels,fig_title,y_label)

data = durations_all_cats_eval_sorted
x_labels = names_all_cats_eval_sorted
fig_title = 'clip durations for every category EVAL set -- all 124 categories.'
plot_boxplot(data,x_labels,fig_title,y_label)





# -- # box plot of clip durations for every high-level category for EVALUATION set after filtering----
names_all_cats_high_level = list()
durations_all_cats_high_level_eval = list()

for key, value in merge_categories.iteritems():
    sound_ids_cat_high_level = list()
    durations_eval_filter_one_cat_high_level = list()

    name_cat_high_level = [cat['name'] for cat in data_onto if cat['id'] == key]
    names_all_cats_high_level.extend(name_cat_high_level)
    for aso_id in value: #review
        # sound_ids = [cat['sound_ids'] for cat in dataset_dev_filter if cat['audioset_id'] == aso_id]
        sound_ids_cat_high_level.extend([cat['sound_ids'] for cat in dataset_eval_filter if cat['audioset_id'] == aso_id])
    # merge into one single list of ids
    sound_ids_cat_high_level_merged = list([item for sublist in sound_ids_cat_high_level for item in sublist])

    for id in sound_ids_cat_high_level_merged:
        durations_eval_filter_one_cat_high_level.append(data_duration[str(id)]['duration'])
    durations_all_cats_high_level_eval.append(durations_eval_filter_one_cat_high_level)



# boxplot ascending order by median
medians_cat=list()
for cat in durations_all_cats_high_level_eval:
    medians_cat.append(np.median(cat))

idx = np.argsort(medians_cat)
durations_all_cats_high_level_eval_sorted = list(durations_all_cats_high_level_eval[val] for val in idx)
names_all_cats_high_level_sorted = list(names_all_cats_high_level[val] for val in idx)


data = durations_all_cats_high_level_eval_sorted
x_labels = names_all_cats_high_level_sorted
fig_title = 'clip durations for every high-level category EVAL set -- all 22 categories.'
y_label = 'seconds'
plot_boxplot(data,x_labels,fig_title,y_label)


print 'Number of sounds in EVAL set of FSDk-broad: ' + str(recursive_len(durations_all_cats_high_level_eval))
print()






""" # ------------------------------BAR plots
# # ------------------------------BAR plots
# # ------------------------------BAR plots
# # ------------------------------BAR plots"""



# DEVELOPMENT SET
# DEVELOPMENT SET
# DEVELOPMENT SET

# -- # bar plot of number of PP/PNP for every low-level category for DEVELOPMENT set after filtering----
nb_PP_per_cat_dev = list()
nb_PNP_per_cat_dev = list()
names_all_cats_dev = list()

for cat in dataset_dev_filter:
    names_all_cats_dev.append(cat['name'])
    nb_PP_per_cat_dev.append(cat['nb_PP'])
    nb_PNP_per_cat_dev.append(cat['nb_PNP'])


data_bottom = nb_PP_per_cat_dev
data_up = nb_PNP_per_cat_dev
x_labels = names_all_cats_dev
y_label = 'votes ie sounds'
fig_title = 'number of sounds (votes) per category in DEV, split in PP - PNP'
legenda = ('PP', 'PNP')

# plot_barplot(data_bottom,data_up,x_labels,y_label,fig_title,legenda)






# # ---------sort by number of votes (relates to PP)
# add 2 lists element wise
nb_votes_per_cat_dev = [sum(x) for x in zip(nb_PP_per_cat_dev, nb_PNP_per_cat_dev)]
# sort by ascending order of number of votes (ALL together)
idx = np.argsort(nb_votes_per_cat_dev)

names_all_cats_dev_sorted = list(names_all_cats_dev[val] for val in idx)
nb_PP_per_cat_dev_sorted = list(nb_PP_per_cat_dev[val] for val in idx)
nb_PNP_per_cat_dev_sorted = list(nb_PNP_per_cat_dev[val] for val in idx)


data_bottom = nb_PP_per_cat_dev_sorted
data_up = nb_PNP_per_cat_dev_sorted
x_labels = names_all_cats_dev_sorted
y_label = 'votes ie sounds'
fig_title = 'number of sounds (votes) per category in DEV, split in PP and PNP, sorted'
legenda = ('PP', 'PNP')

plot_barplot(data_bottom,data_up,x_labels,y_label,fig_title,legenda)





# # ---------sort by number of PNP votes only
idx = np.argsort(nb_PNP_per_cat_dev)

names_all_cats_dev_sorted = list(names_all_cats_dev[val] for val in idx)
nb_PP_per_cat_dev_sorted = list(nb_PP_per_cat_dev[val] for val in idx)
nb_PNP_per_cat_dev_sorted = list(nb_PNP_per_cat_dev[val] for val in idx)


data_bottom = nb_PNP_per_cat_dev_sorted
data_up = nb_PP_per_cat_dev_sorted
x_labels = names_all_cats_dev_sorted
y_label = 'votes ie sounds'
fig_title = 'number of sounds (votes) per category in DEV, split in PP and PNP, sorted by number of PNP'
legenda = ('PNP', 'PP')

plot_barplot(data_bottom,data_up,x_labels,y_label,fig_title,legenda)





# for easier comparison, it would be nice to have a boxplot of durations per category AND a bar plot of votes with the same category order
# this enables for further comparison
if SLAVE_BOXPLOT_DURATIONS == True:
    # sort by the same order as before
    names_all_cats_dev_sorted = list(names_all_cats_dev[val] for val in idx_durations_all_cats_dev)
    nb_PP_per_cat_dev_sorted = list(nb_PP_per_cat_dev[val] for val in idx_durations_all_cats_dev)
    nb_PNP_per_cat_dev_sorted = list(nb_PNP_per_cat_dev[val] for val in idx_durations_all_cats_dev)

    data_bottom = nb_PP_per_cat_dev_sorted
    data_up = nb_PNP_per_cat_dev_sorted
    x_labels = names_all_cats_dev_sorted
    y_label = 'votes ie sounds'
    fig_title = 'number of sounds (votes) per category in DEV, split in PP/PNP, sorted by median of clip durations (previous boxplot)'
    legenda = ('PP', 'PNP')

    plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)



# to do
# --same with 22 high-level categories
# -- same for EVAL




a=9



