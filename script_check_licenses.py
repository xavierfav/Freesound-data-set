import csv
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

# from script_data_characterization import plot_barplot

FOLDER_DATA = 'kaggle3/'
OMIT_LICENSES = 'NC'
# OMIT_LICENSES = 'NC_sampling+'

#### DEFINE CONSTRAIN HERE ###
MIN_HQdev_LQ = 90  # minimum number of sounds between HQ and LQ labels per category


# this the result of the mapping from FS sounds to ASO.
# 268k sounds with basic metadata and their corresponding ASO id.
# useful to get the duration of every sound, and also de license
try:
    with open(FOLDER_DATA + 'json/FS_sounds_ASO_postIQA.json') as data_file:
        data_mapping = json.load(data_file)
except:
    raise Exception('CHOOSE A MAPPING FILE AND ADD IT TO ' + FOLDER_DATA +'json/ FOLDER (THE FILE INCLUDE DURATION INFORMATION NEEDED)')

try:
    # load json with ontology, to map aso_ids to understandable category names
    with open(FOLDER_DATA + 'json/ontology.json') as data_file:
        data_onto = json.load(data_file)
except:
    raise Exception('ADD AN ONTOLOGY JSON FILE TO THE FOLDER ' + FOLDER_DATA + 'json/')

# data_onto is a list of dictionaries
# to retrieve them by id: for every dict o, we create another dict where key = o['id'] and value is o
data_onto_by_id = {o['id']: o for o in data_onto}

def load_csv(csvfile):
    # docstring
    dataset = {}
    # dataset_dev.csv contains fs_id, aso_id, aso_name, aso_id_broad, aso_name_broad, flagHQ_LQ
    with open(csvfile) as csvDataFile:
        dataset_csv = csv.reader(csvDataFile)
        for row in dataset_csv:
            # print(row)
            if row[1] not in dataset:
                dataset[row[1]] = [int(row[0])]
            else:
                dataset[row[1]].append(int(row[0]))
    return dataset


def plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda, axes_up, threshold):
    ind = np.arange(len(data_bottom))  # the x locations for the groups
    width = 0.5  # the width of the bars: can also be len(x) sequence
    axes = [-0.5, len(data_bottom), 0, axes_up]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    p1 = plt.bar(ind, data_bottom, width, color='b')
    p2 = plt.bar(ind, data_up, width, bottom=data_bottom, color='r')
    # horizontal line indicating the threshold
    plt.plot([0, 48], [threshold, threshold], "k--", linewidth=3)
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


def plot_barplot3(data_bottom, data_mid, data_up, x_labels, y_label, fig_title, legenda, axes_up, threshold):
    ind = np.arange(len(data_bottom))  # the x locations for the groups
    width = 0.5  # the width of the bars: can also be len(x) sequence
    axes = [-0.5, len(data_bottom), 0, axes_up]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    p1 = plt.bar(ind, data_bottom, width)
    p2 = plt.bar(ind, data_mid, width, bottom=data_bottom, color='y')
    p3 = plt.bar(ind, data_up, width, bottom=[sum(x) for x in zip(data_bottom, data_mid)], color='r')
    # horizontal line indicating the threshold
    plt.plot([0, 48], [threshold, threshold], "k--", linewidth=3)
    plt.xticks(fontsize=8, rotation=45)
    plt.xticks(ind, x_labels)
    plt.ylabel(y_label)
    plt.title(fig_title)
    # plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0], p3[0]), legenda)
    plt.axis(axes)
    ax.yaxis.grid(True)
    # plt.grid(True)
    plt.show()

# =============================================================
# =============================================================

dataset_dev = load_csv(FOLDER_DATA + 'dataset_dev.csv')
# we have loaded the DEV part (no distinction between HQdev and LQ)
# sanity check
if len(dataset_dev) != 48:
    sys.exit('something wrong in reading categories')
elif sum([len(sounds) for catid, sounds in dataset_dev.iteritems()]) != 10590:
    sys.exit('something wrong in reading audio samples')

dataset_eval = load_csv(FOLDER_DATA + 'dataset_eval.csv')
# we have loaded the DEV part (no distinction between HQdev and LQ)
# sanity check
if len(dataset_eval) != 48:
    sys.exit('something wrong in reading categories')
elif sum([len(sounds) for catid, sounds in dataset_eval.iteritems()]) != 1389:
    sys.exit('something wrong in reading audio samples')


# we have both DEV AND EVAL
# dict of dicts
# every dict is key the catid and a list of fsids

# 1) barplot for DEV with MIN_HQdev_LQ
data_bottom = [len(sounds) for catid, sounds in dataset_dev.iteritems()]
data_up = [0 for catid, sounds in dataset_dev.iteritems()]
x_labels = [data_onto_by_id[catid]['name'] for catid, sounds in dataset_dev.iteritems()]
y_label = 'nb sounds'
fig_title = 'number of sounds (votes) per category in DEV'
legenda = ('-', '--')
plot_barplot(data_bottom,data_up,x_labels,y_label,fig_title,legenda,150, MIN_HQdev_LQ)


# barplot for EVAL with MIN_HQeval
data_bottom = [len(sounds) for catid, sounds in dataset_eval.iteritems()]
data_up = [0 for catid, sounds in dataset_dev.iteritems()]
x_labels = [data_onto_by_id[catid]['name'] for catid, sounds in dataset_eval.iteritems()]
y_label = 'nb sounds'
fig_title = 'number of sounds (votes) per category in EVAL'
legenda = ('-', '--')
plot_barplot(data_bottom,data_up,x_labels,y_label,fig_title,legenda, 50, 12)





