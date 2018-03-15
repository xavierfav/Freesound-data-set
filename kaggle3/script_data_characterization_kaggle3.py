
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

FOLDER_DATA = ''


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

#
#
try:
    # load json with ontology, to map aso_ids to understandable category names
    with open(FOLDER_DATA + 'json/ontology.json') as data_file:
        data_onto = json.load(data_file)
except:
    raise Exception('ADD AN ONTOLOGY JSON FILE TO THE FOLDER ' + FOLDER_DATA + 'json/')
# data_onto is a list of dictionaries
# to retrieve them by id: for every dict o, we create another dict where key = o['id'] and value is o
data_onto_by_id = {o['id']: o for o in data_onto}

#
#
# all_ids of the sounds that compose the dataset
with open(FOLDER_DATA + 'all_freesound_ids.json') as data_file:
    all_ids = json.load(data_file)

# all_ids of the sounds that compose the DEVELOPMENT dataset
with open(FOLDER_DATA + 'json/data_dev.json') as data_file:
    data_dev = json.load(data_file)

# all_ids of the sounds that compose the EVALUATION dataset
with open(FOLDER_DATA + 'json/data_eval.json') as data_file:
    data_eval = json.load(data_file)

# filename = 'dataset_eval.csv'
# raw_data = open(filename, 'rt')
# data_eval = np.loadtxt(raw_data, delimiter=",")
# print(data_eval.shape)

# ===============================================================================================
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
axes1 = [0, 30, 0, 1900]
bins10 = [0, 10, 20, 30]
axes10 = [0, 30, 0, 9000]


def recursive_len(item):
    if type(item) == list:
        return sum(recursive_len(subitem) for subitem in item)
    else:
        return 1
# --------------------------------------end functions for plotting---------------------------------
# --------------------------------------end functions for plotting---------------------------------
# --------------------------------------end functions for plotting---------------------------------


# ==================================HISTOGRAM OF CLIP DURATIONS=========================================================
# ======================================================================================================================

# # --histogram of clip durations for all clips of the dataset
durations = [data_duration[str(id)]['duration'] for id in all_ids]
fig_title = 'all clips in dataset: ' + str(len(durations))
plot_histogram(durations, bins1, fig_title, axes1)
plot_histogram(durations, bins10, fig_title, axes10)

# -- histogram of clip durations for all clips of DEVELOPMENT set----
durations_dev = []
for cat_id, sounds in data_dev.iteritems():
    durations_dev.extend([data_duration[str(fs_id)]['duration'] for fs_id in sounds])

fig_title = 'all clips from DEV set: ' + str(len(durations_dev))
plot_histogram(durations_dev, bins1, fig_title, axes1)
plot_histogram(durations_dev, bins10, fig_title, axes10)

# -- histogram of clip durations for all clips of EVALUATION set----
durations_eval = []
for cat_id, sounds in data_eval.iteritems():
    durations_eval.extend([data_duration[str(fs_id)]['duration'] for fs_id in sounds])

fig_title = 'all clips from EVAL set: ' + str(len(durations_eval))
plot_histogram(durations_eval, bins1, fig_title, axes1)
plot_histogram(durations_eval, bins10, fig_title, axes10)



# ==================================BOX PLOTS=========================================================
# ======================================================================================================================


# ------------------- boxplot number of examples per category in dev / eval
nb_sounds_per_cat_dev = [len(sounds) for cat_id, sounds in data_dev.iteritems()]
nb_sounds_per_cat_eval = [len(sounds) for cat_id, sounds in data_eval.iteritems()]
data_plot = [nb_sounds_per_cat_dev, nb_sounds_per_cat_eval]
x_labels = ['dev', 'eval']
fig_title = 'number of audio samples in categories of dev and eval set'
y_label = '# of audio samples'
plot_boxplot(data_plot, x_labels, fig_title, y_label)


# DEVELOPMENT SET
# DEVELOPMENT SET
# DEVELOPMENT SET

# -- # box plot of clip durations for every category for DEVELOPMENT set ----
names_all_cats_dev = []
durations_all_cats_dev = []

for cat_id, sounds in data_dev.iteritems():
    names_all_cats_dev.append(data_onto_by_id[cat_id]['name'])
    durations_dev_one_cat = [data_duration[str(fs_id)]['duration'] for fs_id in sounds]
    durations_all_cats_dev.append(durations_dev_one_cat)

# sort by ascending order by median
medians_cat = [np.median(cat) for cat in durations_all_cats_dev]
idx_durations_all_cats_dev = np.argsort(medians_cat)
durations_all_cats_dev_sorted = list(durations_all_cats_dev[val] for val in idx_durations_all_cats_dev)
names_all_cats_dev_sorted = list(names_all_cats_dev[val] for val in idx_durations_all_cats_dev)

fig_title = 'clip durations for every category DEV set -- all 41 categories.'
plot_boxplot(durations_all_cats_dev_sorted,
             names_all_cats_dev_sorted,
             fig_title,
             y_label)



# EVAL SET
# EVAL SET
# EVAL SET

# -- # box plot of clip durations for every low-level category for EVALUATION set after filtering----
names_all_cats_eval =  []
durations_all_cats_eval =  []

for cat_id, sounds in data_eval.iteritems():
    names_all_cats_eval.append(data_onto_by_id[cat_id]['name'])
    durations_dev_one_cat = [data_duration[str(fs_id)]['duration'] for fs_id in sounds]
    durations_all_cats_eval.append(durations_dev_one_cat)

# sort by ascending order by median
medians_cat = [np.median(cat) for cat in durations_all_cats_eval]
idx_durations_all_cats_eval = np.argsort(medians_cat)
durations_all_cats_eval_sorted = list(durations_all_cats_eval[val] for val in idx_durations_all_cats_eval)
names_all_cats_eval_sorted = list(names_all_cats_eval[val] for val in idx_durations_all_cats_eval)

fig_title = 'clip durations for every category EVAL set -- all 41 categories.'
plot_boxplot(durations_all_cats_eval_sorted,
             names_all_cats_eval_sorted,
             fig_title,
             y_label)

a=9



""" # ------------------------------BAR plots
# # ------------------------------BAR plots
# # ------------------------------BAR plots
# # ------------------------------BAR plots"""
# esto es lo mas interesante y basic para poner