# 2) repeat barplots with colorbar markingthe sounds with license BY-NC
# we will see then 2 of the 3 thresholds
list_cats_license_NC = []
list_cats_license_SPLUS = []

# highlight only NC
if OMIT_LICENSES == 'NC':

    for catid, sounds in dataset_dev.iteritems():
        count_NC = 0

        for sound in sounds:
            print data_mapping[str(sound)]['license'].split('/')[-3]
            if data_mapping[str(sound)]['license'].split('/')[-3] == 'by-nc':
                count_NC += 1

        list_cats_license_NC.append(count_NC)

    data_bottom = [len(sounds) for catid, sounds in dataset_dev.iteritems()]
    for idx in range(len(data_bottom)):
        data_bottom[idx] = data_bottom[idx] - list_cats_license_NC[idx]

    data_up = list_cats_license_NC
    x_labels = [data_onto_by_id[catid]['name'] for catid, sounds in dataset_dev.iteritems()]
    y_label = 'nb sounds with a license'
    fig_title = 'number of sounds (votes) per category in DEV'
    legenda = ('ok', 'NC')
    plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda, 150, MIN_HQdev_LQ)

    # EVAL
    list_cats_license_NC = []
    list_cats_license_SPLUS = []
    for catid, sounds in dataset_eval.iteritems():
        count_NC = 0

        for sound in sounds:
            print data_mapping[str(sound)]['license'].split('/')[-3]
            if data_mapping[str(sound)]['license'].split('/')[-3] == 'by-nc':
                count_NC += 1

        list_cats_license_NC.append(count_NC)

    data_bottom = [len(sounds) for catid, sounds in dataset_eval.iteritems()]
    for idx in range(len(data_bottom)):
        data_bottom[idx] = data_bottom[idx] - list_cats_license_NC[idx]

    data_up = list_cats_license_NC
    x_labels = [data_onto_by_id[catid]['name'] for catid, sounds in dataset_eval.iteritems()]
    y_label = 'nb sounds with a license'
    fig_title = 'number of sounds (votes) per category in EVAL'
    legenda = ('ok', 'NC')
    plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda, 50, 12)

# highlight both NC and sampling+
elif OMIT_LICENSES == 'NC_sampling+':

    for catid, sounds in dataset_dev.iteritems():
        count_NC = 0
        count_SPLUS = 0

        for sound in sounds:
            print data_mapping[str(sound)]['license'].split('/')[-3]
            if data_mapping[str(sound)]['license'].split('/')[-3] == 'by-nc':
                count_NC += 1
            elif data_mapping[str(sound)]['license'].split('/')[-3] == 'sampling+':
                count_SPLUS += 1

        list_cats_license_NC.append(count_NC)
        list_cats_license_SPLUS.append(count_SPLUS)

    data_bottom = [len(sounds) for catid, sounds in dataset_dev.iteritems()]

    for idx in range(len(data_bottom)):
        data_bottom[idx] = data_bottom[idx] - list_cats_license_NC[idx] - list_cats_license_SPLUS[idx]

    data_mid = list_cats_license_NC
    data_up = list_cats_license_SPLUS
    x_labels = [data_onto_by_id[catid]['name'] for catid, sounds in dataset_dev.iteritems()]
    y_label = 'nb sounds with a license'
    fig_title = 'number of sounds (votes) per category in DEV'
    legenda = ('ok', 'NC', 'sampling+')
    plot_barplot3(data_bottom,data_mid,data_up,x_labels,y_label,fig_title,legenda,150, MIN_HQdev_LQ)



    # EVAL
    list_cats_license_NC = []
    list_cats_license_SPLUS = []
    for catid, sounds in dataset_eval.iteritems():
        count_NC = 0
        count_SPLUS = 0

        for sound in sounds:
            print data_mapping[str(sound)]['license'].split('/')[-3]
            if data_mapping[str(sound)]['license'].split('/')[-3] == 'by-nc':
                count_NC += 1
            elif data_mapping[str(sound)]['license'].split('/')[-3] == 'sampling+':
                count_SPLUS += 1

        list_cats_license_NC.append(count_NC)
        list_cats_license_SPLUS.append(count_SPLUS)


    data_bottom = [len(sounds) for catid, sounds in dataset_eval.iteritems()]
    for idx in range(len(data_bottom)):
        data_bottom[idx] = data_bottom[idx] - list_cats_license_NC[idx] - list_cats_license_SPLUS[idx]

    data_mid = list_cats_license_NC
    data_up = list_cats_license_SPLUS
    x_labels = [data_onto_by_id[catid]['name'] for catid, sounds in dataset_eval.iteritems()]
    y_label = 'nb sounds with a license'
    fig_title = 'number of sounds (votes) per category in EVAL'
    legenda = ('ok', 'NC', 'sampling+')
    plot_barplot3(data_bottom,data_mid,data_up,x_labels,y_label,fig_title,legenda,50, 12)





# but in the plots above you cannot see how many sounds correspond to HQ or LQ,
# and there is an important constraint: MIN_HQdev
# 3) repeat 1 and 2 with the 3rd threshold: MIN_HQdev

a=9